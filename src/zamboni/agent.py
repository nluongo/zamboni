from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent


class SQLAgent:
    """
    Example agent class for demonstration purposes.
    This class should be replaced with an actual agent implementation.
    """

    def __init__(self):
        self.llm = init_chat_model("o4-mini", model_provider="openai")
        self.db = SQLDatabase.from_uri("sqlite:///data/zamboni.db")

        self.sql_toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.sql_tools = self.sql_toolkit.get_tools()

        self.system_message = """
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
        
        You should limit yourself to at most 10 queries of the database. Keep track of the number of queries you have made and stop when you hit 10.
        
        The last line of your output should contain only a decimal number representing your prediction between 0 (away team winning) and 1 (home team winning).
        """.format(
            dialect="SQLite",
        )

        self.agent_executor = create_react_agent(
            self.llm, tools=self.sql_tools, prompt=self.system_message
        )

    # for step in agent_executor.stream(
    #    {"messages": [{"role": "user", "content": question}]},
    #    stream_mode="values",
    # ):
    #    step["messages"][-1].pretty_print()

    def predict(self, game):
        question = f"Give a prediction for the following game: {game}"
        response = self.agent_executor.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        prediction = float(response["messages"][-1].content.split("\n")[-1])
        return prediction
