from loaders.simulator_loader import SimulatorLoader

from pipeline.analysis_pipeline import AnalysisPipeline

from modules.visualization import Visualizer
from modules.coach import CoachFeedback

from utils.logger import setup_logger


logger = setup_logger()


def main():

    print("=" * 60)
    print("ROWING PERFORMANCE ANALYZER")
    print("=" * 60)

    logger.info("Loading data...")

    # -----------------------------------
    # Load data
    # -----------------------------------

    loader = SimulatorLoader()

    df = loader.load()

    # -----------------------------------
    # Run analysis pipeline
    # -----------------------------------

    pipeline = AnalysisPipeline(df)

    processed_df, stroke_df, peaks = pipeline.run()

    # -----------------------------------
    # Session summaries
    # -----------------------------------

    print("\nStroke Summary\n")

    print(stroke_df.head())

    print("\nStroke Statistics\n")

    print(stroke_df.describe())

    print("\nAverage Stroke Score")

    print(round(stroke_df["Score"].mean(), 2))

    print("\nGrade Distribution")

    print(stroke_df["Grade"].value_counts())

    # -----------------------------------
    # Coach feedback
    # -----------------------------------

    coach = CoachFeedback(stroke_df)

    feedback = coach.analyze()

    print()

    print("=" * 60)
    print("COACH FEEDBACK")
    print("=" * 60)

    for line in feedback:

        print("-", line)

    # -----------------------------------
    # Visualizations
    # -----------------------------------

    visualizer = Visualizer(processed_df)

    visualizer.plot_speed()

    visualizer.plot_acceleration()

    visualizer.plot_detected_strokes(peaks)

    visualizer.plot_energy()

    visualizer.plot_power()

    visualizer.plot_drag()

    visualizer.plot_work()

    visualizer.plot_efficiency(stroke_df)

    visualizer.plot_fatigue(stroke_df)

    visualizer.plot_scores(stroke_df)

    visualizer.plot_boatrun(stroke_df)

    visualizer.plot_speed_loss(stroke_df)

    logger.info("Finished.")


if __name__ == "__main__":
    main()