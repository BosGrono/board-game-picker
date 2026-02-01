import streamlit as st
import random
import time

# 1. Setup the Title and Description
st.title("🎲 The Board Game Draw Bag")
st.write("The longer a game sits unplayed, the higher the chance it gets picked!")

# 2. Mock Data (We will replace this with your Spreadsheet later!)
# 'weight' represents the number of weeks/chips in the bag
games_library = [
    {"name": "Terraforming Mars", "weight": 1},
    {"name": "Gloomhaven", "weight": 10},
    {"name": "Catan", "weight": 2},
    {"name": "Wingspan", "weight": 5}
]

# 3. The Logic: Creating the Virtual Bag
virtual_bag = []
for game in games_library:
    # This adds the game name to the bag 'weight' times
    virtual_bag.extend([game["name"]] * game["weight"])

# 4. The User Interface
st.divider()
if st.button("🎰 Draw a Game!"):
    with st.spinner('Rummaging through the bag...'):
        time.sleep(2) # Adds a little suspense!
        
        # This is the randomizer
        winner = random.choice(virtual_bag)
        
        st.balloons() # Visual celebration
        st.success(f"The winner is: **{winner}**!")
        
        # Show the odds for transparency
        total_chips = len(virtual_bag)
        game_chips = virtual_bag.count(winner)
        probability = (game_chips / total_chips) * 100
        st.info(f"This game had a {probability:.1f}% chance of being drawn.")

# 5. Show the current "Bag" contents
with st.expander("View Current Odds"):
    st.write("Here is how many 'chips' are currently in the bag:")
    for game in games_library:
        st.write(f"- {game['name']}: {game['weight']} chips")
