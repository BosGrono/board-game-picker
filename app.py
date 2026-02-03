import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Read and Clean
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    # Column Mapping
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
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
        except:
            chips = 1
        try:
            wtp_val = row[wtp_col]
            wtp_chips = int(float(wtp_val)) if pd.notnull(wtp_val) else 0
        except:
            wtp_chips = 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # 3. User Interface (Sidebar Agency)
    st.sidebar.header("Selection Settings")
    mode = st.sidebar.radio(
        "Choose Selection Method:",
        ["Roll the D20", "Primary Only", "Want To Play Only", "Archive Only", "Greatest Hits Only"]
    )

    # Display counts in sidebar for transparency
    st.sidebar.divider()
    st.sidebar.write("**Bag Sizes (Chips):**")
    for bag_name, contents in bags.items():
        st.sidebar.write(f"- {bag_name}: {len(contents)}")

    st.write(f"Found **{len(df)}** games in your library.")
    
    # 4. Drawing Logic
    if st.button("🎰 Draw a Game!"):
        selected_bag_name = ""
        
        # Scenario A: User wants the Die to decide
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(1)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 Rolled a **{die_roll}**! Drawing from the **{selected_bag_name}** bag.")
        
        # Scenario B: User picked a specific bag
        else:
            selected_bag_name = mode.replace(" Only", "")
            st.info(f"Direct Draw: Drawing specifically from the **{selected_bag_name}** bag.")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging through the {selected_bag_name} bag...'):
                time.sleep(1.5)
                winner = random.choice(active_bag)
                st.balloons()
                st.header(f"Game selected: **{winner}**!")
                
                # --- Metadata Display ---
                winner_data = df[df[game_col] == winner].iloc[0]
                try:
                    current_chips_val = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                    w_chips = int(float(current_chips_val)) if pd.notnull(current_chips_val) else 1
                    prob = (w_chips / len(active_bag)) * 100
                    st.caption(f"Probability of selection: {prob:.2f}% ({w_chips} / {len(active_bag)} chips)")

                    plays_val = winner_data[plays_col]
                    if pd.notnull(plays_val):
                        try:
                            plays_num = int(float(plays_val))
                            if plays_num > 0: st.caption(f"Previous plays: {plays_num}")
                        except: pass

                    rating = winner_data[rating_col]
                    if pd.notnull(rating): st.caption(f"Average Rating: {rating}")

                    catalogue = winner_data[cat_col]
                    if pd.notnull(catalogue): st.caption(f"Catalogue Entry: {catalogue}")

                    bgg_id = winner_data[bgg_col]
                    if pd.notnull(bgg_id):
                        bgg_url = f"https://boardgamegeek.com/boardgame/{int(float(bgg_id))}"
                        st.markdown(f"<h6>🔗 <a href='{bgg_url}'>View on BoardGameGeek</a></h6>", unsafe_allow_html=True)
                except Exception:
                    st.caption("Metadata display encountered a minor issue.")
        else:
            st.warning(f"The {selected_bag_name} bag is empty!")

    with st.expander("View Full Library"):
        st.dataframe(df)

except Exception as e:
    st.error("Connection Error")
    st.info(f"Technical details: {e}")
