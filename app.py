import streamlit as st
import pandas as pd
import random
import time

# 1. Page Config
st.set_page_config(page_title="Game Night Picker", page_icon="🎲", layout="wide")

# --- USER SETTINGS ---
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8' 
# Find the GID at the end of your browser URL when clicking the correct tab
TAB_GID = '0' 

# The direct export link for a specific tab
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={TAB_GID}'

# 2. Data Loading Function
@st.cache_data(ttl=60) # Refreshes every minute if you update the sheet
def load_data(url):
    data = pd.read_csv(url)
    data.columns = data.columns.str.strip() # Clean column names
    return data

# 3. Main App Logic
try:
    df = load_data(SHEET_URL)
    
    # Identify our columns
    game_col = df.columns[0]  # Column A: Game
    date_col = df.columns[1]  # Column B: Date Entered
    chip_col = df.columns[2]  # Column C: Chips

    # Build the Virtual Bag
    virtual_bag = []
    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            count = int(float(row[chip_col]))
        except:
            count = 1 # Default to 1 chip if column C is empty
        virtual_bag.extend([name] * count)

    # --- SIDEBAR ---
    st.sidebar.header("📊 Library Stats")
    st.sidebar.metric("Total Games", len(df))
    st.sidebar.metric("Total Chips", len(virtual_bag))
    
    # Simple logic to find the game with the most chips
    most_chips = df[chip_col].max()
    lucky_game = df[df[chip_col] == most_chips][game_col].iloc[0]
    st.sidebar.info(f"🔥 **Highest Odds:** {lucky_game}")

    # --- MAIN UI ---
    st.title("🎲 The Board Game Draw Bag")
    st.write("Welcome to the weekly randomizer!")
    
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🎰 DRAW A GAME", use_container_width=True):
            if len(virtual_bag) > 0:
                with st.spinner('Mixing the bag...'):
                    time.sleep(2)
                    winner = random.choice(virtual_bag)
                    st.balloons()
                    st.success("## WE ARE PLAYING...")
                    st.header(f"✨ {winner} ✨")
            else:
                st.error("The bag is empty! Check your spreadsheet.")

    with col2:
        with st.expander("View Library & Odds"):
            st.dataframe(df[[game_col, chip_col]], hide_index=True)

except Exception as e:
    st.error("Wait, we hit a snag!")
    st.info(f"Make sure your SHEET_ID and TAB_GID are correct.")
    st.write(f"Technical error: {e}")
