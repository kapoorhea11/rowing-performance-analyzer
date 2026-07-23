from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class SessionPlotGenerator:
    """
    Creates the five final coach-facing and research-facing graphs.

    Graphs:
    1. Boat speed
    2. Stroke rate
    3. Distance per stroke
    4. Stroke score
    5. Fatigue severity
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        fatigue_summary: dict,
        output_directory: str = "outputs/figures",
    ):
        self.df = dataframe.copy()
        self.fatigue_summary = fatigue_summary

        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def add_fatigue_marker(self):
        """
        Add a vertical line when fatigue was detected.

        This method is called after the graph itself has been drawn.
        """

        if not self.fatigue_summary["fatigue_detected"]:
            return

        fatigue_stroke = self.fatigue_summary[
            "fatigue_start_stroke"
        ]

        plt.axvline(
            x=fatigue_stroke,
            linestyle="--",
            linewidth=1.5,
            label="Estimated decline begins",
        )

    def finish_plot(
        self,
        title: str,
        y_label: str,
        filename: str,
        show_legend: bool = True,
    ):
        """
        Apply consistent formatting, save the graph, and close it.
        """

        plt.title(title)
        plt.xlabel("Stroke Number")
        plt.ylabel(y_label)
        plt.grid(
            alpha=0.25
        )

        if show_legend:
            plt.legend()

        plt.tight_layout()

        output_path = (
            self.output_directory / filename
        )

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close()

        return output_path

    def plot_speed(self):
        """
        Show raw per-stroke speed and the 10-stroke rolling average.
        """

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["Speed"],
            alpha=0.35,
            linewidth=1,
            label="Per-stroke speed",
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["RollingSpeed"],
            linewidth=2,
            label="10-stroke rolling speed",
        )

        self.add_fatigue_marker()

        return self.finish_plot(
            title="Boat Speed Across the Session",
            y_label="Speed (m/s)",
            filename="01_boat_speed.png",
        )

    def plot_stroke_rate(self):
        """
        Show raw stroke rate and rolling stroke rate.
        """

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["StrokeRate"],
            alpha=0.35,
            linewidth=1,
            label="Per-stroke rate",
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["RollingStrokeRate"],
            linewidth=2,
            label="10-stroke rolling rate",
        )

        self.add_fatigue_marker()

        return self.finish_plot(
            title="Stroke Rate Across the Session",
            y_label="Stroke Rate (strokes/min)",
            filename="02_stroke_rate.png",
        )

    def plot_distance_per_stroke(self):
        """
        Show technical effectiveness through distance per stroke.
        """

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["DistancePerStroke"],
            alpha=0.35,
            linewidth=1,
            label="Per-stroke distance",
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["RollingDistancePerStroke"],
            linewidth=2,
            label="10-stroke rolling distance",
        )

        self.add_fatigue_marker()

        return self.finish_plot(
            title="Distance per Stroke Across the Session",
            y_label="Distance per Stroke (m)",
            filename="03_distance_per_stroke.png",
        )

    def plot_stroke_score(self):
        """
        Show the combined 0-to-100 relative performance score.
        """

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["StrokeScore"],
            linewidth=1.5,
            label="Stroke score",
        )

        plt.axhline(
            y=80,
            linestyle=":",
            linewidth=1,
            label="80-point reference",
        )

        self.add_fatigue_marker()

        plt.ylim(
            0,
            105,
        )

        return self.finish_plot(
            title="Relative Stroke Performance Score",
            y_label="Stroke Score (0–100)",
            filename="04_stroke_score.png",
        )

    def plot_fatigue(self):
        """
        Show the estimated severity of sustained performance decline.

        This is not a medical measurement of fatigue.
        """

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            self.df["StrokeNumber"],
            self.df["FatigueSeverity"],
            linewidth=2,
            label="Performance-decline severity",
        )

        plt.fill_between(
            self.df["StrokeNumber"],
            self.df["FatigueSeverity"],
            alpha=0.2,
        )

        self.add_fatigue_marker()

        plt.ylim(
            0,
            1.05,
        )

        return self.finish_plot(
            title="Estimated Performance-Decline Trend",
            y_label="Severity (0–1)",
            filename="05_fatigue_trend.png",
        )

    def generate_all(self):
        """
        Generate all five graphs and return their saved locations.
        """

        required_columns = [
            "StrokeNumber",
            "Speed",
            "RollingSpeed",
            "StrokeRate",
            "RollingStrokeRate",
            "DistancePerStroke",
            "RollingDistancePerStroke",
            "StrokeScore",
            "FatigueSeverity",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Visualization is missing required columns: "
                f"{missing_columns}"
            )

        output_paths = [
            self.plot_speed(),
            self.plot_stroke_rate(),
            self.plot_distance_per_stroke(),
            self.plot_stroke_score(),
            self.plot_fatigue(),
        ]

        return output_paths