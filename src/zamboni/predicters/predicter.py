from zamboni.sport import Game
from typing import List
# from zamboni.agent import SQLAgent

def initialize_predicter(id, name, class_name, model_path, active, sql_handler=None):
    """
    Docstring for initialize_predicter
    
    :param name: Name of predicter
    :param class_name: Class of predicter (e.g. "HomeTeamWinsPredicter", "BDTGamePredicter", "NNGamePredicter")
    :param model_path: If relevant, path to model file for predicter (e.g. for BDT or NN predicters)
    """
    if class_name == "HomeTeamWinsPredicter":
        predicter = HomeTeamWinsPredicter(id=id, name=name, active=active)
    elif class_name == "MoreWinsPredicter":
        predicter = MoreWinsPredicter(id=id, name=name, active=active, sql_handler=sql_handler)
    elif class_name == "BDTGamePredicter":
        from .bdt_predicter import BDTGamePredicter
        predicter = BDTGamePredicter(id=id, 
                                     name=name, 
                                     active=active, 
                                     model_path=model_path, 
                                     sql_handler=sql_handler)
    elif class_name == "NNGamePredicter":
        from .nn_predicter import NNGamePredicter
        predicter = NNGamePredicter(id=id, name=name, active=active, model_path=model_path)
    else:
        raise ValueError(f"Unknown predicter class: {class_name}")
    
    return predicter

class GamePredicter:
    """
    Base class for game prediction.
    Takes a Game object and outputs 1 if the home team is predicted to win, 0 otherwise.
    Designed to be inherited by more specific predicters.
    """

    def __init__(self, id, name, active):
        """
        Initializes the GamePredicter.
        This constructor can be extended by subclasses to initialize additional attributes.
        """
        self.id = id
        self.name = name
        self.trainable = False
        self.active = active

    def predict(self, game):
        """
        Predicts the outcome of a game.
        Should be overridden by subclasses.

        Args:
            game: A Game object containing game data.

        Returns:
            int: 1 if home team is predicted to win, 0 otherwise.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def update(self, games: List[Game]) -> None:
        """
        Updates the predicter with new game data. Predictions are registered and model is trained if applicable.
        This method can be overridden by subclasses if they need to process new games differently.

        Args:
            new_games: A DataFrame or similar structure containing new game data.
        """
        games.data['preds'] = games.data.apply(lambda game: self.predict(game), axis=1)

    def run_strategy(self):
        """
        Runs the training strategy for the predicter.
        This method should be overridden by subclasses if they have a specific training strategy.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def clean_up(self):
        """
        Cleans up resources used by the predicter.
        This method can be overridden by subclasses if they need to release additional resources.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class HomeTeamWinsPredicter(GamePredicter):
    """
    Example subclass that always predicts the home team wins.
    """

    trainable = False

    def predict(self, game):
        """
        Predicts that the home team wins.

        Args:
            game: A Game object containing game data.

        Returns:
            int: Always returns 1.
        """
        return 1

class MoreWinsPredicter(GamePredicter):
    """
    Example subclass that always predicts the home team wins.
    """

    trainable = False

    def __init__(self, id, name, active, sql_handler):
        super().__init__(id, name, active)
        self.sql_handler = sql_handler

    def predict(self, game):
        """
        Predicts that the team with more wins to date in the season will win. Ties goes to the home team.

        Args:
            game: A Game object containing game data.

        Returns:
            int: 1 if home team wins else 0
        """
        home_team_id = game["homeTeamID"]
        away_team_id = game["awayTeamID"]
        date_played = game["datePlayed"]
        home_wins = self.sql_handler.wins_to_date(home_team_id, date_played)
        away_wins = self.sql_handler.wins_to_date(away_team_id, date_played)
        if home_wins >= away_wins:
            out = 1
        else:
            out = 0
        return out


# class AgentGamePredicter(GamePredicter):
#    """
#    Example subclass that uses an agent for prediction.
#    """
#
#    trainable = False
#
#    def __init__(self, id, name, active):
#        """
#        Args:
#            agent: An agent that can predict game outcomes.
#        """
#        super().__init__(id, name, active)
#        self.trainable = False
#        self.agent_class = SQLAgent
#        self.agent = self.agent_class()
#
#    def predict(self, game):
#        """
#        Predicts the outcome using the agent.
#
#        Args:
#            game: A Game object containing game data.
#
#        Returns:
#            int: 1 if home team is predicted to win, 0 otherwise.
#        """
#        return self.agent.predict(game)
