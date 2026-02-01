import streamlit as st
import pandas as pd
import random
import time

# 1. Page Config
st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# 2. Connect to Google Sheets
SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
# We added &headers=1 to tell it the first row is the title row
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&headers=1'

try:
    # Read the sheet
    df = pd.read_csv(SHEET_URL)
    
    # Let's clean up the data - removing any empty rows if they exist
    df = df.dropna(subset=['Game', 'Chips'])

    # 3. The Logic: Creating the Virtual Bag
    virtual_bag = []
    for index, row in df.iterrows():
        # Using your specific column names: 'Game' and 'Chips'
        name = str(row['Game'])
        count = int(row['Chips'])
        virtual_bag.extend([name] * count)

    # 4. The User Interface
    st.write(f"Currently, there are **{len(virtual_bag)}** total chips in the bag.")
    
    if st.button("🎰 Draw a Game!"):
        if len(virtual_bag) > 0:
            with st.spinner('Rummaging through the bag...'):
                time.sleep(2)
                winner = random.choice(virtual_bag)
                st.balloons()
                st.success(f"The winner is: **{winner}**!")
        else:
            st.warning("The bag is empty! Check your 'Chips' column.")

    # 5. Show the Library
    with st.expander("View Library & Current Chips"):
        # We only show the columns we care about
        st.dataframe(df[['Game', 'Date Entered', 'Chips']])

except Exception as e:
    st.error("I'm still having trouble reading the sheet.")
    st.info(f"Technical error: {e}")
