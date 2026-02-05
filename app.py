import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Read and Clean
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    # Column Mapping
    game_col = 'Game'
    chip_col = 'Chips'
    bgg_col = 'BGG_ID'
    plays_col = 'Recorded Plays'
    rating_col = 'Avg_Rating'
    cat_col = 'Cataloguing'
    wtp_col = 'WTP_Count'
    wtp_tag_col = 'WTP Tag' 

    # --- EFFICIENCY CLEANUP ---
    df = df[df[game_col].fillna('').str.strip() != ''].copy()
    df.index = range(1, len(df) + 1)

    # 2. Build the Four Bags
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
        except: chips = 1
        try:
            wtp_chips = int(float(row[wtp_col])) if pd.notnull(row[wtp_col]) else 0
        except: wtp_chips = 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # --- 3. D20 CONFIGURATION (Hidden in Expander Logic) ---
    # We define these before the Draw Logic so the Button can see the values
    with st.expander("🎲 D20 Face Distribution & Settings"):
        st.write("Adjust how many faces of the D20 belong to each bag:")
        
        col1, col2, col3, col4 = st.columns(4)
        f_primary = col1.number_input("Primary", 0, 20, 10)
        f_wtp = col2.number_input("WTP", 0, 20, 6)
        f_archive = col3.number_input("Archive", 0, 20, 2)
        f_gh = col4.number_input("G. Hits", 0, 20, 2)

        total_faces = f_primary + f_wtp + f_archive + f_gh
        
        if total_faces != 20:
            st.warning(f"⚠️ Total faces = {total_faces}. For a true D20, this should equal 20!")
        
        st.write("Visual Odds Map: " + "🟦"*f_primary + "🟧"*f_wtp + "🟥"*f_archive + "🟩"*f_gh)

    # 4. USER AGENCY: Selection Method
    st.subheader("Selection Method")
    mode = st.radio(
        "Choose how you want to pick a game:",
        ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"],
        horizontal=True
    )

    st.write("---")

    # 5. Drawing Logic
    if st.button("🎰 Draw a Game!", use_container_width=True):
        selected_bag_name = ""
        
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(1)
                die_roll = random.randint(1, total_faces if total_faces > 0 else 20)
                
                # Logic using the dynamic inputs
                if die_roll <= f_primary: 
                    selected_bag_name = "Primary"
                elif die_roll <= (f_primary + f_wtp): 
                    selected_bag_name = "Want To Play"
                elif die_roll <= (f_primary + f_wtp + f_archive): 
                    selected_bag_name = "Archive"
                else: 
                    selected_bag_name = "Greatest Hits"
                
                st.info(f"🎲 **D20 Result: {die_roll}** → Drawing from the **{selected_bag_name}** bag.")
        else:
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging...'):
                time.sleep(1.5)
                winner = random.choice(active_bag)
                st.balloons()
                st.header(f"Game selected: **{winner}**!")
                
                winner_data = df[df[game_col] == winner].iloc[0]
                try:
                    if selected_bag_name == "Want To Play":
                        wtp_tags = winner_data[wtp_tag_col]
                        if pd.notnull(wtp_tags):
                            st.subheader(f"♟️ Want to play tag: {wtp_tags}")
                    
                    current_val = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                    w_chips = int(float(current_val)) if pd.notnull(current_val) else 1
                    prob = (w_chips / len(active_bag)) * 100
                    st.caption(f"Probability: {prob:.2f}% ({w_chips} / {len(active_bag)} chips)")

                    rating = winner_data[rating_col]
                    if pd.notnull(rating): st.caption(f"Average Rating: {rating}")

                    bgg_id = winner_data[bgg_col]
                    if pd.notnull(bgg_id):
                        bgg_url = f"https://boardgamegeek.com/boardgame/{int(float(bgg_id))}"
                        st.markdown(f"<h6>🔗 <a href='{bgg_url}'>View on BoardGameGeek</a></h6>", unsafe_allow_html=True)
                except Exception:
                    st.caption("Metadata display issue.")
        else:
            st.warning(f"The {selected_bag_name} bag is empty!")

    # --- BOTTOM SECTION ---
    st.write("---")

    with st.expander("🏆 Greatest Hits"):
        gh_df = df[df[cat_col].str.strip() == "Greatest Hits"].copy()
        gh_df[rating_col] = pd.to_numeric(gh_df[rating_col], errors='coerce')
        gh_ranked = gh_df.sort_values(by=rating_col, ascending=False)
        if not gh_ranked.empty:
            display_df = gh_ranked[[game_col, rating_col, plays_col]].reset_index(drop=True)
            display_df.index += 1 
            st.table(display_df.style.format({rating_col: "{:.1f}"}))

    with st.expander("🔥 Want To Play"):
        wtp_display_df = df[pd.to_numeric(df[wtp_col], errors='coerce') >= 1].copy()
        wtp_display_df[rating_col] = pd.to_numeric(wtp_display_df[rating_col], errors='coerce')
        wtp_ranked = wtp_display_df.sort_values(by=wtp_col, ascending=False)
        if not wtp_ranked.empty:
            display_wtp = wtp_ranked[[game_col, wtp_col, wtp_tag_col, rating_col]].reset_index(drop=True)
            display_wtp.index += 1
            st.table(display_wtp.style.format({rating_col: "{:.1f}", wtp_col: "{:.0f}"}))
    
    with st.expander("📒 View Full Library"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Connection Error")
    st.info(f"Technical details: {e}")
