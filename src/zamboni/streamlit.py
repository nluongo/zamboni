import requests
import streamlit as st
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
st.subheader("NHL Game Predictions")

# Date input for selecting games
selected_date = st.date_input("Select a date to view predictions:", value=today_date)
selected_date_str = str(selected_date)
st.session_state.selected_date = selected_date

# Display predictions for the selected date
st.header("Games")
try:
    api_response = requests.get(
        f"https://nicholas-luongo.com/zamboni/api/{selected_date}"
    ).json()
except requests.JSONDecodeError:
    st.warning(f"No prediction file found for {selected_date_str}.")

if len(api_response) == 0:
    st.info("No predictions available for the selected date.")
else:
    predictions = sorted(
        api_response, key=lambda x: (x["homeAbbrev"], x["predicterName"])
    )
    home_teams = set(prediction["homeAbbrev"] for prediction in predictions)
    for home_team in home_teams:
        matchup_predictions = [
            prediction
            for prediction in predictions
            if prediction["homeAbbrev"] == home_team
        ]
        away_team = matchup_predictions[0]["awayAbbrev"]
        st.subheader(f"{away_team} at {home_team}")
        for prediction in matchup_predictions:
            predicted_winner = prediction["predictedWinner"]
            predicted_confidence = prediction["predictedConfidence"]
            predicter_name = prediction["predicterName"]
            outcome = prediction["outcome"]
            home_team_goals = prediction["homeTeamGoals"]
            away_team_goals = prediction["awayTeamGoals"]
            st.text(f"Predicter name: {predicter_name}")
            st.text(f"Predicted winner: {predicted_winner}")
            st.text(f"Predicted confidence: {predicted_confidence * 100:.1f}%")
            if home_team_goals > away_team_goals:
                winner = home_team
                winner_goals = home_team_goals
                loser_goals = away_team_goals
            else:
                winner = away_team
                winner_goals = away_team_goals
                loser_goals = home_team_goals
            st.text("----------")
        st.text(f"Winner: {winner} ({winner_goals} - {loser_goals})")
