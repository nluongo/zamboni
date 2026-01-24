import altair as alt
import pandas as pd
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
    ZamboniAI is a machine learning platform that predicts the outcomes of NHL games.
    Models are trained on historical data to make predictions.
    """
)
st.sidebar.markdown(
    """
    ### How to Use
    1. Select a date from the date picker.
    2. Select the tab corresponding to your chosen game.
    3. View the predictions for the selected game.
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

inner_ticks_df = pd.DataFrame({"tick": [-0.25, 0, 0.25]})
outer_ticks_df = pd.DataFrame({"tick": [-0.5, 0.5]})

inner_ticks_mark = (
    alt.Chart(inner_ticks_df)
    .mark_tick(color="white", height=15, width=7)
    .encode(x="tick:Q")
)
outer_ticks_mark = (
    alt.Chart(outer_ticks_df)
    .mark_tick(color="white", height=30, width=7)
    .encode(x="tick:Q")
)

# Display predictions for the selected date
st.header("Games")
try:
    api_response = requests.get(
        f"https://zamboni.nicholas-luongo.com/api/{selected_date}"
    ).json()
    if len(api_response) == 0:
        st.info("No predictions available for the selected date.")
    else:
        predictions = sorted(
            api_response, key=lambda x: (x["homeAbbrev"], x["predicterName"])
        )
        matchups = list(
            set(
                [
                    f"{prediction['awayAbbrev']} @ {prediction['homeAbbrev']}"
                    for prediction in predictions
                ]
            )
        )
        home_teams = set(prediction["homeAbbrev"] for prediction in predictions)
        predicters = set(prediction["predicterName"] for prediction in predictions)
        tabs = st.tabs(matchups)

        header_height = 400
        predicter_height = 200
        for tab, matchup in zip(tabs, matchups):
            home_team = matchup[-3:]
            matchup_predictions = [
                prediction
                for prediction in predictions
                if prediction["homeAbbrev"] == home_team
            ]
            away_team = matchup_predictions[0]["awayAbbrev"]
            with tab:
                pred_name_col, away_team_col, pred_val_col, home_team_col = st.columns(
                    [1, 2, 1, 2]
                )

                away_tile = away_team_col.container(
                    horizontal_alignment="center",
                    vertical_alignment="center",
                    height=header_height,
                    border=False,
                )
                away_tile.title(away_team, text_alignment="center")
                away_tile.image(f"data/logos/{away_team}.png")

                vs_tile = pred_val_col.container(
                    horizontal_alignment="center",
                    vertical_alignment="center",
                    height=header_height,
                    border=False,
                )
                vs_tile.title("", text_alignment="center")

                home_tile = home_team_col.container(
                    horizontal_alignment="center",
                    vertical_alignment="center",
                    height=header_height,
                    border=False,
                )
                home_tile.title(home_team, text_alignment="center")
                home_tile.image(f"data/logos/{home_team}.png")

                for prediction in matchup_predictions:
                    pred_name_col, away_team_col, pred_val_col, home_team_col = (
                        st.columns([1, 2, 1, 2])
                    )
                    predicted_winner = prediction["predictedWinner"]
                    predicted_confidence = prediction["predictedConfidence"]
                    predicter_name = prediction["predicterName"]
                    outcome = prediction["outcome"]
                    home_team_goals = prediction["homeTeamGoals"]
                    away_team_goals = prediction["awayTeamGoals"]

                    if predicted_winner == home_team:
                        home_prob = predicted_confidence
                        away_prob = 1 - predicted_confidence
                    else:
                        home_prob = 1 - predicted_confidence
                        away_prob = predicted_confidence
                    if home_prob in [0, 1]:
                        home_moneyline_str = "N/A"
                        away_moneyline_str = "N/A"
                    elif home_prob > 0.5:
                        home_moneyline = -home_prob / (1 - home_prob) * 100
                        home_moneyline_str = f"{home_moneyline:.0f}"
                        away_moneyline = (1 - away_prob) / away_prob * 100
                        away_moneyline_str = f"+{away_moneyline:.0f}"
                    else:
                        away_moneyline = -away_prob / (1 - away_prob) * 100
                        away_moneyline_str = f"{away_moneyline:.0f}"
                        home_moneyline = (1 - home_prob) / home_prob * 100
                        home_moneyline_str = f"+{home_moneyline:.0f}"

                    df = pd.DataFrame(
                        {"category": ["Prediction"], "values": [home_prob - 0.5]}
                    )
                    chart = alt.Chart(df).encode(
                        y=alt.Y("category", axis=None),
                        x=alt.X(
                            "values",
                            scale=alt.Scale(domain=(-0.5, 0.5)),
                            axis=alt.Axis(
                                title=None,
                                domain=False,
                                ticks=False,
                                labels=False,
                                grid=False,
                            ),
                        ),
                    )
                    chart_mark = chart.mark_bar(size=2)
                    point_mark = chart.mark_point(
                        shape="diamond", size=15, strokeWidth=5
                    )
                    all_marks = (
                        chart_mark + point_mark + inner_ticks_mark + outer_ticks_mark
                    )

                    pred_name_tile = pred_name_col.container(
                        horizontal_alignment="left",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    pred_name_tile.write(f"## {predicter_name}")

                    away_tile = away_team_col.container(
                        horizontal_alignment="center",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    away_tile.title(f"{away_prob * 100:.0f}%", text_alignment="center")
                    away_tile.subheader(away_moneyline_str, text_alignment="center")

                    vs_tile = pred_val_col.container(
                        horizontal_alignment="center",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    vs_tile.altair_chart(all_marks)

                    home_tile = home_team_col.container(
                        horizontal_alignment="center",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    home_tile.title(f"{home_prob * 100:.0f}%", text_alignment="center")
                    home_tile.subheader(home_moneyline_str, text_alignment="center")

                if home_team_goals:
                    if home_team_goals > away_team_goals:
                        winner = home_team
                        winner_goals = home_team_goals
                        loser_goals = away_team_goals
                    else:
                        winner = away_team
                        winner_goals = away_team_goals
                        loser_goals = home_team_goals

                    pred_name_tile = pred_name_col.container(
                        horizontal_alignment="left",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    pred_name_tile.write("# :grey[Final]")

                    away_tile = away_team_col.container(
                        horizontal_alignment="center",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    away_tile.title(
                        f":grey[{away_team_goals}]", text_alignment="center"
                    )

                    home_tile = home_team_col.container(
                        horizontal_alignment="center",
                        vertical_alignment="center",
                        height=predicter_height,
                        border=False,
                    )
                    home_tile.title(
                        f":grey[{home_team_goals}]", text_alignment="center"
                    )


except requests.JSONDecodeError:
    st.warning(f"No prediction file found for {selected_date_str}.")
