#from zamboni import SQLHandler
# from zamboni.predicter import (
#    GamePredicter,
#    HomeTeamWinsPredicter,
#    NNGamePredicter,
# )  # Import your predictor classes as needed

# Map predicterType strings to classes
# predicter_type_map = {
#    "GamePredicter": GamePredicter,
#    "HomeTeamWinsPredicter": HomeTeamWinsPredicter,
#    "NNGamePredicter": NNGamePredicter,
#    # Add other mappings as needed
# }


#class PredicterService:
#    """
#    Service to load Predicter objects from the database using SQLHandler.
#    """
#
#    def __init__(self, db_path="data/zamboni.db", sql_handler=None):
#        if sql_handler is None:
#            self.sql_handler = SQLHandler(db_path)
#        else:
#            self.sql_handler = sql_handler
#
#    def get_predicters(self):
#        """
#        Queries the predicterRegister table and returns a list of Predicter objects.
#        """
#        # First check if table exists
#        table_exists = self.sql_handler.query(
#            "SELECT name "
#            "FROM sqlite_master "
#            "WHERE type='table' AND name='predicterRegister'"
#        )
#        if table_exists is None:
#            return []
#
#        rows = self.sql_handler.query(
#            "SELECT id, "
#            "predicterName, "
#            "predicterType, "
#            "predicterPath, "
#            "trainable, "
#            "active "
#            "FROM predicterRegister"
#        )
#        predicters = []
#        if rows is None:
#            return predicters
#        for index, row in rows.iterrows():
#            row = row.to_dict()
#            predicter = self.init_predicter(row)
#            predicters.append(predicter)
#        return predicters
#
#    def init_predicter(self, df_row):
#        """
#        Initializes a predicter by name and additional parameters.
#        """
#        predicter_id = df_row.get("id")
#        predicter_type = df_row.get("predicterType")
#        predicter_name = df_row.get("predicterName")
#        predicter_path = df_row.get("predicterPath")
#        predicter_active = df_row.get("active", True)
#
#        predicter_class = predicter_type_map.get(predicter_type)
#
#        if predicter_type == "HomeTeamWinsPredicter":
#            from zamboni.predicter import HomeTeamWinsPredicter
#
#            predicter_class = HomeTeamWinsPredicter
#            # Special case for HomeTeamWinsPredicter, which does not require additional parameters
#            return predicter_class(
#                id=predicter_id,
#                name=predicter_name,
#                active=predicter_active,
#            )
#        elif predicter_class == NNGamePredicter:
#            try:
#                from zamboni.predicter import NNGamePredicter
#
#                predicter_class = NNGamePredicter
#                # For NNGamePredicter, we might need to pass the model path
#                return predicter_class(
#                    id=predicter_id,
#                    name=predicter_name,
#                    active=predicter_active,
#                    model_path=predicter_path,
#                    sql_handler=self.sql_handler,
#                )
#            except ImportError:
#                raise ImportError("[ml] installation option required for NN predicter")
#        else:
#            raise ValueError(f"Unknown predicter class '{predicter_class}'.")
#
#    def register_predicter(self, name, predicter_class_name, path="", active=True):
#        """
#        Register a new predicter, adding entries to relevant tables
#        """
#        self.sql_handler.add_predicter_to_register(
#            name, predicter_class_name, path, active
#        )
#        predicter_class = predicter_type_map.get(predicter_class_name)
#        if not predicter_class.trainable:
#            return
#        predicter_id = self.sql_handler.predicter_id_from_name(name)
#        self.sql_handler.add_predicter_to_last_training(predicter_id)
