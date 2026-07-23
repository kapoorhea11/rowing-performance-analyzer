import pandas as pd

from modules.real_stroke_analysis import RealStrokeAnalyzer
from modules.fatigue_detector import FatigueDetector
from modules.stroke_scorer import StrokeScorer
from modules.coach_report import CoachReportGenerator
from modules.session_segmenter import SessionSegmenter



class RealDataPipeline:
    """
    Runs the focused analysis pipeline for SpeedCoach per-stroke data.
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.raw_df = dataframe.copy()

    def run(self):
        # First calculate the basic per-stroke metrics.
        stroke_df = RealStrokeAnalyzer(
            self.raw_df
        ).run()

        if stroke_df.empty:
            raise ValueError(
                "No valid rowing strokes remained after cleaning."
            )
        stroke_df, segment_summary = SessionSegmenter(
            stroke_df
        ).run()
        
        # Then calculate fatigue-related metrics.
        stroke_df, fatigue_summary = FatigueDetector(
            stroke_df
                ).run()

        stroke_df, session_score = StrokeScorer(
            stroke_df,
            baseline_start_index=(
                fatigue_summary["baseline_start_index"]
            ),
            baseline_end_index=(
                fatigue_summary["baseline_end_index"]
            ),
        ).run()

        coach_report = CoachReportGenerator(
            dataframe=stroke_df,
            fatigue_summary=fatigue_summary,
            session_score=session_score,
        ).run()

        return (
            stroke_df,
            segment_summary,
            fatigue_summary,
            session_score,
            coach_report,
        )