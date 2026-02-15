import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# --- 1. INITIALIZE SESSION STATE (The App's Memory) ---
if 'veto_list' not in st.session_state:
    st.session_state.veto_list = []
if 'last_draw' not in st.session_state:
    st.session_state.last_draw = None

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 2. Read and Clean
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    
    game_col = 'Game'
    chip_col = 'Chips'
    bgg_col = 'BGG_ID'
    plays_col = 'Recorded Plays'
    rating_col = 'Avg_Rating'
    cat_col = 'Cataloguing'
    wtp_col = 'WTP_Count'
    wtp_tag_col = 'WTP Tag' 

    df = df[df[game_col].fillna('').str.strip() != ''].copy()
    df.index = range(1, len(df) + 1)

    # 3. Build the Four Bags (Excluding Vetoed Games)
    bags = {"Primary": [], "Archive": [], "Greatest Hits": [], "Want To Play": []}

    for index, row in df.iterrows():
        name = str(row[game_col])
        # SKIP if the game is in the Veto List
        if name in st.session_state.veto_list:
            continue

        try: chips = int(float(row[chip_col])) if pd.notnull(row[chip_col]) else 1
        except: chips = 1
        try: wtp_chips = int(float(row[wtp_col])) if pd.notnull(row[wtp_col]) else 0
        except: wtp_chips = 0
            
        catalog = str(row[cat_col]).strip()
        if catalog in bags:
            bags[catalog].extend([name] * chips)
        if wtp_chips >= 1:
            bags["Want To Play"].extend([name] * wtp_chips)

    # --- 4. D20 CONFIGURATION ---
    with st.expander("⚙️ Bag Selection D20 Face Distribution"):
        col1, col2, col3, col4 = st.columns(4)
        f_primary = col1.number_input("Primary", 0, 20, 10)
        f_wtp = col2.number_input("WTP", 0, 20, 6)
        f_archive = col3.number_input("Archive", 0, 20, 2)
        f_gh = col4.number_input("G. Hits", 0, 20, 2)
        total_faces = f_primary + f_wtp + f_archive + f_gh
        st.write("Visual Odds Map: " + "🟦"*f_primary + "🟧"*f_wtp + "🟥"*f_archive + "🟩"*f_gh)

    # 5. USER AGENCY: Selection Method
    st.subheader("Selection Method")
    mode = st.radio("Choose how you want to pick a game:", ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"], horizontal=True)

    # 6. DRAWING LOGIC
    draw_button = st.button("🎰 Draw a Game!", use_container_width=True)
    
    # Check if a veto was just triggered
    if st.session_state.last_draw and st.session_state.last_draw in st.session_state.veto_list:
        st.warning(f"🚫 **{st.session_state.last_draw}** has been vetoed! Drawing a replacement...")
        time.sleep(1)
        draw_button = True # Force a re-draw

    if draw_button:
        selected_bag_name = ""
        if mode == "Roll the D20":
            die_roll = random.randint(1, total_faces if total_faces > 0 else 20)
            if die_roll <= f_primary: selected_bag_name = "Primary"
            elif die_roll <= (f_primary + f_wtp): selected_bag_name = "Want To Play"
            elif die_roll <= (f_primary + f_wtp + f_archive): selected_bag_name = "Archive"
            else: selected_bag_name = "Greatest Hits"
        else:
            selected_bag_name = mode.replace("Pick from ", "")

        active_bag = bags[selected_bag_name]

        if len(active_bag) > 0:
            winner = random.choice(active_bag)
            st.session_state.last_draw = winner # Save to memory
            st.balloons()
            st.header(f"Game selected: **{winner}**!")
            
            # --- VETO BUTTON ---
            if st.button(f"🚫 Veto {winner}?", type="secondary"):
                st.session_state.veto_list.append(winner)
                st.rerun()

            # Metadata Display
            winner_data = df[df[game_col] == winner].iloc[0]
            try:
                wtp_tags = winner_data[wtp_tag_col]
                if pd.notnull(wtp_tags) and str(wtp_tags).strip() != "":
                    st.subheader(f"♟️ Want to play tag: {wtp_tags}")
                
                current_val = winner_data[wtp_col] if selected_bag_name == "Want To Play" else winner_data[chip_col]
                w_chips = int(float(current_val)) if pd.notnull(current_val) else 1
                prob = (w_chips / len(active_bag)) * 100
                st.caption(f"Probability: {prob:.2f}% | Rating: {winner_data[rating_col]}")
            except: pass
        else:
            st.warning(f"The {selected_bag_name} bag is empty!")

    # --- 7. VISUAL STATS DASHBOARD ---
    st.write("---")
    with st.expander("📊 Collection Analytics"):
        st.subheader("Bag Composition")
        # Pie Chart of Cataloguing
        cat_counts = df[cat_col].value_counts()
        st.write("Number of games in each catalog category:")
        st.bar_chart(cat_counts)
        
        

        st.subheader("Top Rated Games")
        # Sort and show top 10 ratings
        top_10 = df[[game_col, rating_col]].dropna().sort_values(by=rating_col, ascending=False).head(10)
        st.table(top_10.set_index(game_col))
        
        if st.session_state.veto_list:
            st.write("---")
            st.write(f"🚫 **Games Vetoed this Session:** {', '.join(st.session_state.veto_list)}")
            if st.button("Clear Vetoes"):
                st.session_state.veto_list = []
                st.rerun()

    # --- BOTTOM SECTION ---
    with st.expander("🏆 Greatest Hits"):
        gh_df = df[df[cat_col].str.strip() == "Greatest Hits"].copy()
        gh_ranked = gh_df.sort_values(by=rating_col, ascending=False)
        if not gh_ranked.empty:
            st.table(gh_ranked[[game_col, rating_col, plays_col]].reset_index(drop=True).style.format({rating_col: "{:.1f}"}))

    with st.expander("🔥 Want To Play"):
        wtp_display_df = df[pd.to_numeric(df[wtp_col], errors='coerce') >= 1].copy()
        wtp_ranked = wtp_display_df.sort_values(by=wtp_col, ascending=False)
        if not wtp_ranked.empty:
            st.table(wtp_ranked[[game_col, wtp_col, wtp_tag_col, rating_col]].reset_index(drop=True).style.format({rating_col: "{:.1f}", wtp_col: "{:.0f}"}))
    
    with st.expander("📒 View Full Library"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
