import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# --- Google Sheet Connection ---
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Fetch Data
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()

    # Column Mapping
    game_col, chip_col, cat_col = 'Game', 'Chips', 'Cataloguing'
    wtp_col, plays_col, rating_col, bgg_col = 'WTP_Count', 'Recorded Plays', 'Avg_Rating', 'BGG_ID'

    # 2. Build the Bags
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
            wtp_chips = int(float(row[wtp_col])) if pd.notnull(row[wtp_col]) else 0
        except:
            chips, wtp_chips = 1, 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # 3. UI
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
                time.sleep(0.5)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 **D20 Result: {die_roll}** → Drawing from **{selected_bag_name}**.")
        else:
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging...'):
                time.sleep(1)
                winner = random.choice(active_bag)
                st.balloons()
                
                st.header(f"Winner: {winner}!")
                
                winner_data = df[df[game_col] == winner].iloc[0]
                
                # Probability Math
                c_
