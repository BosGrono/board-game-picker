import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night", page_icon="🎲")

# --- SETTINGS ---
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
# We add a random number to the end of the URL to force Google to give us fresh data
import datetime
cache_buster = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0&cb={cache_buster}'

st.title("🎲 The Board Game Draw Bag")

# Use a very short cache time so updates show up quickly
@st.cache_data(ttl=5)
def get_data(url):
    # We use 'on_bad_lines' to prevent crashing if the sheet has messy rows
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = get_data(SHEET_URL)
    df.columns = df.columns.str.strip() # Remove any hidden spaces

    # Let's be very explicit about finding the right columns
    # We will look for names, but fall back to positions if names fail
    game_col = 'Game' if 'Game' in df.columns else df.columns[0]
    chip_col = 'Chips' if 'Chips' in df.columns else df.columns[2]

    # Generate the "Virtual Bag"
    virtual_bag = []
    for _, row in df.iterrows():
        try:
            name = str(row[game_col])
            count = int(float(row[chip_col]))
            virtual_bag.extend([name] * count)
        except:
            continue

    # --- UI LAYOUT ---
    st.sidebar.metric("Games Found", len(df))
    st.sidebar.metric("Total Chips", len(virtual_bag))

    if st.button("🎰 DRAW A GAME", use_container_width=True):
        if virtual_bag:
            with st.spinner('Spinning the wheel...'):
                time.sleep(1)
                winner = random.choice(virtual_bag)
                st.balloons()
                st.success(f"### The winner is: {winner}")
        else:
            st.warning("Bag is empty. Check your 'Chips' column!")

    # This will show you EXACTLY what the app is reading
    st.write("---")
    st.subheader("Data Preview")
    st.write("If the list below is wrong, the Sheet ID might be pointing to an old file.")
    st.dataframe(df, hide_index=True)

except Exception as e:
    st.error(f"Error: {e}")
