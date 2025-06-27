import logging
from zamboni.training import (
    ZamboniData,
    ModelInitializer,
    Trainer,
    SequentialStrategy,
    ResultsAnalyzer,
)
from zamboni.data_management import ColumnTracker, ZamboniDataManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

manager = ZamboniDataManager("data/games_all.parquet")
manager.load_parquet()
all_data = ZamboniData(manager.data)
all_columns = all_data.data.columns.tolist()

column_tracker = ColumnTracker(all_columns)
all_data.column_tracker = column_tracker

model_init = ModelInitializer("data/embed_test_nn", "EmbeddingNN", column_tracker)
model, optimizer, _, _ = model_init.get_model()

trainer = Trainer(model, optimizer)

strategy = SequentialStrategy(all_data, trainer)
trainer, all_preds, all_labels = strategy.run()

results = ResultsAnalyzer(all_preds, all_labels)
accuracy = results.get_accuracy()
print(f"Accuracy at 50%: {accuracy}")
accuracy = results.get_accuracy(threshold=0.6)
print(f"Accuracy at 60%: {accuracy}")
accuracy = results.get_accuracy(threshold=0.7)
print(f"Accuracy at 70%: {accuracy}")
accuracy = results.get_accuracy(threshold=0.8)
print(f"Accuracy at 80%: {accuracy}")
