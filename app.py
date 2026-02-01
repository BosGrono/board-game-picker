import streamlit as st
import pandas as pd
import random
import time

# 1. Page Config
st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# 2. Connect to Google Sheets
# Replace the URL below with your actual Google Sheet URL
SHEET_ID = 1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8
SHEET_URL = https://docs.google.com/spreadsheets/d/1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8/edit?gid=963174730#gid=963174730

try:
    # This reads the sheet and turns it into a "DataFrame" (like a mini-table in the app)
    df = pd.read_csv(SHEET_URL)
    
    # 3. The Logic: Creating the Virtual Bag
    virtual_bag = []
    for index, row in df.iterrows():
        # Adds the game name to the bag 'weight' times
        virtual_bag.extend([row['name']] * int(row['weight']))

    # 4. The User Interface
    if st.button("🎰 Draw a Game!"):
        with st.spinner('Rummaging through the bag...'):
            time.sleep(2)
            winner = random.choice(virtual_bag)
            st.balloons()
            st.success(f"The winner is: **{winner}**!")

    # 5. Show the Library
    with st.expander("View Library & Odds"):
        st.dataframe(df) # This displays your sheet data in a nice table

except Exception as e:
    st.error("I couldn't read the Google Sheet. Check the URL and permissions!")
