import streamlit as st
import pandas as pd
import random
import time

# 1. Page Config
st.set_page_config(page_title="Game Night Picker", page_icon="🎲", layout="wide")

# --- YOUR CUSTOM SETTINGS ---
# Hardcoded your Sheet ID as requested
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8' 

# IMPORTANT: If it's still pulling the wrong tab, change '0' to the gid 
# number found at the end of your browser URL.
TAB_GID = '0' 

SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={TAB_GID}'

# 2. Data Loading
@st.cache_data(ttl=60)
def load_data(url):
    data = pd.read_csv(url)
    data.columns = data.columns.str.strip()
    return data

# 3. App Logic
try:
    df = load_data(SHEET_URL)
    
    # Mapping your columns: A=Game, B=Date, C=Chips
    game_col = df.columns[0]
    chip_col = df.columns[2]

    # Build the Virtual Bag
    virtual_bag = []
    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            # We use float then int to handle cases where chips might be 1.0
            count = int(float(row[chip_col]))
        except:
            count = 1
        virtual_bag.extend([name] * count)

    # --- SIDEBAR ---
    st.sidebar.header("📊 Library Stats")
    st.sidebar.metric("Total Games", len(df))
    st.sidebar.metric("Total Chips", len(virtual_bag))
    
    if not df.empty:
        most_chips = df[chip_col].max()
        # Find the game(s) with the highest weight
        top_games = df[df[chip_col] == most_chips][game_col].tolist()
        st.sidebar.info(f"🔥 **Highest Odds:** {top_games[0]}")

    # --- MAIN UI ---
    st.title("🎲 The Board Game Draw Bag")
    st.write("Making game night decisions easier (and slightly more dramatic).")
    
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🎰 DRAW A GAME", use_container_width=True):
            if virtual_bag:
                with st.spinner('Consulting the dice gods...'):
                    time.sleep(2)
                    winner = random.choice(virtual_bag)
                    st.balloons()
                    st.success("## THE CHOSEN ONE IS:")
                    st.header(f"✨ {winner} ✨")
            else:
                st.error("The bag is empty! Please check Column C in your sheet.")

    with col2:
        with st.expander("View Full Library & Weights"):
            # Show only the Game and Chips columns for a cleaner look
            st.dataframe(df[[game_col, chip_col]], hide_index=True, use_container_width=True)

except Exception as e:
    st.error("Connection Error!")
    st.write("I found the spreadsheet, but I can't read the columns correctly.")
    st.info(f"Technical error: {e}")
