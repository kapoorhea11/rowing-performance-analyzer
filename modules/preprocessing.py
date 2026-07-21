import numpy as np
from scipy.signal import savgol_filter

from config.settings import (
    SMOOTHING_WINDOW,
    SMOOTHING_POLYORDER,
)


class DataPreprocessor:
    """
    Cleans and processes rowing speed data.
    """

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def interpolate_missing(self):
        """
        Fill missing values using linear interpolation.
        """
        self.df = self.df.interpolate(method="linear")
        return self

    def smooth_speed(self):
        """
        Smooth the speed signal using a Savitzky-Golay filter.
        """
        self.df["SmoothSpeed"] = savgol_filter(
            self.df["Speed"],
            window_length=SMOOTHING_WINDOW,
            polyorder=SMOOTHING_POLYORDER,
        )
        return self

    def calculate_acceleration(self):
        """
        Calculate acceleration from smoothed speed.
        """
        self.df["Acceleration"] = np.gradient(
            self.df["SmoothSpeed"],
            self.df["Time"],
        )
        return self

    def calculate_jerk(self):
        """
        Calculate jerk from acceleration.
        """
        self.df["Jerk"] = np.gradient(
            self.df["Acceleration"],
            self.df["Time"],
        )
        return self

    def get_dataframe(self):
        return self.df