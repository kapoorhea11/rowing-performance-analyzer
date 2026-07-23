import pandas as pd


class CoachReportGenerator:
    """
    Converts stroke metrics into a concise coach-facing report.

    The report identifies:
    - overall session quality
    - strongest performance area
    - weakest performance area
    - fatigue timing
    - one main recommendation
    """

    COMPONENT_COLUMNS = {
        "Speed retention": "SpeedScore",
        "Distance per stroke": "DistancePerStrokeScore",
        "Rhythm control": "RhythmScore",
        "Speed consistency": "ConsistencyScore",
    }

    def __init__(
        self,
        dataframe: pd.DataFrame,
        fatigue_summary: dict,
        session_score: float,
    ):
        self.df = dataframe.copy()
        self.fatigue_summary = fatigue_summary
        self.session_score = session_score

    def get_scoring_data(self):
        """
        Exclude startup strokes from coach-level averages.
        """

        baseline_start_index = self.fatigue_summary[
            "baseline_start_index"
        ]

        return self.df.iloc[
            baseline_start_index:
        ].copy()

    def calculate_component_averages(self):
        scoring_data = self.get_scoring_data()

        averages = {}

        for label, column in self.COMPONENT_COLUMNS.items():

            if column in scoring_data.columns:

                averages[label] = float(
                    scoring_data[column].mean()
                )

        return averages

    def classify_session_score(self):
        """
        Convert the numerical score into a simple description.
        """

        if self.session_score >= 90:
            return "Excellent"

        if self.session_score >= 80:
            return "Strong"

        if self.session_score >= 70:
            return "Solid"

        if self.session_score >= 60:
            return "Developing"

        return "Needs improvement"

    def identify_strength_and_weakness(self, averages):
        if not averages:
            return None, None

        strongest_area = max(
            averages,
            key=averages.get,
        )

        weakest_area = min(
            averages,
            key=averages.get,
        )

        return strongest_area, weakest_area

    def create_fatigue_message(self):
        if not self.fatigue_summary["fatigue_detected"]:

            return (
                "No sustained performance decline was detected "
                "after the baseline period."
            )

        stroke = self.fatigue_summary[
            "fatigue_start_stroke"
        ]

        time_minutes = (
            self.fatigue_summary[
                "fatigue_start_time"
            ]
            / 60
        )

        distance = self.fatigue_summary[
            "fatigue_start_distance"
        ]

        confidence = self.fatigue_summary.get(
            "fatigue_confidence",
            0.0,
        )

        confidence_rating = self.fatigue_summary.get(
            "fatigue_confidence_rating",
            "Unknown",
        )

        return (
            "Sustained performance decline began near "
            f"stroke {stroke}, "
            f"{time_minutes:.1f} minutes, "
            f"and {distance:.0f} meters. "
            f"Detection confidence was "
            f"{confidence:.1f}% "
            f"({confidence_rating.lower()})."
        )

    def create_recommendation(self, weakest_area):
        """
        Return one main recommendation based on the weakest component.
        """

        recommendations = {
            "Speed retention": (
                "Focus on maintaining boat speed through the "
                "second half of the session."
            ),

            "Distance per stroke": (
                "Prioritize effective connection and stroke length "
                "instead of increasing stroke rate."
            ),

            "Rhythm control": (
                "Work on holding a steadier stroke rate and recovery rhythm."
            ),

            "Speed consistency": (
                "Focus on producing more repeatable strokes and "
                "reducing stroke-to-stroke speed variation."
            ),
        }

        return recommendations.get(
            weakest_area,
            "Continue monitoring stroke quality throughout the session.",
        )

    def create_fatigue_recommendation(self, recommendation):
        """
        Add fatigue context without replacing the main recommendation.
        """

        if not self.fatigue_summary["fatigue_detected"]:
            return recommendation

        fatigue_stroke = self.fatigue_summary[
            "fatigue_start_stroke"
        ]

        return (
            f"{recommendation} Pay particular attention after "
            f"approximately stroke {fatigue_stroke}."
        )

    def run(self):
        averages = self.calculate_component_averages()

        strongest_area, weakest_area = (
            self.identify_strength_and_weakness(
                averages
            )
        )

        recommendation = self.create_recommendation(
            weakest_area
        )

        recommendation = self.create_fatigue_recommendation(
            recommendation
        )

        report = {
            "session_score": round(
                self.session_score,
                1,
            ),

            "session_rating": (
                self.classify_session_score()
            ),

            "strongest_area": strongest_area,

            "strongest_area_score": (
                round(averages[strongest_area], 1)
                if strongest_area is not None
                else None
            ),

            "weakest_area": weakest_area,

            "weakest_area_score": (
                round(averages[weakest_area], 1)
                if weakest_area is not None
                else None
            ),

            "fatigue_message": (
                self.create_fatigue_message()
            ),

            "recommendation": recommendation,

            "component_scores": {
                label: round(score, 1)
                for label, score in averages.items()
            },
        }

        return report