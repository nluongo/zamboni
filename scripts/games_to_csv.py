from zamboni import SQLHandler
from zamboni.data_management import ColumnTracker

def games_to_csv(games_df, csv_name, eval_only=False):
    column_tracker = ColumnTracker(games_df.columns)
    drop_columns = column_tracker.notrain
    target_column = column_tracker.target
    train_columns = column_tracker.inputs
    if eval_only:
        drop_columns += ['outcome']
        columns_ordered = train_columns
    else:
        columns_ordered = [target_column] + train_columns
    games_df = games_df.drop(drop_columns, axis=1)
    games_df = games_df.dropna()
    print(games_df)
    games_df.to_csv(csv_name, columns=columns_ordered, index=False, header=False)
