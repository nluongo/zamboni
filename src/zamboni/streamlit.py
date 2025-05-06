import streamlit as st
from zamboni.sql.sql_helpers import days_games
from zamboni.utils import today_date_str

# Get today's date
today_date = today_date_str()

# Set up the Streamlit page
st.set_page_config(
    page_title="ZamboniAI",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar content
st.sidebar.image("zamboni_logo.png", width=200)
st.sidebar.title("ZamboniAI")
st.sidebar.markdown(
    """
    ## NHL Game Predictions
    ZamboniAI is a machine learning model that predicts the outcome of NHL games.
    The model is trained on historical data and uses various features to make predictions.
    """
)
st.sidebar.markdown(
    """
    ### How to Use
    1. Select a date from the date picker.
    2. View the predictions for the selected date.
    """
)
st.sidebar.markdown(
    """
    ### Disclaimer
    Predictions are for entertainment purposes only and are guaranteed to be wrong at times.
    """
)
st.sidebar.markdown(
    """
    ### Source Code
    The source code for this project is available on [GitHub](https://github.com/nluongo/zamboni).
    """
)

# Main page content
st.title("ZamboniAI")
st.subheader(f"NHL Game Predictions for {today_date}")

# Date input for selecting games
selected_date = st.date_input("Select a date to view predictions:", value=today_date)
selected_date_str = str(selected_date)

# Display predictions for the selected date
st.header("Games")
try:
    with open(f"data/predictions/preds_{selected_date_str}.txt", "r") as f:
        pred_lines = f.readlines()
    pred_lines = [line.strip() for line in pred_lines]
    game_results = days_games(selected_date_str)
    if pred_lines:
        for line in pred_lines:
            if 'Game: ' in line:
                home_team_goals = away_team_goals = None
                split_line = line.split(' ')
                home_team_abbrev, away_team_abbrev = split_line[1], split_line[3]
                for result in game_results:
                    if home_team_abbrev == result[0] and away_team_abbrev == result[2]:
                        home_team_goals, away_team_goals = result[1], result[3]
                        break
            if '---' in line:
                if home_team_goals and away_team_goals:
                    st.text(f"{home_team_abbrev} ({home_team_goals}) - {away_team_abbrev} ({away_team_goals})")
                else:
                    st.text(f"No score available")
            st.text(line)
    else:
        st.info("No predictions available for the selected date.")
except FileNotFoundError:
    st.warning(f"No prediction file found for {selected_date_str}.")
