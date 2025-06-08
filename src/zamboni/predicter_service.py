from zamboni import SQLHandler
from zamboni.predicter import (
    GamePredicter,
    HomeTeamWinsPredicter,
    NNGamePredicter,
)  # Import your predictor classes as needed

# Map predicterType strings to classes
PREDICTER_TYPE_MAP = {
    "GamePredicter": GamePredicter,
    "HomeTeamWinsPredicter": HomeTeamWinsPredicter,
    "NNGamePredicter": NNGamePredicter,
    # Add other mappings as needed
}


class PredicterService:
    """
    Service to load Predicter objects from the database using SQLHandler.
    """

    def __init__(self, db_path="data/zamboni.db"):
        self.sql_handler = SQLHandler(db_path)

    def get_predicters(self):
        """
        Queries the predicterRegister table and returns a list of Predicter objects.
        """
        rows = self.sql_handler.query(
            "SELECT id, "
            "predicterName, "
            "predicterType, "
            "predicterPath, "
            "trainable, "
            "active "
            "FROM predicterRegister"
        )
        predicters = []
        for index, row in rows.iterrows():
            row = row.to_dict()
            predicter = self.init_predicter(row)
            predicters.append(predicter)
        return predicters

    def init_predicter(self, df_row):
        """
        Initializes a predicter by name and additional parameters.
        """
        predicter_id = df_row.get("id")
        predicter_type = df_row.get("predicterType")
        predicter_name = df_row.get("predicterName")
        predicter_path = df_row.get("predicterPath")
        predicter_active = df_row.get("active", True)

        predicter_class = PREDICTER_TYPE_MAP.get(predicter_type)

        if predicter_class == HomeTeamWinsPredicter:
            # Special case for HomeTeamWinsPredicter, which does not require additional parameters
            return predicter_class(
                id=predicter_id, name=predicter_name, active=predicter_active
            )
        elif predicter_class == NNGamePredicter:
            # For NNGamePredicter, we might need to pass the model path
            return predicter_class(
                id=predicter_id,
                name=predicter_name,
                active=predicter_active,
                model_path=predicter_path,
            )
        else:
            raise ValueError(f"Unknown predicter class '{predicter_class}'.")
