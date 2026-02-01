import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
# We'll use a more direct export link
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Read the sheet
    df = pd.read_csv(SHEET_URL)
    
    # 2. Clean up column names (remove hidden spaces and make lowercase for easy matching)
    df.columns = df.columns.str.strip()
    
    # 3. Create the Virtual Bag
    virtual_bag = []
    
    # We find the right columns even if they aren't exactly 'Game' or 'Chips'
    # This looks for any column that STarts with 'Game' or 'Chip'
    game_col = [c for c in df.columns if 'Game' in c][0]
    chip_col = [c for c in df.columns if 'Chip' in c][0]
    # Find the BGG_ID column
    bgg_col = [c for c in df.columns if 'BGG_ID' in c][0]

    for index, row in df.iterrows():
        name = str(row[game_col])
        # If the chip cell is empty, we treat it as 1
        count = int(row[chip_col]) if pd.notnull(row[chip_col]) else 1
        virtual_bag.extend([name] * count)

    # 4. User Interface
    st.write(f"Found **{len(df)}** games with **{len(virtual_bag)}** total chips.")
    
    if st.button("🎰 Draw a Game!"):
        if len(virtual_bag) > 0:
            with st.spinner('Rummaging through the bag...'):
                time.sleep(2)
                winner = random.choice(virtual_bag)
                st.toast('Great pick!', icon='🎲')
                st.header(f"Game selected: **{winner}**!")
                
                # --- NEW: Link to Board Game Geek ---
                # Look up the BGG_ID for the winning game name
                winner_data = df[df[game_col] == winner].iloc[0]
                bgg_id = winner_data[bgg_col]
                
                if pd.notnull(bgg_id):
                    bgg_url = f"https://boardgamegeek.com/boardgame/{int(bgg_id)}"
                    st.subheader(f"🔗 [View on BoardGameGeek]({bgg_url})")
                # ------------------------------------
                
        else:
            st.warning("The bag is empty!")

    with st.expander("View Full Library"):
        st.dataframe(df)

except Exception as e:
    st.error("Connection Error")
    st.info(f"I see these columns in your sheet: {list(df.columns) if 'df' in locals() else 'None'}")
    st.info(f"Technical details: {e}")
