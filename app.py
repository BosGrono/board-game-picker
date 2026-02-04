import streamlit as st
import pandas as pd
import random
import time
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

# --- ROBUST BGG FETCH WITH RETRIES ---
def get_bgg_image(bgg_id):
    if not bgg_id or pd.isna(bgg_id):
        return None
    
    try:
        clean_id = str(int(float(bgg_id)))
    except:
        return None

    headers = {'User-Agent': 'BoardGamePickerApp/2.0'}
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={clean_id}"
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find("item")
                if item is not None:
                    image_node = item.find("image")
                    if image_node is not None:
                        return image_node.text
                    thumb_node = item.find("thumbnail")
                    if thumb_node is not None:
                        return thumb_node.text
                return None
            elif response.status_code == 202:
                time.sleep(1.5)
                continue
        except:
            continue
    return None

try:
    # 1. Read and Clean
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    game_col = 'Game'
    chip_col = 'Chips'
    bgg_col = 'BGG_ID'
    plays_col = 'Recorded Plays'
    rating_col = 'Avg_Rating'
    cat_col = 'Cataloguing'
    wtp_col = 'WTP_Count'

    # 2. Build the Four Bags
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
            wtp_val = row[wtp_col]
            wtp_chips = int(float(wtp_val)) if pd.notnull(wtp_val) else 0
        except:
            chips, wtp_chips = 1, 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # 3. UI: Selection Method
    st.subheader("Selection Method")
    mode = st.radio(
        "Choose how you want to pick a game:",
        ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"],
        horizontal=True
    )

    st.write("---")

    # 4. Drawing Logic
    if st.button("🎰 Draw a Game!", use_container_width=True):
        selected_bag_name = ""
        
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(1)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 **D20 Result: {die_roll}** → Drawing from the **{selected_bag_name}** bag.")
        else:
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging through the bag...'):
                time.sleep(1.5)
                winner = random.choice(active_bag)
                st.balloons()
                
                winner_data = df[df[game_col] == winner].iloc[0]
                bgg_id = winner_data[bgg_col]
                img_url = get_bgg_image(bgg_id)
                
                col_a, col_b = st.columns([1, 2])
                
                with col_a:
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown("### 🖼️\n*Image unavailable*")
                
                with col_b:
                    st.header(f"Game selected: **{winner}**!")
                    try:
                        current_chips_val = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                        w_chips = int(float(current_chips_val)) if pd.notnull(current_chips_val) else 1
                        prob = (w_chips / len(active_bag)) * 100
                        st.caption(f"Probability: {prob:.2f}% ({w_chips} / {len(active_bag)} chips)")

                        for label, col in [("Previous plays", plays_col), ("Average Rating", rating_col), ("Catalogue Entry", cat_col)]:
                            val = winner_data[col]
                            if pd.notnull(val):
                                st.caption(f"{label}: {val}")

                        if pd.notnull(bgg_id):
                            bgg_url = f"https://boardgamegeek.com/boardgame/{int(float(bgg_id))}"
                            st.markdown(f"<h6>🔗 <a href='{bgg_url}'>View on BoardGameGeek</a></h6>", unsafe_allow_html=True)
                    except:
                        st.caption("Metadata display encountered a minor issue.")
        else:
            st.warning(f"The {selected_bag_name} bag is empty!")

    # Footer Logic
    st.write("---")
    with st.expander("🎲 View D20 Face Distribution"):
        cols = st.columns(4)
        labels = [("Primary", "10 Faces", "1-10"), ("WTP", "6 Faces", "11-16"), ("Archive", "2 Faces", "17-18"), ("G. Hits", "2 Faces", "19-20")]
        for i, (name, faces, rng) in enumerate(labels):
            cols[i].metric(name, faces, rng)
        st.write("Visual Odds Map: " + "🟦"*10 + "🟧"*6 + "🟥"*2 + "🟩"*2)

    with st.expander("View Full Library"):
