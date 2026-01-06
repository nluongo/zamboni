from fastapi import FastAPI
import uvicorn
from zamboni.sql import SQLHandler
from zamboni.utils import confidence_from_prediction

app = FastAPI()

@app.get("/health")
@app.head("/health")
def health():
        return {"status": "ok"}

@app.get("/api/{date_str}")
def read_root(date_str):
    sql_handler = SQLHandler()
    games_df = sql_handler.query_games_with_predictions(date_str, date_str)

    if games_df is None:
        return []

    out = []
    for index, row in games_df.iterrows():
        game = {
            "homeAbbrev": row["homeAbbrev"],
            "awayAbbrev": row["awayAbbrev"],
            "homeTeamGoals": row["homeTeamGoals"],
            "awayTeamGoals": row["awayTeamGoals"],
            "outcome": row["outcome"],
            "inOT": row["inOT"],
            "prediction": row["prediction"],
            "predicterName": row["predicterName"],
        }
        if game["prediction"] >= 0.5:
            game["predictedWinner"] = game["homeAbbrev"]
        else:
            game["predictedWinner"] = game["awayAbbrev"]
        game["predictedConfidence"] = confidence_from_prediction(game["prediction"])
        out.append(game)
    return out


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
