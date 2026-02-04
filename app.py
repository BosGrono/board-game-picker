import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲", layout="wide")
st.title("🎲 The Board Game Draw Bag")

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 1. Read and Clean
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    # Column Mapping
    game_col, chip_col, cat_col, wtp_col = 'Game', 'Chips', 'Cataloguing', 'WTP_Count'
    bgg_col, plays_col, rating_col = 'BGG_ID', 'Recorded Plays', 'Avg_Rating'

    # 2. Build the Four Bags
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        try:
            chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
            wtp_chips = int(float(row[wtp_col])) if pd.notnull(row[wtp_col]) else 0
        except:
            chips, wtp_chips = 1, 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # --- NEW: LIVE BAG STATS DASHBOARD ---
    st.subheader("📊 Library Analytics")
    
    # Calculate stats for the dashboard
    stats_data = []
    for b_name, b_contents in bags.items():
        unique_games = len(set(b_contents))
        total_chips = len(b_contents)
        stats_data.append({"Bag": b_name, "Unique Games": unique_games, "Total Chips": total_chips})
    
    stats_df = pd.DataFrame(stats_data)

    # Top Row Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Games", len(df))
    m2.metric("Primary Bag", f"{len(set(bags['Primary']))} Games")
    m3.metric("WTP Bag", f"{len(set(bags['Want To Play']))} Games")
    m4.metric("Total Chips", stats_df["Total Chips"].sum())

    # Visual Distribution Chart
    st.write("#### Chip Count Distribution")
    # Setting the index to 'Bag' makes the chart label the bars correctly
    chart_df = stats_df.set_index("Bag")[["Total Chips"]]
    st.bar_chart(chart_df, color="#2E86C1")

    st.write("---")

    # 3. Selection Method
    st.subheader("🎯 Selection Method")
    mode = st.radio(
        "Choose how you want to pick a game:",
        ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"],
        horizontal=True
    )

    # 4. Drawing Logic
    if st.button("🎰 Draw a Game!", use_container_width=True):
        selected_bag_name = ""
        
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(0.7)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 **D20 Result: {die_roll}** → Drawing from the **{selected_bag_name}** bag.")
        else:
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Searching {selected_bag_name}...'):
                time.sleep(1.2)
                winner = random.choice(active_bag)
                st.balloons()
                
                # Result Card
                with st.container(border=True):
                    st.header(f"Winner: {winner}!")
                    
                    winner_data = df[df[game_col] == winner].iloc[0]
                    
                    # Metadata with formatting
                    c_key = wtp_col if selected_bag_name == "Want To Play" else chip_col
                    w_chips = int(float(winner_data[c_key])) if pd.notnull(winner_data[c_key]) else 1
                    prob = (w_chips / len(active_bag)) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Probability:** {prob:.2f}%")
                    col2.write(f"**Plays:** {int(float(winner_data[plays_col])) if pd.notnull(winner_data[plays_col]) else 0}")
                    col3.write(f"**Rating:** {winner_data[rating_col] if pd.notnull(winner_data[rating_col]) else 'N/A'}")
                    
                    if pd.notnull(winner_data[bgg_col]):
                        b_url = f"https://boardgamegeek.com/boardgame/{int(float(winner_data[bgg_col]))}"
                        st.link_button("View on BoardGameGeek", b_url)
        else:
            st.warning(f"The {selected_bag_name} bag is empty!")

    # 5. Footer Logic
    st.write("---")
    with st.expander("🎲 View D20 Probability Guide"):
        st.write("Visual Odds Map: " + "🟦"*10 + "🟧"*6 + "🟥"*2 + "🟩"*2)
        st.caption("Blue: Primary (50%) | Orange: WTP (30%) | Red: Archive (10%) | Green: G. Hits (10%)")

    with st.expander("View Full Library Data"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Error connecting to spreadsheet: {e}")
