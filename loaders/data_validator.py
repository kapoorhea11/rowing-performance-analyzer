import pandas as pd


class DataValidator:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def check_required_columns(self, required):

        missing = []

        for column in required:

            if column not in self.df.columns:
                missing.append(column)

        if missing:

            raise ValueError(
                f"Missing required columns: {missing}"
            )

        return self

    def remove_duplicate_rows(self):

        self.df = self.df.drop_duplicates()

        return self

    def sort_by_time(self):

        if "Time" in self.df.columns:

            self.df = self.df.sort_values("Time")

        return self

    def reset_index(self):

        self.df = self.df.reset_index(drop=True)

        return self

    def get_dataframe(self):

        return self.df