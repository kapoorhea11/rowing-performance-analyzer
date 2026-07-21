import numpy as np


class BiomechanicsAnalyzer:

    def __init__(self, dataframe, peaks):

        self.df = dataframe
        self.peaks = peaks

    def calculate_boatrun(self):

        boat_runs = []

        for i in range(len(self.peaks) - 1):

            start = self.peaks[i]
            end = self.peaks[i + 1]

            segment = self.df.iloc[start:end]

            dt = np.gradient(segment["Time"])

            distance = np.sum(
                segment["SmoothSpeed"] * dt
            )

            boat_runs.append(distance)

        return boat_runs

    def calculate_speed_loss(self):

        losses = []

        for i in range(len(self.peaks) - 1):

            start = self.peaks[i]
            end = self.peaks[i + 1]

            segment = self.df.iloc[start:end]

            losses.append(

                segment["SmoothSpeed"].max()

                -

                segment["SmoothSpeed"].min()

            )

        return losses

    def calculate_peak_acceleration(self):

        peaks = []

        for i in range(len(self.peaks)-1):

            segment = self.df.iloc[
                self.peaks[i]:
                self.peaks[i+1]
            ]

            peaks.append(

                segment["Acceleration"].max()

            )

        return peaks