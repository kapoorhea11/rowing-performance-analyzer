import numpy as np
import pandas as pd


class RealStrokeAnalyzer:
    """
    Computes coach-friendly metrics from SpeedCoach per-stroke data.

    Each input row already represents one stroke, so no peak detection
    or waveform segmentation is required.
    """

    REQUIRED_COLUMNS = [
        "Time",
        "Speed",
        "StrokeRate",
        "StrokeNumber",
        "DistancePerStroke",
    ]

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    def validate(self):
        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in self.df.columns
        ]

        if missing:
            raise ValueError(
                f"SpeedCoach data is missing required columns: {missing}"
            )

        return self

    def remove_invalid_rows(self):
        """
        Remove rows that cannot represent usable strokes.
        The first few strokes may contain startup artifacts, so extreme
        stroke rates and nonpositive values are excluded.
        """
        self.df = self.df.dropna(
            subset=self.REQUIRED_COLUMNS
        ).copy()

        self.df = self.df[
            (self.df["Speed"] > 0)
            & (self.df["StrokeRate"].between(8, 60))
            & (self.df["DistancePerStroke"] > 0)
        ].copy()

        self.df = self.df.sort_values("StrokeNumber")
        self.df = self.df.reset_index(drop=True)

        return self

    def calculate_stroke_duration(self):
        """
        Prefer duration inferred from stroke rate:
            duration = 60 / strokes per minute

        This is more stable than differencing rounded elapsed timestamps.
        """
        self.df["StrokeDuration"] = 60.0 / self.df["StrokeRate"]

        return self

    def calculate_speed_change(self):
        """
        Change in measured average boat speed from the previous stroke.

        This is not true within-stroke speed loss because the CSV has only
        one summarized value per stroke.
        """
        self.df["SpeedChange"] = self.df["Speed"].diff()

        return self

    def calculate_rolling_metrics(self, window: int = 10):
        """
        Rolling values reduce GPS noise and reveal longer trends.
        """
        min_periods = max(3, window // 2)

        self.df["RollingSpeed"] = (
            self.df["Speed"]
            .rolling(window, min_periods=min_periods)
            .mean()
        )

        self.df["RollingDistancePerStroke"] = (
            self.df["DistancePerStroke"]
            .rolling(window, min_periods=min_periods)
            .mean()
        )

        self.df["RollingStrokeRate"] = (
            self.df["StrokeRate"]
            .rolling(window, min_periods=min_periods)
            .mean()
        )

        self.df["SpeedConsistency"] = (
            self.df["Speed"]
            .rolling(window, min_periods=min_periods)
            .std()
        )

        return self

    def create_output(self):
        """
        Return only the columns used by the focused coach-facing system.
        """
        preferred_columns = [
            "StrokeNumber",
            "Time",
            "Distance",
            "Speed",
            "StrokeRate",
            "DistancePerStroke",
            "StrokeDuration",
            "SpeedChange",
            "RollingSpeed",
            "RollingDistancePerStroke",
            "RollingStrokeRate",
            "SpeedConsistency",
        ]

        available_columns = [
            column
            for column in preferred_columns
            if column in self.df.columns
        ]

        return self.df[available_columns].copy()

    def run(self):
        return (
            self.validate()
            .remove_invalid_rows()
            .calculate_stroke_duration()
            .calculate_speed_change()
            .calculate_rolling_metrics()
            .create_output()
        )