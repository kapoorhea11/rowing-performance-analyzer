import numpy as np
import pandas as pd

from config.settings import BOAT_MASS, TRUE_DRAG


class PhysicsAnalyzer:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def calculate_momentum(self):

        self.df["Momentum"] = (
            BOAT_MASS *
            self.df["SmoothSpeed"]
        )

        return self

    def calculate_kinetic_energy(self):

        self.df["KineticEnergy"] = (
            0.5 *
            BOAT_MASS *
            self.df["SmoothSpeed"] ** 2
        )

        return self

    def calculate_drag_force(self):

        self.df["DragForce"] = (
            TRUE_DRAG *
            self.df["SmoothSpeed"] ** 2
        )

        return self

    def calculate_deceleration(self):

        self.df["Deceleration"] = np.minimum(
            self.df["Acceleration"],
            0
        )

        return self

    def calculate_glide_distance(self):

        dt = np.gradient(self.df["Time"])

        self.df["GlideDistance"] = (
            self.df["SmoothSpeed"] * dt
        ).cumsum()

        return self

    def get_dataframe(self):

        return self.df