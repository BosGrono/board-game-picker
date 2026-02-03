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
        ["Roll the D20", "
