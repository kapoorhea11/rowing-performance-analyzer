import pandas as pd


class DataStandardizer:

    """
    Converts raw SpeedCoach data into
    the standard format used throughout the project.
    """

    NUMERIC_COLUMNS = [

    "Distance",
    "Speed",
    "StrokeRate",
    "StrokeNumber",
    "DistancePerStroke",
    "HeartRate",
    "Power"

]

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def convert_time(self):

        self.df["Time"] = pd.to_timedelta(
            self.df["Time"]
        ).dt.total_seconds()

        return self

    def convert_numeric(self):

        for column in self.NUMERIC_COLUMNS:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(

                    self.df[column],

                    errors="coerce"

                )

        return self

    def remove_empty_columns(self):

        self.df = self.df.dropna(

            axis=1,

            how="all"

        )

        return self

    def get_dataframe(self):

        return self.df