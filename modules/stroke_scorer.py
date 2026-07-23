import numpy as np
import pandas as pd


class StrokeScorer:
    """
    Produces a 0-to-100 relative stroke-quality score.

    The score compares each stroke with the athlete's own
    early-session baseline.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        baseline_start_index: int,
        baseline_end_index: int,
    ):
        self.df = dataframe.copy()

        self.baseline_start_index = baseline_start_index
        self.baseline_end_index = baseline_end_index

        self.baseline_speed = None
        self.baseline_distance_per_stroke = None
        self.baseline_stroke_rate = None
        self.baseline_speed_consistency = None

    def calculate_baselines(self):
        baseline = self.df.iloc[
            self.baseline_start_index:self.baseline_end_index
        ].copy()

        baseline = baseline.dropna(
            subset=[
                "RollingSpeed",
                "RollingDistancePerStroke",
                "RollingStrokeRate",
            ]
        )

        if baseline.empty:
            raise ValueError(
                "Not enough valid baseline data to calculate scores."
            )

        self.baseline_speed = float(
            baseline["RollingSpeed"].median()
        )

        self.baseline_distance_per_stroke = float(
            baseline["RollingDistancePerStroke"].median()
        )

        self.baseline_stroke_rate = float(
            baseline["RollingStrokeRate"].median()
        )

        valid_consistency = baseline[
            "SpeedConsistency"
        ].dropna()

        if valid_consistency.empty:
            self.baseline_speed_consistency = float(
                self.df["Speed"].std()
            )
        else:
            self.baseline_speed_consistency = float(
                valid_consistency.median()
            )

        return self

    def calculate_speed_score(self):
        """
        Full credit at or above baseline speed.

        Score decreases gradually as speed falls below baseline.
        A 20% drop produces approximately zero for this component.
        """

        speed_ratio = (
            self.df["RollingSpeed"]
            / self.baseline_speed
        )

        self.df["SpeedScore"] = (
            100
            * (speed_ratio - 0.80)
            / 0.20
        ).clip(
            lower=0,
            upper=100,
        )

        return self

    def calculate_distance_score(self):
        """
        Full credit at or above baseline distance per stroke.

        A 20% decline produces approximately zero.
        """

        distance_ratio = (
            self.df["RollingDistancePerStroke"]
            / self.baseline_distance_per_stroke
        )

        self.df["DistancePerStrokeScore"] = (
            100
            * (distance_ratio - 0.80)
            / 0.20
        ).clip(
            lower=0,
            upper=100,
        )

        return self

    def calculate_rhythm_score(self):
        """
        Penalize large stroke-rate deviations from baseline.

        Small changes are allowed because rowing rate naturally varies.
        """

        rate_difference = (
            self.df["RollingStrokeRate"]
            - self.baseline_stroke_rate
        ).abs()

        rate_difference_fraction = (
            rate_difference
            / self.baseline_stroke_rate
        )

        self.df["RhythmScore"] = (
            100
            * (
                1
                - rate_difference_fraction / 0.20
            )
        ).clip(
            lower=0,
            upper=100,
        )

        return self

    def calculate_consistency_score(self):
        """
        Reward stable speed from stroke to stroke.

        Lower rolling standard deviation is better.
        """

        reference = max(
            self.baseline_speed_consistency,
            0.01,
        )

        consistency_ratio = (
            self.df["SpeedConsistency"]
            / reference
        )

        self.df["ConsistencyScore"] = (
            100
            * (
                1
                - (consistency_ratio - 1) / 2
            )
        ).clip(
            lower=0,
            upper=100,
        )

        self.df["ConsistencyScore"] = (
            self.df["ConsistencyScore"]
            .fillna(100)
        )

        return self

    def calculate_total_score(self):
        self.df["StrokeScore"] = (
            0.35 * self.df["SpeedScore"]
            + 0.35 * self.df["DistancePerStrokeScore"]
            + 0.15 * self.df["RhythmScore"]
            + 0.15 * self.df["ConsistencyScore"]
        )

        self.df["StrokeScore"] = (
            self.df["StrokeScore"]
            .clip(
                lower=0,
                upper=100,
            )
            .round(1)
        )

        return self

    def calculate_session_score(self):
        """
        Exclude startup strokes from the session average.
        """

        scoring_data = self.df.iloc[
            self.baseline_start_index:
        ]

        return float(
            scoring_data["StrokeScore"].mean()
        )

    def run(self):
        required_columns = [
            "RollingSpeed",
            "RollingDistancePerStroke",
            "RollingStrokeRate",
            "SpeedConsistency",
        ]

        missing = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing:
            raise ValueError(
                f"Stroke scoring is missing columns: {missing}"
            )

        (
            self.calculate_baselines()
            .calculate_speed_score()
            .calculate_distance_score()
            .calculate_rhythm_score()
            .calculate_consistency_score()
            .calculate_total_score()
        )

        session_score = self.calculate_session_score()

        return self.df, session_score