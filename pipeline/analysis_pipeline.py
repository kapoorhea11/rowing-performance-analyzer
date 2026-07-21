from modules.preprocessing import DataPreprocessor
from modules.physics import PhysicsAnalyzer
from modules.power_analysis import PowerAnalyzer
from modules.stroke_detection import StrokeDetector
from modules.stroke_analysis import StrokeAnalyzer
from modules.performance_analysis import PerformanceAnalyzer
from modules.scoring import StrokeScorer


class AnalysisPipeline:

    def __init__(self, dataframe):

        self.df = dataframe

    def run(self):

        # -------------------------
        # Preprocessing
        # -------------------------

        processor = (
            DataPreprocessor(self.df)
            .interpolate_missing()
            .smooth_speed()
            .calculate_acceleration()
            .calculate_jerk()
        )

        self.df = processor.get_dataframe()

        # -------------------------
        # Physics
        # -------------------------

        physics = (
            PhysicsAnalyzer(self.df)
            .calculate_momentum()
            .calculate_kinetic_energy()
            .calculate_drag_force()
            .calculate_deceleration()
            .calculate_glide_distance()
        )

        self.df = physics.get_dataframe()

        # -------------------------
        # Power
        # -------------------------

        power = (
            PowerAnalyzer(self.df)
            .calculate_power()
            .calculate_drag_power()
            .calculate_work()
            .calculate_energy_loss()
        )

        self.df = power.get_dataframe()

        # -------------------------
        # Stroke Detection
        # -------------------------

        detector = StrokeDetector(self.df)

        peaks = detector.detect()

        # -------------------------
        # Stroke Analysis
        # -------------------------

        analyzer = StrokeAnalyzer(self.df, peaks)

        analyzer.analyze()

        stroke_df = analyzer.to_dataframe()

        # -------------------------
        # Performance
        # -------------------------

        performance = (
            PerformanceAnalyzer(stroke_df)
            .calculate_efficiency()
            .calculate_consistency()
            .detect_fatigue()
        )

        stroke_df = performance.get_dataframe()

        # -------------------------
        # Scoring
        # -------------------------

        scorer = (
            StrokeScorer(stroke_df)
            .calculate_scores()
            .grade()
        )

        stroke_df = scorer.get_dataframe()

        return self.df, stroke_df, peaks