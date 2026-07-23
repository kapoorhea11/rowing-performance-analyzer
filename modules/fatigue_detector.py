import numpy as np
import pandas as pd

from config.fatigue_config import FATIGUE_CONFIG


class FatigueDetector:
    """
    Detect sustained performance decline independently within
    each continuous rowing segment.

    The detector compares each segment with its own early baseline.
    Fatigue signals do not carry across pauses or separate segments.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        config: dict = None,
    ):
        self.df = dataframe.copy()

        if config is None:
            self.config = FATIGUE_CONFIG.copy()
        else:
            self.config = config.copy()

        self.startup_strokes = self.config[
            "startup_strokes"
        ]

        self.baseline_strokes = self.config[
            "baseline_strokes"
        ]

        self.minimum_segment_strokes = self.config[
            "minimum_segment_strokes"
        ]

        self.confirmation_strokes = self.config[
            "confirmation_strokes"
        ]

        self.speed_decline_threshold = self.config[
            "speed_decline_threshold"
        ]

        self.distance_decline_threshold = self.config[
            "distance_per_stroke_decline_threshold"
        ]

        self.stroke_rate_change_threshold = self.config[
            "stroke_rate_change_threshold"
        ]

        self.high_confidence_signal_strokes = self.config[
            "high_confidence_signal_strokes"
        ]

        self.high_confidence_decline_multiplier = self.config[
            "high_confidence_decline_multiplier"
        ]

    def validate_columns(self):
        """
        Confirm that all columns required for fatigue analysis exist.
        """

        required_columns = [
            "StrokeNumber",
            "Time",
            "Distance",
            "RollingSpeed",
            "RollingDistancePerStroke",
            "RollingStrokeRate",
            "SessionSegment",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Fatigue detection is missing required columns: "
                f"{missing_columns}"
            )

        return self

    def initialize_output_columns(self):
        """
        Create all fatigue-analysis columns before segment processing.
        """

        self.df["SpeedDecline"] = np.nan
        self.df["DistancePerStrokeDecline"] = np.nan
        self.df["StrokeRateChange"] = np.nan

        self.df["FatigueSignal"] = False
        self.df["FatigueConfirmed"] = False
        self.df["FatigueSeverity"] = 0.0

        return self

    def get_segment_data(
        self,
        segment_number,
    ):
        """
        Return one segment while preserving the original DataFrame index.
        """

        segment_df = self.df.loc[
            self.df["SessionSegment"] == segment_number
        ].copy()

        return segment_df

    def create_skipped_summary(
        self,
        segment_number,
        segment_df,
        reason,
    ):
        """
        Create a standard result for a segment that cannot be analyzed.
        """

        return {
            "segment": int(segment_number),
            "strokes": int(len(segment_df)),
            "analyzed": False,
            "reason": reason,
            "fatigue_detected": False,
            "fatigue_start_stroke": None,
            "fatigue_start_time": None,
            "fatigue_start_distance": None,
            "maximum_fatigue_severity": 0.0,
            "baseline_start_stroke": None,
            "baseline_end_stroke": None,
            "baseline_start_index": None,
            "baseline_end_index": None,
            "confidence_score": None,
            "confidence_rating": "Not analyzed",
            "signal_agreement_score": None,
            "signal_duration_score": None,
            "decline_magnitude_score": None,
            "stroke_rate_stability_score": None,
            "longest_signal_run": 0,
        }

    def calculate_segment_baseline(
        self,
        segment_df,
    ):
        """
        Calculate an early-segment baseline after startup strokes.

        Medians are used because they are less sensitive to isolated
        unusual strokes than means.
        """

        baseline_start_position = self.startup_strokes

        baseline_end_position = (
            baseline_start_position
            + self.baseline_strokes
        )

        baseline_df = segment_df.iloc[
            baseline_start_position:baseline_end_position
        ].copy()

        baseline_df = baseline_df.dropna(
            subset=[
                "RollingSpeed",
                "RollingDistancePerStroke",
                "RollingStrokeRate",
            ]
        )

        if baseline_df.empty:
            return None

        baseline_speed = float(
            baseline_df["RollingSpeed"].median()
        )

        baseline_distance_per_stroke = float(
            baseline_df[
                "RollingDistancePerStroke"
            ].median()
        )

        baseline_stroke_rate = float(
            baseline_df["RollingStrokeRate"].median()
        )

        if (
            baseline_speed <= 0
            or baseline_distance_per_stroke <= 0
            or baseline_stroke_rate <= 0
        ):
            return None

        return {
            "speed": baseline_speed,
            "distance_per_stroke": baseline_distance_per_stroke,
            "stroke_rate": baseline_stroke_rate,
            "baseline_start_index": baseline_df.index[0],
            "baseline_end_index": baseline_df.index[-1],
            "baseline_start_stroke": int(
                baseline_df.iloc[0]["StrokeNumber"]
            ),
            "baseline_end_stroke": int(
                baseline_df.iloc[-1]["StrokeNumber"]
            ),
        }

    def calculate_declines(
        self,
        segment_df,
        baseline,
    ):
        """
        Calculate relative changes from the segment baseline.
        """

        speed_decline = (
            baseline["speed"]
            - segment_df["RollingSpeed"]
        ) / baseline["speed"]

        distance_decline = (
            baseline["distance_per_stroke"]
            - segment_df["RollingDistancePerStroke"]
        ) / baseline["distance_per_stroke"]

        stroke_rate_change = (
            segment_df["RollingStrokeRate"]
            - baseline["stroke_rate"]
        ).abs() / baseline["stroke_rate"]

        self.df.loc[
            segment_df.index,
            "SpeedDecline",
        ] = speed_decline

        self.df.loc[
            segment_df.index,
            "DistancePerStrokeDecline",
        ] = distance_decline

        self.df.loc[
            segment_df.index,
            "StrokeRateChange",
        ] = stroke_rate_change

        return self

    def calculate_segment_signals(
        self,
        segment_df,
        baseline,
    ):
        """
        Mark strokes where both speed and distance per stroke have
        declined beyond their thresholds.

        Stroke-rate change is retained as supporting information but
        is not required for a fatigue signal.
        """

        after_baseline = (
            segment_df.index
            > baseline["baseline_end_index"]
        )

        speed_declined = (
            self.df.loc[
                segment_df.index,
                "SpeedDecline",
            ]
            >= self.speed_decline_threshold
        )

        distance_declined = (
            self.df.loc[
                segment_df.index,
                "DistancePerStrokeDecline",
            ]
            >= self.distance_decline_threshold
        )

        fatigue_signal = (
            after_baseline
            & speed_declined
            & distance_declined
        )

        self.df.loc[
            segment_df.index,
            "FatigueSignal",
        ] = fatigue_signal.fillna(False)

        return self

    def confirm_segment_fatigue(
        self,
        segment_df,
        baseline,
    ):
        """
        Confirm fatigue only after the required number of consecutive
        fatigue signals.
        """

        fatigue_signal = (
            self.df.loc[
                segment_df.index,
                "FatigueSignal",
            ]
            .fillna(False)
            .astype(int)
        )

        consecutive_signal_count = fatigue_signal.rolling(
            window=self.confirmation_strokes,
            min_periods=self.confirmation_strokes,
        ).sum()

        fatigue_confirmed = (
            consecutive_signal_count
            >= self.confirmation_strokes
        )

        fatigue_confirmed.loc[
            fatigue_confirmed.index
            <= baseline["baseline_end_index"]
        ] = False

        self.df.loc[
            segment_df.index,
            "FatigueConfirmed",
        ] = fatigue_confirmed.fillna(False)

        return self

    def calculate_segment_severity(
        self,
        segment_df,
        baseline,
    ):
        """
        Calculate a zero-to-one decline-severity score.

        Severity combines speed decline and distance-per-stroke decline.
        It is set to zero unless fatigue has been confirmed.
        """

        speed_component = (
            self.df.loc[
                segment_df.index,
                "SpeedDecline",
            ]
            / (
                self.speed_decline_threshold
                * self.high_confidence_decline_multiplier
            )
        )

        distance_component = (
            self.df.loc[
                segment_df.index,
                "DistancePerStrokeDecline",
            ]
            / (
                self.distance_decline_threshold
                * self.high_confidence_decline_multiplier
            )
        )

        severity = (
            0.5 * speed_component
            + 0.5 * distance_component
        ).clip(
            lower=0.0,
            upper=1.0,
        )

        severity.loc[
            severity.index
            <= baseline["baseline_end_index"]
        ] = 0.0

        confirmed_mask = self.df.loc[
            segment_df.index,
            "FatigueConfirmed",
        ].fillna(False)

        severity.loc[
            ~confirmed_mask
        ] = 0.0

        self.df.loc[
            segment_df.index,
            "FatigueSeverity",
        ] = severity.fillna(0.0)

        return self

    def calculate_longest_signal_run(
        self,
        segment_df,
    ):
        """
        Return the longest consecutive run of fatigue-signal strokes.
        """

        fatigue_signal = (
            self.df.loc[
                segment_df.index,
                "FatigueSignal",
            ]
            .fillna(False)
            .astype(bool)
        )

        longest_run = 0
        current_run = 0

        for signal_value in fatigue_signal:
            if signal_value:
                current_run += 1
                longest_run = max(
                    longest_run,
                    current_run,
                )
            else:
                current_run = 0

        return int(longest_run)

    def calculate_segment_confidence(
        self,
        segment_df,
        baseline,
    ):
        """
        Calculate confidence that a sustained performance decline
        was detected.

        This confidence score is not the probability that the athlete
        experienced physiological fatigue. It reflects the strength
        and consistency of the SpeedCoach-data pattern.
        """

        analysis_indices = segment_df.index[
            segment_df.index
            > baseline["baseline_end_index"]
        ]

        if len(analysis_indices) == 0:
            return {
                "confidence_score": 0.0,
                "confidence_rating": "Insufficient data",
                "signal_agreement_score": 0.0,
                "signal_duration_score": 0.0,
                "decline_magnitude_score": 0.0,
                "stroke_rate_stability_score": 0.0,
                "longest_signal_run": 0,
            }

        speed_decline = self.df.loc[
            analysis_indices,
            "SpeedDecline",
        ].fillna(0.0).clip(lower=0.0)

        distance_decline = self.df.loc[
            analysis_indices,
            "DistancePerStrokeDecline",
        ].fillna(0.0).clip(lower=0.0)

        stroke_rate_change = self.df.loc[
            analysis_indices,
            "StrokeRateChange",
        ].fillna(0.0).clip(lower=0.0)

        fatigue_signal = self.df.loc[
            analysis_indices,
            "FatigueSignal",
        ].fillna(False)

        fatigue_confirmed = self.df.loc[
            analysis_indices,
            "FatigueConfirmed",
        ].fillna(False)

        signal_count = int(
            fatigue_signal.sum()
        )

        analysis_count = int(
            len(analysis_indices)
        )

        signal_agreement_score = (
            100.0
            * signal_count
            / max(analysis_count, 1)
        )

        longest_signal_run = (
            self.calculate_longest_signal_run(
                segment_df
            )
        )

        signal_duration_score = min(
            100.0,
            (
                100.0
                * longest_signal_run
                / max(
                    self.high_confidence_signal_strokes,
                    1,
                )
            ),
        )

        confirmed_indices = fatigue_confirmed[
            fatigue_confirmed
        ].index

        if len(confirmed_indices) > 0:
            mean_speed_decline = float(
                speed_decline.loc[
                    confirmed_indices
                ].mean()
            )

            mean_distance_decline = float(
                distance_decline.loc[
                    confirmed_indices
                ].mean()
            )

            mean_stroke_rate_change = float(
                stroke_rate_change.loc[
                    confirmed_indices
                ].mean()
            )
        else:
            mean_speed_decline = 0.0
            mean_distance_decline = 0.0
            mean_stroke_rate_change = 0.0

        target_speed_decline = (
            self.speed_decline_threshold
            * self.high_confidence_decline_multiplier
        )

        target_distance_decline = (
            self.distance_decline_threshold
            * self.high_confidence_decline_multiplier
        )

        speed_magnitude_score = min(
            100.0,
            (
                100.0
                * mean_speed_decline
                / max(
                    target_speed_decline,
                    0.001,
                )
            ),
        )

        distance_magnitude_score = min(
            100.0,
            (
                100.0
                * mean_distance_decline
                / max(
                    target_distance_decline,
                    0.001,
                )
            ),
        )

        decline_magnitude_score = (
            0.5 * speed_magnitude_score
            + 0.5 * distance_magnitude_score
        )

        stroke_rate_stability_score = max(
            0.0,
            min(
                100.0,
                (
                    100.0
                    * (
                        1.0
                        - (
                            mean_stroke_rate_change
                            / max(
                                self.stroke_rate_change_threshold,
                                0.001,
                            )
                        )
                    )
                ),
            ),
        )

        fatigue_detected = bool(
            fatigue_confirmed.any()
        )

        if fatigue_detected:
            confidence_score = (
                0.30 * signal_agreement_score
                + 0.30 * signal_duration_score
                + 0.30 * decline_magnitude_score
                + 0.10 * stroke_rate_stability_score
            )
        else:
            confidence_score = 0.0

        confidence_score = float(
            min(
                100.0,
                max(
                    0.0,
                    confidence_score,
                ),
            )
        )

        if not fatigue_detected:
            confidence_rating = "No confirmed decline"
        elif confidence_score >= 85.0:
            confidence_rating = "Very high"
        elif confidence_score >= 70.0:
            confidence_rating = "High"
        elif confidence_score >= 50.0:
            confidence_rating = "Moderate"
        else:
            confidence_rating = "Low"

        return {
            "confidence_score": round(
                confidence_score,
                1,
            ),
            "confidence_rating": confidence_rating,
            "signal_agreement_score": round(
                signal_agreement_score,
                1,
            ),
            "signal_duration_score": round(
                signal_duration_score,
                1,
            ),
            "decline_magnitude_score": round(
                decline_magnitude_score,
                1,
            ),
            "stroke_rate_stability_score": round(
                stroke_rate_stability_score,
                1,
            ),
            "longest_signal_run": longest_signal_run,
        }

    def summarize_segment(
        self,
        segment_number,
        segment_df,
        baseline,
    ):
        """
        Create the complete result for one analyzed segment.
        """

        confirmed_rows = self.df.loc[
            segment_df.index
        ].copy()

        confirmed_rows = confirmed_rows[
            confirmed_rows["FatigueConfirmed"]
        ]

        maximum_severity = float(
            self.df.loc[
                segment_df.index,
                "FatigueSeverity",
            ]
            .fillna(0.0)
            .max()
        )

        confidence = self.calculate_segment_confidence(
            segment_df=segment_df,
            baseline=baseline,
        )

        summary = {
            "segment": int(segment_number),
            "strokes": int(len(segment_df)),
            "analyzed": True,
            "reason": None,
            "fatigue_detected": False,
            "fatigue_start_stroke": None,
            "fatigue_start_time": None,
            "fatigue_start_distance": None,
            "maximum_fatigue_severity": maximum_severity,
            "baseline_start_stroke": baseline[
                "baseline_start_stroke"
            ],
            "baseline_end_stroke": baseline[
                "baseline_end_stroke"
            ],
            "baseline_start_index": baseline[
                "baseline_start_index"
            ],
            "baseline_end_index": (
                baseline["baseline_end_index"]
                + 1
            ),
            **confidence,
        }

        if confirmed_rows.empty:
            return summary

        first_confirmed = confirmed_rows.iloc[0]

        summary.update(
            {
                "fatigue_detected": True,
                "fatigue_start_stroke": int(
                    first_confirmed["StrokeNumber"]
                ),
                "fatigue_start_time": float(
                    first_confirmed["Time"]
                ),
                "fatigue_start_distance": float(
                    first_confirmed["Distance"]
                ),
            }
        )

        return summary

    def analyze_segment(
        self,
        segment_number,
    ):
        """
        Run fatigue analysis for one continuous rowing segment.
        """

        segment_df = self.get_segment_data(
            segment_number
        )

        if len(segment_df) < self.minimum_segment_strokes:
            return self.create_skipped_summary(
                segment_number=segment_number,
                segment_df=segment_df,
                reason=(
                    "Segment is shorter than the "
                    f"{self.minimum_segment_strokes}-stroke minimum."
                ),
            )

        required_length = (
            self.startup_strokes
            + self.baseline_strokes
            + self.confirmation_strokes
        )

        if len(segment_df) < required_length:
            return self.create_skipped_summary(
                segment_number=segment_number,
                segment_df=segment_df,
                reason=(
                    "Segment does not contain enough strokes for "
                    "startup, baseline, and fatigue confirmation."
                ),
            )

        baseline = self.calculate_segment_baseline(
            segment_df
        )

        if baseline is None:
            return self.create_skipped_summary(
                segment_number=segment_number,
                segment_df=segment_df,
                reason=(
                    "Segment does not contain enough valid rolling "
                    "data to calculate a baseline."
                ),
            )

        self.calculate_declines(
            segment_df=segment_df,
            baseline=baseline,
        )

        self.calculate_segment_signals(
            segment_df=segment_df,
            baseline=baseline,
        )

        self.confirm_segment_fatigue(
            segment_df=segment_df,
            baseline=baseline,
        )

        self.calculate_segment_severity(
            segment_df=segment_df,
            baseline=baseline,
        )

        return self.summarize_segment(
            segment_number=segment_number,
            segment_df=segment_df,
            baseline=baseline,
        )

    def create_overall_summary(
        self,
        segment_results,
    ):
        """
        Combine segment results while preserving the summary keys used
        by the scorer, coach report, graphs, exporter, and main program.
        """

        analyzed_results = [
            result
            for result in segment_results
            if result["analyzed"]
        ]

        fatigue_results = [
            result
            for result in analyzed_results
            if result["fatigue_detected"]
        ]

        if not analyzed_results:
            return {
                "fatigue_detected": False,
                "fatigue_start_stroke": None,
                "fatigue_start_time": None,
                "fatigue_start_distance": None,
                "maximum_fatigue_severity": 0.0,
                "baseline_start_stroke": None,
                "baseline_end_stroke": None,
                "baseline_start_index": 0,
                "baseline_end_index": min(
                    len(self.df),
                    1,
                ),
                "fatigue_segment": None,
                "fatigue_confidence": 0.0,
                "fatigue_confidence_rating": (
                    "Insufficient data"
                ),
                "segments_analyzed": 0,
                "segment_results": segment_results,
            }

        if fatigue_results:
            primary_result = min(
                fatigue_results,
                key=lambda result: (
                    result["fatigue_start_time"]
                ),
            )
        else:
            primary_result = max(
                analyzed_results,
                key=lambda result: result["strokes"],
            )

        maximum_severity = max(
            (
                result[
                    "maximum_fatigue_severity"
                ]
                for result in analyzed_results
            ),
            default=0.0,
        )

        return {
            "fatigue_detected": bool(
                fatigue_results
            ),
            "fatigue_start_stroke": (
                primary_result[
                    "fatigue_start_stroke"
                ]
                if fatigue_results
                else None
            ),
            "fatigue_start_time": (
                primary_result[
                    "fatigue_start_time"
                ]
                if fatigue_results
                else None
            ),
            "fatigue_start_distance": (
                primary_result[
                    "fatigue_start_distance"
                ]
                if fatigue_results
                else None
            ),
            "maximum_fatigue_severity": float(
                maximum_severity
            ),
            "baseline_start_stroke": primary_result[
                "baseline_start_stroke"
            ],
            "baseline_end_stroke": primary_result[
                "baseline_end_stroke"
            ],
            "baseline_start_index": primary_result[
                "baseline_start_index"
            ],
            "baseline_end_index": primary_result[
                "baseline_end_index"
            ],
            "fatigue_segment": (
                primary_result["segment"]
                if fatigue_results
                else None
            ),
            "fatigue_confidence": (
                primary_result["confidence_score"]
                if fatigue_results
                else 0.0
            ),
            "fatigue_confidence_rating": (
                primary_result["confidence_rating"]
                if fatigue_results
                else "No confirmed decline"
            ),
            "segments_analyzed": int(
                len(analyzed_results)
            ),
            "segment_results": segment_results,
        }

    def run(self):
        """
        Run segment-aware fatigue detection.
        """

        self.validate_columns()
        self.initialize_output_columns()

        segment_numbers = sorted(
            self.df["SessionSegment"]
            .dropna()
            .unique()
        )

        segment_results = []

        for segment_number in segment_numbers:
            segment_result = self.analyze_segment(
                segment_number
            )

            segment_results.append(
                segment_result
            )

        overall_summary = self.create_overall_summary(
            segment_results
        )

        return self.df, overall_summary