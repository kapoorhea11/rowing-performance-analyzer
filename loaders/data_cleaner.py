import numpy as np


class DataCleaner:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def remove_negative_speed(self):

        if "Speed" in self.df.columns:

            self.df.loc[
                self.df["Speed"] < 0,
                "Speed"
            ] = np.nan

        return self

    def interpolate(self):

        self.df = self.df.interpolate()

        return self

    def clip_speed(self, maximum=9):

        if "Speed" in self.df.columns:

            self.df["Speed"] = self.df["Speed"].clip(
                lower=0,
                upper=maximum
            )

        return self

    def get_dataframe(self):

        return self.df