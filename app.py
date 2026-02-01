import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# --- TRIPLE CHECK THIS ID ---
# It should look something like: 1A2b3C4d5E6f7G8h9I0j
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8' 

# This is the most reliable "Public" CSV export link
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

@st.cache_data(ttl=600) # This keeps the data for 10 mins so it's fast
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(SHEET_URL)
    df.columns = df.columns.str.strip() # Remove hidden spaces
    
    # Identify columns by position if names are being tricky
    # We assume Column A (index 0) is Game and Column C (index 2) is Chips
    game_col = df.columns[0]
    chip_col = df.columns[2]

    virtual_bag = []
    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            # Convert chips to number, default to 1 if it's not a number
            count = int(float(row[chip_col])) 
        except:
            count = 1
        virtual_bag.extend([name] * count)

    st.success(f"Successfully loaded {len(df)} games!")
    
    if st.button("🎰 Draw a Game!"):
        with st.spinner('Rummaging...'):
            time.sleep(1.5)
            winner = random.choice(virtual_bag)
            st.balloons()
            st.header(f"The winner is: {winner}")

    with st.expander("View Spreadsheet Data"):
        st.write(df)

except Exception as e:
    st.error("Still hitting a wall!")
    st.write(f"**Current URL being used:** {SHEET_URL}")
    st.write(f"**Technical Error:** {e}")
