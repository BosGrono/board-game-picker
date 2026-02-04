import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Game Night Picker", page_icon="🎲")
st.title("🎲 The Board Game Draw Bag")

# --- 1. INITIALIZE CONFIG AT THE TOP (Outside the try block) ---
if 'd20_config' not in st.session_state:
    st.session_state.d20_config = {
        "Primary": 10,
        "Want To Play": 6,
        "Archive": 2,
        "Greatest Hits": 2
    }

SHEET_ID = '1w2zW4_P2fPqE-BCjPaAJTWT7eoCksqUxnvyvfmgf5a8'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

try:
    # 2. Read and Clean
    df = pd.read_csv(SHEET_URL)
    # ... (Keep your column mapping and bag building logic here, properly indented) ...
    
    # --- 3. D20 CONFIGURATION (Inside the try, since we need the bags) ---
    with st.expander("⚙️ Configure D20 Odds (Total must = 20)"):
        cols = st.columns(4)
        new_config = {}
        for i, (bag_name, current_val) in enumerate(st.session_state.d20_config.items()):
            new_config[bag_name] = cols[i].number_input(
                bag_name, min_value=0, max_value=20, value=current_val, key=f"cfg_{bag_name}"
            )
        
        if sum(new_config.values()) != 20:
            st.error(f"Total is {sum(new_config.values())}. Must be 20!")
            st.session_state.valid_config = False
        else:
            st.session_state.d20_config = new_config
            st.session_state.valid_config = True

    # --- 4. SELECTION METHOD ---
    st.subheader("Selection Method")
    mode = st.radio(
        "Choose how you want to pick a game:",
        ["Roll the D20", "Pick from Primary", "Pick from Want To Play", "Pick from Archive", "Pick from Greatest Hits"],
        horizontal=True
    )

    # ... (The rest of your logic, ensuring it stays indented under the 'try') ...

except Exception as e:
    st.error("Connection Error")
    st.info(f"Technical details: {e}")
