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
    
    # --- Robust Column Mapping ---
    def get_col(target, options):
        match = [c for c in options if target.lower() in c.lower()]
        if not match:
            raise ValueError(f"Could not find a column containing '{target}'")
        return match[0]

    game_col = get_col('Game', df.columns)
    chip_col = get_col('Chips', df.columns)
    bgg_col = get_col('BGG_ID', df.columns)
    plays_col = get_col('Plays', df.columns)
    rating_col = get_col('Avg_Rating', df.columns)
    cat_col = get_col('Catalogue', df.columns)
    wtp_col = get_col('WTP_Count', df.columns)

    # 2. Build the Four Bags
    bags = {
        "Primary": [],
        "Archive": [],
        "Greatest Hits": [],
        "Want To Play": []
    }

    for index, row in df.iterrows():
        name = str(row[game_col])
        chips = int(row[chip_col]) if pd.notnull(row[chip_col]) else 1
        wtp_val = row[wtp_col]
        wtp_chips = int(wtp_val) if pd.notnull(wtp_val) and wtp_val >= 1 else 0
        catalog = str(row[cat_col]).strip()

        # Add to Catalogue-based bags
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        
        # Add to Want To Play bag independently
        if wtp_chips > 0:
            bags["Want To Play"].extend([name] * wtp_chips)

    # 3. User Interface
    st.sidebar.header("Selection Settings")
    mode = st.sidebar.radio(
        "Selection Mode",
        ["Roll the D20", "Primary Only", "Want To Play Only", "Archive Only", "Greatest Hits Only"]
    )

    st.write(f"Connected! Found **{len(df)}** games in the library.")
    
    if st.button("🎰 Draw a Game!"):
        selected_bag_name = ""
        
        # Handle Die Roll or Manual Selection
        if mode == "Roll the D20":
            with st.spinner('Rolling D20...'):
                time.sleep(1)
                die_roll = random.randint(1, 20)
                if die_roll <= 10: selected_bag_name = "Primary"
                elif die_roll <= 16: selected_bag_name = "Want To Play"
                elif die_roll <= 18: selected_bag_name = "Archive"
                else: selected_bag_name = "Greatest Hits"
                st.info(f"🎲 Rolled a **{die_roll}**! Drawing from the **{selected_bag_name}** bag.")
        else:
            selected_bag_name = mode.replace(" Only", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            with st.spinner(f'Rummaging through the {selected_bag_name} bag...'):
                time.sleep(2)
                winner = random.choice(active_bag)
                st.balloons()
                st.header(f"Game selected: **{winner}**!")
                
                # --- Metadata Display ---
                winner_data = df[df[game_col] == winner].iloc[0]
                
                # Probability (Small Text)
                w_chips = int(winner_data[wtp_col]) if selected_bag_name == "Want To Play" else int(winner_data[chip_col])
                prob = (w_chips / len(active_bag)) * 100
                st.caption(f"Probability of selection: {prob:.2f}% ({w_chips} / {len(active_bag)} chips)")

                # Conditional Plays
                plays = winner_data[plays_col]
                if pd.notnull(plays) and plays > 0:
                    st.caption(f"Previous plays: {int(plays)}")

                # Conditional Rating
                rating = winner_data[rating_col]
                if pd.notnull(rating):
                    st.caption(f"Average Rating: {rating}")

                # Catalogue Entry
                catalogue = winner_data[cat_col]
                if pd.notnull(catalogue):
                    st.caption(f"Catalogue Entry: {catalogue}")

                # Board Game Geek Link (Small)
                bgg_id = winner_data[bgg_col]
                if pd.notnull(bgg_id):
                    bgg_url = f"https://boardgamegeek.com/boardgame/{int(bgg_id)}"
                    st.markdown(f"<h6>🔗 <a href='{bgg_url}'>View on BoardGameGeek</a></h6>", unsafe_allow_html=True)
        else:
            st.warning(f"The {selected_bag_name} bag is empty! Check your spreadsheet filters.")

    with st.expander("View Full Library"):
        st.dataframe(df)

except Exception as e:
    st.error("Connection Error")
    st.info(f"I see these columns in your sheet: {list(df.columns) if 'df' in locals() else 'None'}")
    st.info(f"Technical details: {e}")
