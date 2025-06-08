class GamePredicter:
    """
    Base class for game prediction.
    Takes a Game object and outputs 1 if the home team is predicted to win, 0 otherwise.
    Designed to be inherited by more specific predicters.
    """

    def __init__(self, id, name, active=True):
        """
        Initializes the GamePredicter.
        This constructor can be extended by subclasses to initialize additional attributes.
        """
        self.id = id
        self.name = name
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


class HomeTeamWinsPredicter(GamePredicter):
    """
    Example subclass that always predicts the home team wins.
    """

    def predict(self, game):
        """
        Predicts that the home team wins.

        Args:
            game: A Game object containing game data.

        Returns:
            int: Always returns 1.
        """
        return 1


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

    def predict(self, game):
        """
        Predicts the outcome using the neural network model.

        Args:
            game: A Game object containing game data.

        Returns:
            int: 1 if home team is predicted to win, 0 otherwise.
        """
        # Example: assumes game.to_features() returns a tensor or array for the model
        features = game.to_features()
        output = self.model(features)
        # Assume output is a probability; threshold at 0.5
        return int(output >= 0.5)
