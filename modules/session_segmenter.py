import pandas as pd


class SessionSegmenter:
    """
    Splits a rowing workout into continuous rowing segments.

    Every stroke is also assigned a SessionPhase:

    - "Rowing segment"
    - "Short rowing segment"
    - "Transition/Cooldown"

    Transition and cooldown strokes do not receive a SessionSegment
    number, so they are excluded from fatigue analysis.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        minimum_speed: float = 1.0,
        minimum_stroke_rate: float = 10.0,
        maximum_time_gap: float = 8.0,
        minimum_segment_strokes: int = 10,
        minimum_analysis_strokes: int = 120,
    ):
        self.df = dataframe.copy()

        self.minimum_speed = minimum_speed
        self.minimum_stroke_rate = minimum_stroke_rate
        self.maximum_time_gap = maximum_time_gap
        self.minimum_segment_strokes = (
            minimum_segment_strokes
        )
        self.minimum_analysis_strokes = (
            minimum_analysis_strokes
        )

    def validate_required_columns(self):
        """
        Confirm that the dataframe contains the columns required
        for session segmentation.
        """

        required_columns = {
            "StrokeNumber",
            "Time",
            "Distance",
            "Speed",
            "StrokeRate",
        }

        missing_columns = (
            required_columns
            - set(self.df.columns)
        )

        if missing_columns:
            missing_text = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "Session segmentation cannot run because "
                f"these columns are missing: {missing_text}"
            )

        return self

    def calculate_time_gap(self):
        """
        Calculate the elapsed time between consecutive stroke rows.
        """

        self.df["TimeGap"] = (
            pd.to_numeric(
                self.df["Time"],
                errors="coerce",
            )
            .diff()
            .fillna(0.0)
        )

        return self

    def identify_rowing_rows(self):
        """
        A row counts as active rowing when both speed and stroke rate
        meet their minimum thresholds.
        """

        speed = pd.to_numeric(
            self.df["Speed"],
            errors="coerce",
        )

        stroke_rate = pd.to_numeric(
            self.df["StrokeRate"],
            errors="coerce",
        )

        self.df["IsRowing"] = (
            speed.ge(self.minimum_speed)
            & stroke_rate.ge(
                self.minimum_stroke_rate
            )
        ).fillna(False)

        return self

    def assign_candidate_segments(self):
        """
        Assign temporary segment numbers.

        A new candidate segment begins when:

        - rowing begins for the first time;
        - rowing resumes after a non-rowing row; or
        - a large time gap occurs.

        Non-rowing rows are initially left without a segment.
        """

        segment_number = 0
        previous_row_was_rowing = False
        candidate_segments = []

        for _, row in self.df.iterrows():
            is_rowing = bool(
                row["IsRowing"]
            )

            if not is_rowing:
                candidate_segments.append(
                    pd.NA
                )

                previous_row_was_rowing = False
                continue

            time_gap = row["TimeGap"]

            large_time_gap = (
                pd.notna(time_gap)
                and time_gap
                > self.maximum_time_gap
            )

            resumed_after_interruption = (
                not previous_row_was_rowing
            )

            if (
                segment_number == 0
                or large_time_gap
                or resumed_after_interruption
            ):
                segment_number += 1

            candidate_segments.append(
                segment_number
            )

            previous_row_was_rowing = True

        self.df["CandidateSegment"] = (
            pd.array(
                candidate_segments,
                dtype="Int64",
            )
        )

        return self

    def identify_valid_segments(self):
        """
        Determine which candidate segments contain enough strokes
        to count as genuine rowing segments.

        Very short groups are treated as transitions, turns,
        isolated strokes, or GPS artifacts.
        """

        candidate_counts = (
            self.df
            .dropna(
                subset=["CandidateSegment"]
            )
            .groupby("CandidateSegment")
            .size()
        )

        valid_segment_numbers = (
            candidate_counts[
                candidate_counts
                >= self.minimum_segment_strokes
            ]
            .index
            .tolist()
        )

        self.df["SessionSegment"] = (
            self.df["CandidateSegment"]
            .where(
                self.df[
                    "CandidateSegment"
                ].isin(
                    valid_segment_numbers
                )
            )
            .astype("Int64")
        )

        return self

    def renumber_segments(self):
        """
        Renumber valid segments consecutively as 1, 2, 3, and so on.
        """

        segment_numbers = sorted(
            self.df["SessionSegment"]
            .dropna()
            .unique()
            .tolist()
        )

        mapping = {
            old_number: new_number
            for new_number, old_number
            in enumerate(
                segment_numbers,
                start=1,
            )
        }

        self.df["SessionSegment"] = (
            self.df["SessionSegment"]
            .map(mapping)
            .astype("Int64")
        )

        return self

    def classify_session_phases(self):
        """
        Assign a descriptive classification to every stroke.

        Long segments are classified as "Rowing segment".

        Valid segments shorter than the fatigue detector's analysis
        minimum are classified as "Short rowing segment".

        All remaining rows are classified as
        "Transition/Cooldown".
        """

        self.df["SessionPhase"] = (
            "Transition/Cooldown"
        )

        segment_counts = (
            self.df
            .dropna(
                subset=["SessionSegment"]
            )
            .groupby("SessionSegment")
            .size()
        )

        for (
            segment_number,
            stroke_count,
        ) in segment_counts.items():
            if (
                stroke_count
                >= self.minimum_analysis_strokes
            ):
                phase_name = (
                    "Rowing segment"
                )
            else:
                phase_name = (
                    "Short rowing segment"
                )

            segment_mask = (
                self.df["SessionSegment"]
                == segment_number
            )

            self.df.loc[
                segment_mask,
                "SessionPhase",
            ] = phase_name

        return self

    def remove_temporary_columns(self):
        """
        Remove internal segmentation columns that are no longer needed.
        """

        self.df = self.df.drop(
            columns=[
                "CandidateSegment",
            ],
            errors="ignore",
        )

        return self

    def summarize_segments(self):
        """
        Create one summary row for every valid rowing segment.

        Transition/cooldown strokes are intentionally excluded because
        they do not represent a continuous rowing effort.
        """

        rowing_df = self.df.dropna(
            subset=["SessionSegment"]
        ).copy()

        summary_columns = [
            "SessionSegment",
            "SegmentType",
            "Strokes",
            "StartStroke",
            "EndStroke",
            "StartTime",
            "EndTime",
            "DurationSeconds",
            "StartDistance",
            "EndDistance",
            "SegmentDistance",
        ]

        if rowing_df.empty:
            return pd.DataFrame(
                columns=summary_columns
            )

        summary = (
            rowing_df
            .groupby(
                "SessionSegment",
                dropna=False,
            )
            .agg(
                SegmentType=(
                    "SessionPhase",
                    "first",
                ),
                Strokes=(
                    "StrokeNumber",
                    "count",
                ),
                StartStroke=(
                    "StrokeNumber",
                    "min",
                ),
                EndStroke=(
                    "StrokeNumber",
                    "max",
                ),
                StartTime=(
                    "Time",
                    "min",
                ),
                EndTime=(
                    "Time",
                    "max",
                ),
                StartDistance=(
                    "Distance",
                    "min",
                ),
                EndDistance=(
                    "Distance",
                    "max",
                ),
            )
            .reset_index()
        )

        summary["DurationSeconds"] = (
            summary["EndTime"]
            - summary["StartTime"]
        )

        summary["SegmentDistance"] = (
            summary["EndDistance"]
            - summary["StartDistance"]
        )

        return summary[
            summary_columns
        ]

    def run(self):
        """
        Run the complete session-segmentation process.
        """

        (
            self
            .validate_required_columns()
            .calculate_time_gap()
            .identify_rowing_rows()
            .assign_candidate_segments()
            .identify_valid_segments()
            .renumber_segments()
            .classify_session_phases()
            .remove_temporary_columns()
        )

        segment_summary = (
            self.summarize_segments()
        )

        return self.df, segment_summary