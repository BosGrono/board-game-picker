import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Read the sheet
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    # --- Exact Column Mapping based on your sheet ---
    game_col = 'Game'
    chip_col = 'Chips'
    bgg_col = 'BGG_ID'
    plays_col = 'Recorded Plays'
    rating_col = 'Avg_Rating'
    cat_col = 'Cataloguing'
    wtp_col = 'WTP_Count'

    # 2. Build the Four Bags
    bags = {
        "Primary": [],
        "Archive": [],
        "Greatest Hits": [],
        "Want To Play": []
    }

    for index, row in df.iterrows():
        name = str(row[game_col])
        
        # Safe numeric conversion for Chips
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
        except:
            chips = 1
            
        # Safe numeric conversion for WTP_Count
        try:
            wtp_val = row[wtp_col]
            wtp_chips = int(float(wtp_val)) if pd.notnull(wtp_val) else 0
        except:
            wtp_chips = 0
            
        catalog = str(row[cat_col]).strip()

        # Add to Catalogue-based bags
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        
        # Add to Want To Play bag independently
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # 3. User Interface
    st.sidebar.header("Selection Settings")
    mode = st.sidebar.radio(
        "Selection Mode",
        ["Roll the D20", "Primary Only", "Want To Play Only", "Archive Only", "Greatest Hits Only"]
    )

    st.write(f"Found **{len(df)}** games with **{len(bags['Primary']) + len(bags['Archive']) + len(bags['Greatest Hits'])}** total chips.")
    
    if st.button("🎰 Draw a Game!"):
        selected_bag_name = ""
        
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(1)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 Rolled a **{die_roll}**! Drawing from the **{selected_bag_name}** bag.")
        else:
            selected_bag_name = mode.replace(" Only", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging through the bag...'):
                time.sleep(2)
                winner = random.choice(active_bag)
                st.balloons()
                st.header(f"Game selected: **{winner}**!")
                
                # --- Metadata Display (with extra error protection) ---
                winner_data = df[df[game_col] == winner].iloc[0]
                
                try:
                    # Probability
                    current_chips = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                    w_chips = int(float(current_chips)) if pd.notnull(current_chips) else 1
                    prob = (w_chips / len(active_bag)) * 100
                    st.caption(f"Probability of selection: {prob:.2f}% ({w_chips} / {len(active_bag)} chips)")

                    # Previous Plays (Safe conversion)
                    plays_val = winner_data[plays_col]
                    if pd.notnull(plays_val):
                        try:
                            plays_num = int(float(plays_val))
                            if plays_num > 0:
                                st.caption(f"Previous plays: {plays_num}")
                                
