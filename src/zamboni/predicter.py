from zamboni.data_management import ColumnTracker
from zamboni.training import Trainer, ModelInitializer
from zamboni.data_management import ZamboniData
from zamboni.training import SequentialStrategy
from zamboni.sql.sql_handler import SQLHandler


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

    def update(self, new_games):
        """
        Updates the predicter with new game data. Predictions are registered and model is trained if applicable.
        This method can be overridden by subclasses if they need to process new games differently.

        Args:
            new_games: A DataFrame or similar structure containing new game data.
        """
        raise NotImplementedError("Subclasses should implement this method.")

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

    def __init__(self, id, name, active):
        super().__init__(id, name, active)
        self.trainable = False

    def predict(self, game):
        """
        Predicts that the home team wins.

        Args:
            game: A Game object containing game data.

        Returns:
            int: Always returns 1.
        """
        return 1

    def update(self, zdata: ZamboniData):
        """
        Updates the predicter with new game data.
        This implementation does nothing as this predicter does not require training.

        Args:
            games: A DataFrame or similar structure containing new game data.
        """
        sql_handler = SQLHandler()
        preds = [self.predict(game) for game in zdata.data.itertuples()]
        for i in range(len(zdata.data)):
            game = zdata.data.iloc[[i]]
            game_id = game["id"].item()
            prediction = preds[i]
            sql_handler.record_game_prediction(game_id, self.id, prediction)


class NNGamePredicter(GamePredicter):
    """
    Example subclass using a neural network for prediction.
    """

    def __init__(self, id, name, active, model_path):
        """
        Args:
            model: A trained neural network model.
        """
        super().__init__(id, name, active)
        self.model_path = model_path
        self.trainer = None
        self.model_init = None
        self.trainable = True
        self.training_strategy = SequentialStrategy

    def get_trainer(self, data, overwrite=False):
        self.data = data
        self.column_tracker = ColumnTracker(data.data.columns.tolist())
        self.model_init = ModelInitializer(
            self.model_path, "EmbeddingNN", self.column_tracker
        )
        self.model, self.optimizer, self.scaler, _, _ = self.model_init.get_model(
            overwrite
        )
        self.trainer = Trainer(self.model, self.optimizer)

    def update(self, zdata: ZamboniData):
        """
        Updates the predicter with new game data.
        If trainable, it initializes the trainer and runs the training strategy.

        Args:
            zdata: A ZamboniData object containing new game data.
        """
        if not self.trainer:
            self.get_trainer(zdata, overwrite=False)

        _, preds, labels = self.run_strategy()
        preds, labels = preds.numpy(), labels.numpy()

        sql_handler = SQLHandler()
        for i in range(len(zdata.data)):
            game = zdata.data.iloc[[i]]
            game_id = game["id"].item()
            prediction = preds[i]
            sql_handler.record_game_prediction(game_id, self.id, prediction)

    def run_strategy(self):
        """
        Runs the training strategy for the neural network.
        This method should be called after initializing the trainer.
        """
        if not self.trainer:
            raise ValueError("Trainer not initialized. Call get_trainer first.")
        strategy = self.training_strategy(self.data, self.trainer)
        return strategy.run()

    def predict(self, game):
        """
        Predicts the outcome using the neural network model.

        Args:
            game: A Game object containing game data.

        Returns:
            int: 1 if home team is predicted to win, 0 otherwise.
        """
        if not self.trainer:
            self.get_trainer(game, overwrite=False)

        zamboni_data = ZamboniData(game, column_tracker=self.column_tracker)
        zamboni_data.prep_data(scaler=self.scaler, fit=False)

        _, pred, _ = self.trainer.eval(zamboni_data.loader)
        pred = pred[0].item()
        # Assume output is a probability; threshold at 0.5
        return pred


class AgentGamePredicter(GamePredicter):
    """
    Example subclass that uses an agent for prediction.
    """

    def __init__(self, id, name, active, agent):
        """
        Args:
            agent: An agent that can predict game outcomes.
        """
        super().__init__(id, name, active)
        self.trainable = False
        self.agent = agent

    def predict(self, game):
        """
        Predicts the outcome using the agent.

        Args:
            game: A Game object containing game data.

        Returns:
            int: 1 if home team is predicted to win, 0 otherwise.
        """
        return self.agent.predict(game)
