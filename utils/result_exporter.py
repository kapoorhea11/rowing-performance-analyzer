from pathlib import Path

import pandas as pd


class ResultExporter:
    """
    Exports detailed stroke data, a session summary,
    and a readable coach report.
    """

    def __init__(
        self,
        stroke_dataframe: pd.DataFrame,
        fatigue_summary: dict,
        session_score: float,
        coach_report: dict,
        data_directory: str = "outputs/data",
        report_directory: str = "outputs/reports",
    ):
        self.stroke_df = stroke_dataframe.copy()
        self.fatigue_summary = fatigue_summary
        self.session_score = float(session_score)
        self.coach_report = coach_report

        self.data_directory = Path(data_directory)
        self.report_directory = Path(report_directory)

        self.data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.report_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export_stroke_analysis(self):
        """
        Save one row per stroke with all calculated metrics.
        """

        output_path = (
            self.data_directory
            / "stroke_analysis.csv"
        )

        self.stroke_df.to_csv(
            output_path,
            index=False,
        )

        return output_path

    def create_session_summary(self):
        """
        Build a one-row summary of the complete session.
        """

        fatigue_start_stroke = self.fatigue_summary.get(
            "fatigue_start_stroke"
        )

        fatigue_start_time = self.fatigue_summary.get(
            "fatigue_start_time"
        )

        fatigue_start_distance = self.fatigue_summary.get(
            "fatigue_start_distance"
        )

        summary = {
            "ValidStrokes": len(self.stroke_df),

            "DurationSeconds": float(
                self.stroke_df["Time"].max()
            ),

            "DurationMinutes": float(
                self.stroke_df["Time"].max() / 60
            ),

            "DistanceMeters": float(
                self.stroke_df["Distance"].max()
            ),

            "AverageSpeedMetersPerSecond": float(
                self.stroke_df["Speed"].mean()
            ),

            "AverageStrokeRate": float(
                self.stroke_df["StrokeRate"].mean()
            ),

            "AverageDistancePerStroke": float(
                self.stroke_df[
                    "DistancePerStroke"
                ].mean()
            ),

            "AverageStrokeDurationSeconds": float(
                self.stroke_df[
                    "StrokeDuration"
                ].mean()
            ),

            "SessionScore": self.session_score,

            "SessionRating": self.coach_report.get(
                "session_rating"
            ),

            "StrongestArea": self.coach_report.get(
                "strongest_area"
            ),

            "StrongestAreaScore": self.coach_report.get(
                "strongest_area_score"
            ),

            "WeakestArea": self.coach_report.get(
                "weakest_area"
            ),

            "WeakestAreaScore": self.coach_report.get(
                "weakest_area_score"
            ),

            "FatigueDetected": self.fatigue_summary.get(
                "fatigue_detected",
                False,
            ),

            "FatigueConfidence": (
                self.fatigue_summary.get(
                    "fatigue_confidence",
                    0.0,
                )
            ),

            "FatigueConfidenceRating": (
                self.fatigue_summary.get(
                    "fatigue_confidence_rating"
                )
            ),

            "FatigueStartStroke": fatigue_start_stroke,

            "FatigueStartTimeSeconds": fatigue_start_time,

            "FatigueStartDistanceMeters": (
                fatigue_start_distance
            ),

            "MaximumFatigueSeverity": (
                self.fatigue_summary.get(
                    "maximum_fatigue_severity"
                )
            ),

            "BaselineStartStroke": (
                self.fatigue_summary.get(
                    "baseline_start_stroke"
                )
            ),

            "BaselineEndStroke": (
                self.fatigue_summary.get(
                    "baseline_end_stroke"
                )
            ),
        }

        return pd.DataFrame([summary])

    def export_session_summary(self):
        """
        Save the session-level summary as a one-row CSV.
        """

        summary_df = self.create_session_summary()

        output_path = (
            self.data_directory
            / "session_summary.csv"
        )

        summary_df.to_csv(
            output_path,
            index=False,
        )

        return output_path

    def create_coach_report_text(self):
        """
        Convert the coach report dictionary into readable text.
        """

        fatigue_confidence = self.fatigue_summary.get(
            "fatigue_confidence",
            0.0,
        )

        fatigue_confidence_rating = (
            self.fatigue_summary.get(
                "fatigue_confidence_rating",
                "Unknown",
            )
        )

        lines = [
            "ROWING SESSION COACH REPORT",
            "=" * 40,
            "",
            (
                "Overall rating: "
                f"{self.coach_report['session_rating']}"
            ),
            (
                "Session score: "
                f"{self.coach_report['session_score']:.1f}/100"
            ),
            "",
            (
                "Strongest area: "
                f"{self.coach_report['strongest_area']} "
                f"({self.coach_report['strongest_area_score']:.1f}/100)"
            ),
            (
                "Main area to improve: "
                f"{self.coach_report['weakest_area']} "
                f"({self.coach_report['weakest_area_score']:.1f}/100)"
            ),
            "",
            (
                "Fatigue finding: "
                f"{self.coach_report['fatigue_message']}"
            ),
            (
                "Fatigue confidence: "
                f"{fatigue_confidence:.1f}% "
                f"({fatigue_confidence_rating})"
            ),
            "",
            (
                "Recommendation: "
                f"{self.coach_report['recommendation']}"
            ),
            "",
            "COMPONENT SCORES",
            "-" * 40,
        ]

        for component, score in self.coach_report[
            "component_scores"
        ].items():
            lines.append(
                f"{component}: {score:.1f}/100"
            )

        lines.extend(
            [
                "",
                "IMPORTANT INTERPRETATION",
                "-" * 40,
                (
                    "The fatigue result represents an estimated "
                    "sustained performance decline relative to the "
                    "athlete's early-session baseline."
                ),
                (
                    "It does not independently prove physiological "
                    "fatigue or identify its cause."
                ),
            ]
        )

        return "\n".join(lines)
    def export_coach_report(self):
        """
        Save the readable report as a text file.
        """

        output_path = (
            self.report_directory
            / "coach_report.txt"
        )

        report_text = (
            self.create_coach_report_text()
        )

        output_path.write_text(
            report_text,
            encoding="utf-8",
        )

        return output_path

    def export_all(self):
        """
        Export every final result and return the saved paths.
        """

        return [
            self.export_stroke_analysis(),
            self.export_session_summary(),
            self.export_coach_report(),
        ]