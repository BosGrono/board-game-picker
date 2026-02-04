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

def get_bgg_image(bgg_id):
    if not bgg_id or pd.isna(bgg_id): return None
    try:
        clean_id = str(int(float(bgg_id)))
        # Switching back to v2 (thing), which is public and shouldn't 401
        url = f"https://boardgamegeek.com/xmlapi2/thing?id={clean_id}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (BoardGamePicker)'}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            # In API v2, image is inside 'item'
            item = root.find("item")
            if item is not None:
                img_node = item.find("image")
                if img_node is not None:
                    img_url = img_node.text
                    # Ensure the URL is absolute
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    return img_url
    except Exception as e:
        pass
    return None

try:
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    # 1. Setup Bags
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}
    for _, row in df.iterrows():
        name = str(row['Game'])
        try:
            c = int(float(row['Chips'])) if pd.notnull(row['Chips']) else 1
            w = int(float(row['WTP_Count'])) if pd.notnull(row['WTP_Count']) else 0
        except: c, w = 1, 0
        cat = str(row['Cataloguing']).strip()
        if cat in bags: bags[cat].extend([name] * c)
        if w >= 1: bags["Want To Play"].extend([name] * w)

    # 2. UI
    st.subheader("Selection Method")
    mode = st.radio("Choose Method:", ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"], horizontal=True)
    
    if st.button("🎰 Draw a Game!", use_container_width=True):
        bag_name = ""
        if mode == "Roll the D20":
            roll = random.randint(1, 20)
            if roll <= 10: bag_name = "Primary"
            elif roll <= 16: bag_name = "Want To Play"
            elif roll <= 18: bag_name = "Archive"
            else: bag_name = "Greatest Hits"
            st.info(f"🎲 Rolled a **{roll}**! Drawing from **{bag_name}**.")
        else:
            bag_name = mode.replace("Pick from ", "")

        active_bag = bags[bag_name]
        if active_bag:
            winner = random.choice(active_bag)
            row_data = df[df['Game'] == winner].iloc[0]
            
            with st.spinner(f"Summoning {winner}..."):
                img_url = get_bgg_image(row_data['BGG_ID'])
            
            st.balloons()
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if img_url: 
                    st.image(img_url, use_container_width=True)
                else: 
                    st.markdown("### 🖼️\n*No Image Found*")
                    if pd.notnull(row_data['BGG_ID']):
                        test_id = int(float(row_data['BGG_ID']))
                        st.caption(f"Debug Info: [Click to test BGG v2 Link](https://boardgamegeek.com/xmlapi2/thing?id={test_id})")
            with c2:
                st.header(winner)
                st.write(f"**Bag:** {bag_name}")
                if pd.notnull(row_data['BGG_ID']):
                    b_id = int(float(row_data['BGG_ID']))
                    st.markdown(f"[View on BGG](https://boardgamegeek.com/boardgame/{b_id})")
        else:
            st.warning("That bag is currently empty!")

    # 3. Footer
    st.divider()
    with st.expander("🎲 View D20 Odds"):
        st.write("1-10: Primary | 11-16: WTP | 17-18: Archive | 19-20: G. Hits")
        st.write("🟦"*10 + "🟧"*6 + "🟥"*2 + "🟩"*2)
    with st.expander("View Library"):
        st.dataframe(df)

except Exception as e:
    st.error(f"App Error: {e}")
