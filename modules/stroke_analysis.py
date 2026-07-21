import pandas as pd

from modules.stroke import Stroke


class StrokeAnalyzer:

    def __init__(self, dataframe, peaks):

        self.df = dataframe

        self.peaks = peaks

        self.strokes = []

    def analyze(self):

        if len(self.peaks) < 2:

            return []

        for i in range(len(self.peaks) - 1):

            start = self.peaks[i]

            end = self.peaks[i + 1]

            segment = self.df.iloc[start:end]

            if len(segment) < 5:

                continue

            stroke = Stroke(

                number=i + 1,

                start_time=segment["Time"].iloc[0],

                end_time=segment["Time"].iloc[-1],

                duration=segment["Time"].iloc[-1]
                - segment["Time"].iloc[0],

                peak_speed=segment["SmoothSpeed"].max(),

                min_speed=segment["SmoothSpeed"].min(),

                mean_speed=segment["SmoothSpeed"].mean(),

                peak_acceleration=segment["Acceleration"].max(),

                peak_jerk=segment["Jerk"].max(),

                speed_loss=
                segment["SmoothSpeed"].max()
                - segment["SmoothSpeed"].min()

            )

            self.strokes.append(stroke)

        return self.strokes

    def to_dataframe(self):

        rows = []

        for s in self.strokes:

            rows.append({

                "Stroke": s.number,

                "Duration": s.duration,

                "PeakSpeed": s.peak_speed,

                "MinimumSpeed": s.min_speed,

                "MeanSpeed": s.mean_speed,

                "PeakAcceleration": s.peak_acceleration,

                "PeakJerk": s.peak_jerk,

                "SpeedLoss": s.speed_loss,

                "PowerMean":
                segment["Power"].mean(),

                "PowerPeak":
                segment["Power"].max(),

                "Energy":
                segment["KineticEnergy"].mean(),

                "Drag":
                segment["DragForce"].mean()

            })

        return pd.DataFrame(rows)