import numpy as np

from config.settings import BOAT_MASS


class PowerAnalyzer:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def calculate_power(self):

        self.df["Power"] = (
            BOAT_MASS
            * self.df["Acceleration"]
            * self.df["SmoothSpeed"]
        )

        return self

    def calculate_drag_power(self):

        self.df["DragPower"] = (
            self.df["DragForce"]
            * self.df["SmoothSpeed"]
        )

        return self

    def calculate_work(self):

        dt = np.gradient(self.df["Time"])

        self.df["Work"] = (
            self.df["Power"] * dt
        ).cumsum()

        return self

    def calculate_energy_loss(self):

        self.df["EnergyLoss"] = (
            self.df["DragPower"]
            * np.gradient(self.df["Time"])
        ).cumsum()

        return self

    def get_dataframe(self):

        return self.df