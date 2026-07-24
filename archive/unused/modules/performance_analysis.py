import pandas as pd


class PerformanceAnalyzer:

    def __init__(self, stroke_df):

        self.df = stroke_df.copy()

    def calculate_efficiency(self):

        self.df["Efficiency"] = (
            self.df["MeanSpeed"] /
            self.df["SpeedLoss"]
        )

        return self

    def calculate_consistency(self):

        avg = self.df["MeanSpeed"].mean()

        self.df["Consistency"] = (
            100
            - abs(
                self.df["MeanSpeed"] - avg
            ) / avg * 100
        )

        return self

    def detect_fatigue(self):

        baseline = self.df["MeanSpeed"].iloc[:20].mean()

        self.df["Fatigue"] = (
            (baseline - self.df["MeanSpeed"])
            / baseline
            * 100
        )

        return self

    def summarize(self):

        return pd.DataFrame({

            "Average Efficiency":
            [self.df["Efficiency"].mean()],

            "Average Consistency":
            [self.df["Consistency"].mean()],

            "Maximum Fatigue (%)":
            [self.df["Fatigue"].max()]

        })

    def get_dataframe(self):

        return self.df
    
    def strongest_stroke(self):

        idx = self.df["PowerPeak"].idxmax()

        return self.df.loc[idx]


    def weakest_stroke(self):

        idx = self.df["PowerPeak"].idxmin()

        return self.df.loc[idx]