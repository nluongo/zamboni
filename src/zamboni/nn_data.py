import logging
import torch
from .data_management import ZamboniData
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)

class ZamboniDataset(Dataset):
    """Custom Dataset class to handle parquet data"""

    def __init__(self, data, target_column, cat_features=None, nonet_columns=None):
        """
        Split columns based on features, labels, and data type

        :param data: Path to data file
        :param target_column: Column containing labels
        :cat_features: Columns holding categorical features
        """
        self.feature_data = data.drop(columns=target_column)
        self.features = self.feature_data.values
        self.cont_features = (
            self.feature_data.drop(columns=cat_features).astype("float64").values
        )
        self.cat_features = self.feature_data[cat_features].astype("int").values
        self.labels = data[target_column].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        x_cont = torch.tensor(self.cont_features[idx], dtype=torch.float32)
        x_cat = torch.tensor(self.cat_features[idx], dtype=torch.long)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        if self.cat_features is not None:
            return x_cont, x_cat, y
        else:
            return x_cont, y


def create_dataset(data: ZamboniData) -> ZamboniDataset:
    """
    Create dataset
    """
    target_column = data.column_tracker.target
    categorical_columns = data.column_tracker.categorical
    notrain_columns = data.column_tracker.notrain
    dataset = ZamboniDataset(
        data.data_scaled, target_column, categorical_columns, notrain_columns
    )
    logger.debug(f"{len(dataset)} samples")
    return dataset


def create_dataloader(dataset: ZamboniDataset) -> DataLoader:
    """
    Create dataloader
    """
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    return dataloader
