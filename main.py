from simulator.simulator import RowingSimulator

from utils.logger import setup_logger

from modules.preprocessing import DataPreprocessor
from modules.stroke_detection import StrokeDetector
from modules.stroke_analysis import StrokeAnalyzer
from modules.visualization import Visualizer
from modules.physics import PhysicsAnalyzer
from modules.performance_analysis import PerformanceAnalyzer
from modules.power_analysis import PowerAnalyzer
from modules.scoring import StrokeScorer
from modules.coach import CoachFeedback
from modules.biomechanics import BiomechanicsAnalyzer


logger = setup_logger()


def main():

    print("=" * 60)
    print("ROWING PERFORMANCE ANALYZER")
    print("=" * 60)

    logger.info("Generating simulation...")

    # -------------------------
    # Generate simulated data
    # -------------------------

    simulator = RowingSimulator()

    df = simulator.generate()

    print("\nRaw Data")
    print(df.head())

    # -------------------------
    # Preprocess data
    # -------------------------

    processor = (
        DataPreprocessor(df)
        .interpolate_missing()
        .smooth_speed()
        .calculate_acceleration()
        .calculate_jerk()
    )

    df = processor.get_dataframe()

    # -------------------------
    # Physics calculations
    # -------------------------

    physics = (
        PhysicsAnalyzer(df)
        .calculate_momentum()
        .calculate_kinetic_energy()
        .calculate_drag_force()
        .calculate_deceleration()
        .calculate_glide_distance()
    )

    df = physics.get_dataframe()
    
    power = (
        PowerAnalyzer(df)
        .calculate_power()
        .calculate_drag_power()
        .calculate_work()
        .calculate_energy_loss()
)

    df = power.get_dataframe()

    # -------------------------
    # Stroke Detection
    # -------------------------

    detector = StrokeDetector(df)

    peaks = detector.detect()

    print(f"\nDetected {len(peaks)} strokes")

    # -------------------------
    # Stroke Analysis
    # -------------------------

    analyzer = StrokeAnalyzer(df, peaks)

    analyzer.analyze()

    stroke_df = analyzer.to_dataframe()

    performance = (
        PerformanceAnalyzer(stroke_df)
        .calculate_efficiency()
        .calculate_consistency()
        .detect_fatigue()
)

    stroke_df = performance.get_dataframe()

    # -------------------------
    # Stroke Scoring
    # -------------------------

    scorer = (
        StrokeScorer(stroke_df)
        .calculate_scores()
        .grade()
    )

    stroke_df = scorer.get_dataframe()
    
    biomechanics = BiomechanicsAnalyzer(df, peaks)

    stroke_df["BoatRun"] = biomechanics.calculate_boatrun()

    stroke_df["SpeedDrop"] = biomechanics.calculate_speed_loss()

    stroke_df["PeakAcceleration2"] = biomechanics.calculate_peak_acceleration()
    
    print("\nStroke Summary")

    print(stroke_df.head())

    print("\nStroke Statistics")

    print(stroke_df.describe())

    print()

    print("Performance Summary")

    print()

    print("Average Stroke Score")

    print(round(stroke_df["Score"].mean(), 2))

    print()

    print("Grade Distribution")

    print(
        stroke_df["Grade"].value_counts()
    )

    print(performance.summarize())

    coach = CoachFeedback(stroke_df)

    feedback = coach.analyze()

    print()

    print("=" * 60)
    print("COACH FEEDBACK")
    print("=" * 60)

    for item in feedback:
        print("-", item)

    print("\nStrongest Stroke\n")

    print(performance.strongest_stroke())

    print("\nWeakest Stroke\n")

    print(performance.weakest_stroke())

    # -------------------------
    # Physics Summary
    # -------------------------

    print("\nPhysics Statistics")

    print(
        df[
            [
                "Momentum",
                "KineticEnergy",
                "DragForce",
                "GlideDistance",
            ]
        ].describe()
    )

    # -------------------------
    # Visualizations
    # -------------------------

    visualizer = Visualizer(df)

    visualizer.plot_speed()

    visualizer.plot_acceleration()

    visualizer.plot_detected_strokes(peaks)

    visualizer.plot_energy()

    visualizer.plot_efficiency(stroke_df)

    visualizer.plot_fatigue(stroke_df)

    visualizer.plot_power()

    visualizer.plot_drag()

    visualizer.plot_work()

    visualizer.plot_scores(stroke_df)

    visualizer.plot_boatrun(stroke_df)

    visualizer.plot_speed_loss(stroke_df)

    logger.info("Analysis Complete")


if __name__ == "__main__":
    main()