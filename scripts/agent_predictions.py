from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

llm = init_chat_model("o4-mini", model_provider="openai")
db = SQLDatabase.from_uri("sqlite:///data/zamboni.db")

sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sql_toolkit.get_tools()

system_message = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Here are the schemas of the most relevant tables.

games:
CREATE TABLE IF NOT EXISTS games (
   id INTEGER PRIMARY KEY,
   apiID INTEGER,
   seasonID INTEGER,
   homeTeamID INTEGER,
   awayTeamID INTEGER,
   datePlayed INTEGER,
   dayOfYrPlayed INTEGER,
   yrPlayed INTEGER,
   timePlayed INTEGER,
   homeTeamGoals INTEGER,
   awayTeamGoals INTEGER,
   gameTypeID INTEGER,
   lastPeriodTypeID INTEGER,
   outcome INTEGER,
   inOT INTEGER,
   recordCreated INTEGER
)

teams:
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    apiID INTEGER,
    name TEXT,
    nameAbbrev TEXT,
    conferenceAbbrev TEXT,
    divisionAbbrev TEXT
)

Query the game from the games table to retrieve all available information (e.g. which team is home). Note that the outcome column of the games table contains 1 if the home team won the game and 0 if the away team won the game. You should only consider games that took place before the game in question when formulating your predictions.

Carefully consider the outputs of these calls so that you can give an accurate summary.

Any dates given will be in 'YYYY-MM-DD' format.

Do NOT use the gamePredictions table.

You should limit yourself to at most 10 queries of the database.

The last line of your output should your prediction in the form of a decimal number between 0 (away team winning) and 1 (home team winning).
""".format(
    dialect="SQLite",
)

agent_executor = create_react_agent(llm, tools=sql_tools, prompt=system_message)

question = "Give a prediction for the game between the Florida Panthers (ID 13) and Edmonton Oilers (ID 12) of 2025-06-17?"

for step in agent_executor.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
