import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ColumnTracker:
    """Class to track columns for various uses in data"""

    def __init__(
        self,
        columns,
        target="outcome",
        categorical=["homeTeamID", "awayTeamID"],
        notrain=["id", "inOT", "datePlayed"],
    ):
        self.columns = columns
        self.target = target
        self.categorical = categorical
        self.notrain = notrain
        self.inputs = [column for column in columns if column not in [target] + notrain]

    def get_noscale_columns(self):
        return [self.target] + self.categorical + self.notrain

    def get_scale_columns(self):
        noscale_columns = self.get_noscale_columns()
        return [column for column in self.inputs if column not in noscale_columns]


class ZamboniDataManager:
    """Manages data for NN training"""

    def __init__(self, data_path):
        self.data_path = data_path
        self.is_split = 0

    def load_parquet(self):
        """
        Read data from parquet file into dataframe
        """
        data = pd.read_parquet(self.data_path)
        data = data[data["homeTeamID"] != -1]
        data = data[data["awayTeamID"] != -1]
        self.data = data

    def split_data(self, test_size=0.2, random_state=42):
        """
        Split into train and test sets

        param: test_size: Percentage of dataset for testing
        param: random_state: Seed for randomizing
        """
        self.train_data, self.test_data = train_test_split(
            self.data, test_size=test_size, random_state=random_state, shuffle=False
        )

    def num_samples(self):
        return len(self.data)


class ZamboniData:
    """One set of data for training or eval"""

    def __init__(self, data, column_tracker=None):
        self.data = data[data["homeTeamID"] != -1]
        self.data = self.data[self.data["awayTeamID"] != -1]
        if not column_tracker:
            self.column_tracker = ColumnTracker(data.columns.tolist())
        else:
            self.column_tracker = column_tracker

    def define_columns(
        self,
        target_column="outcome",
        categorical_columns=["homeTeamID", "awayTeamID"],
        nonet_columns=["datePlayed"],
    ):
        """
        Define which column is the label and which will use categorical embedding

        param: target_column: Column holding labels
        param: categorical_columns: Columns for categorical embedding
        param: nonet_columns: Columns to not pass to network
        """
        self.all_columns = self.data.columns.tolist()
        self.target_column = target_column
        self.categorical_columns = categorical_columns
        self.noscale_columns = [self.target_column] + self.categorical_columns
        self.nonet_columns = nonet_columns

    def select_by_date(self, begin_date, end_date, filter_column="datePlayed"):
        """
        Filter data by date in sequential training

        param: date: Date of games to select
        """
        datetime_column = pd.to_datetime(self.data[filter_column])
        begin_date = pd.to_datetime(begin_date).strftime("%Y-%m-%d")
        end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")
        begin_mask = datetime_column >= begin_date
        end_mask = datetime_column <= end_date
        mask = begin_mask & end_mask
        date_data = self.data[mask]
        return ZamboniData(date_data, self.column_tracker)

    def scale_data(self, scaler=None, fit=False, transform=True):
        """
        Scale with provided scaler or use StandardScaler as default

        param: scaler: Scaler class
        """
        if not scaler:
            self.scaler = StandardScaler()
        else:
            self.scaler = scaler
        scale_columns = self.column_tracker.get_scale_columns()
        if fit and transform:
            features = self.scaler.fit_transform(self.data[scale_columns])
        elif fit:
            features = self.scaler.fit(self.data[scale_columns])
        elif transform:
            features = self.scaler.transform(self.data[scale_columns])

        # Recast as DataFrames
        self.data_scaled = pd.DataFrame(features, columns=scale_columns)

    def readd_noscale_columns(self):
        """
        Add back columns that were not scaled
        """
        noscale_columns = self.column_tracker.get_noscale_columns()
        for column in noscale_columns:
            if column in self.column_tracker.notrain:
                continue
            self.data_scaled[column] = self.data[column].values

    # def create_dataset(self):
    #    """
    #    Create dataset
    #    """
    #    target_column = self.column_tracker.target
    #    categorical_columns = self.column_tracker.categorical
    #    notrain_columns = self.column_tracker.notrain
    #    self.dataset = ZamboniDataset(
    #        self.data_scaled, target_column, categorical_columns, notrain_columns
    #    )
    #    logger.debug(f"{len(self.dataset)} samples")

    # def create_dataloader(self, shuffle=False):
    #    """
    #    Create dataloader
    #    """
    #    self.loader = DataLoader(self.dataset, batch_size=32, shuffle=shuffle)

    def prep_data(self, scaler=None, fit=False, transform=True, shuffle=False):
        """
        Scale data and create dataset and dataloader

        param: scaler: Scaler class
        param: fit: Fit scaler to data
        param: transform: Transform data with scaler
        param: shuffle: Shuffle data
        """
        self.scale_data(scaler=scaler, fit=fit, transform=transform)
        self.readd_noscale_columns()
        #self.create_dataset()
        #self.create_dataloader(shuffle=shuffle)
