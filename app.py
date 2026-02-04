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
    df.columns = df.columns.str.strip()  # Clean whitespace from headers

    # Column Mapping (matches your sheet headers)
    game_col = 'Game'
    chip_col = 'Chips'
    cat_col = 'Cataloguing'
    wtp_col = 'WTP_Count'
    plays_col = 'Recorded Plays'
    rating_col = 'Avg_Rating'
    bgg_col = 'BGG_ID'

    # 2. Build the Bags
    # We populate lists where a game appears once per "chip" it has
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        
        # Determine Chip Counts
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
            wtp_chips = int(float(row[wtp_col])) if pd.notnull(row[wtp_col]) else 0
        except:
            chips, wtp_chips = 1, 0
            
        # Assign to Catalogue Bag
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        
        # Assign to "Want To Play" Bag if it has WTP chips
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
                # D20 Odds: 1-10 Primary, 11-16 WTP, 17-18 Archive, 19-20 Greatest Hits
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                
                st.info(f"🎲 **D20 Result: {die_roll}** → Drawing from the **{selected_bag_name}** bag.")
        else:
            # Manual Selection
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging through the bag...'):
                time.sleep(1.5)
                winner = random.choice(active_bag)
                st.balloons()
                
                # Display Results
                st.header(f"Game selected: **{winner}**!")
                
                # Metadata retrieval
                winner_data = df[df[game_col] == winner].iloc[0]
                
                # Calculate odds of that specific game being picked from the bag
                current_chips_val = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                w_chips = int(float(current_chips_val)) if pd.notnull(current_chips_val) else 1
                prob = (w_chips / len(active_bag)) * 100
                
                st.write(f"This game had a **{prob:.2f}%** chance of being drawn from the {selected_bag_name} bag.")
                
                # Show additional info if available
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Recorded Plays", int(float(winner_data[plays_col])) if pd.notnull(winner_data[plays_col]) else 0)
                with cols[1]:
                    st.metric("Avg Rating", winner_data[rating_col] if pd.notnull(winner_data[rating_col]) else "N/A")
                with cols[2]:
                    if pd.notnull(winner_data[bgg_col]):
                        bgg_url = f"https://boardgamegeek.com/boardgame/{int(float(winner_data[bgg_col
