import pandas as pd

from loaders.data_validator import DataValidator
from loaders.data_cleaner import DataCleaner


class SpeedCoachLoader:

    def __init__(self, filename):

        self.filename = filename

    def load(self):

        df = pd.read_csv(self.filename)

        validator = (
            DataValidator(df)
            .remove_duplicate_rows()
            .sort_by_time()
            .reset_index()
        )

        df = validator.get_dataframe()

        cleaner = (
            DataCleaner(df)
            .remove_negative_speed()
            .interpolate()
            .clip_speed()
        )

        return cleaner.get_dataframe()