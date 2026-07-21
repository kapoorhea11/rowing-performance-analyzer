import matplotlib.pyplot as plt


class Visualizer:

    def __init__(self, dataframe):
        self.df = dataframe

    def plot_speed(self):

        plt.figure(figsize=(12, 5))

        plt.plot(
            self.df["Time"],
            self.df["Speed"],
            label="Raw Speed"
        )

        plt.plot(
            self.df["Time"],
            self.df["SmoothSpeed"],
            linewidth=2,
            label="Smoothed Speed"
        )

        plt.title("Boat Speed")

        plt.xlabel("Time (s)")
        plt.ylabel("Speed (m/s)")

        plt.grid()

        plt.legend()

        plt.show()

    def plot_acceleration(self):

        plt.figure(figsize=(12, 5))

        plt.plot(
            self.df["Time"],
            self.df["Acceleration"]
        )

        plt.title("Acceleration")

        plt.xlabel("Time (s)")
        plt.ylabel("Acceleration (m/s²)")

        plt.grid()

        plt.show()

    def plot_detected_strokes(self, peaks):

        plt.figure(figsize=(14, 6))

        plt.plot(
            self.df["Time"],
            self.df["SmoothSpeed"],
            label="Smoothed Speed"
        )

        plt.scatter(
            self.df["Time"].iloc[peaks],
            self.df["SmoothSpeed"].iloc[peaks],
            color="red",
            s=35,
            label="Stroke Peaks"
        )

        plt.title("Detected Stroke Peaks")

        plt.xlabel("Time (s)")
        plt.ylabel("Speed (m/s)")

        plt.grid()

        plt.legend()

        plt.show()

    def plot_energy(self):

        plt.figure(figsize=(12, 5))

        plt.plot(
            self.df["Time"],
            self.df["KineticEnergy"]
        )

        plt.title("Boat Kinetic Energy")

        plt.xlabel("Time (s)")
        plt.ylabel("Energy (J)")

        plt.grid()

        plt.show()
    def plot_efficiency(self, stroke_df):

        plt.figure(figsize=(12,5))

        plt.plot(
        stroke_df["Stroke"],
        stroke_df["Efficiency"]
        )

        plt.title("Stroke Efficiency")

        plt.xlabel("Stroke Number")

        plt.ylabel("Efficiency")

        plt.grid()

        plt.show()


    def plot_fatigue(self, stroke_df):

        plt.figure(figsize=(12,5))

        plt.plot(
        stroke_df["Stroke"],
        stroke_df["Fatigue"]
        )

        plt.title("Fatigue Trend")

        plt.xlabel("Stroke Number")

        plt.ylabel("Fatigue (%)")

        plt.grid()

        plt.show()

    def plot_power(self):

        plt.figure(figsize=(12,5))

        plt.plot(
        self.df["Time"],
        self.df["Power"]
        )

        plt.title("Estimated Power")

        plt.xlabel("Time (s)")
        plt.ylabel("Watts (relative)")

        plt.grid()

        plt.show()


    def plot_drag(self):

        plt.figure(figsize=(12,5))

        plt.plot(
        self.df["Time"],
        self.df["DragPower"]
        )

        plt.title("Drag Power Loss")

        plt.xlabel("Time")

        plt.ylabel("Watts")

        plt.grid()

        plt.show()


    def plot_work(self):

        plt.figure(figsize=(12,5))

        plt.plot(
        self.df["Time"],
        self.df["Work"]
        )

        plt.title("Cumulative Mechanical Work")

        plt.xlabel("Time")

        plt.ylabel("Joules")

        plt.grid()

        plt.show()

    def plot_scores(self, stroke_df):

        plt.figure(figsize=(12,5))

        plt.plot(

            stroke_df["Stroke"],

            stroke_df["Score"]

        )

        plt.ylim(0,100)

        plt.title("Stroke Quality Score")

        plt.xlabel("Stroke")

        plt.ylabel("Score")

        plt.grid()

        plt.show()

    def plot_boatrun(self, stroke_df):

        plt.figure(figsize=(12,5))

        plt.plot(

            stroke_df["Stroke"],

            stroke_df["BoatRun"]

        )

        plt.title("Boat Run per Stroke")

        plt.xlabel("Stroke")

        plt.ylabel("Meters")

        plt.grid()

        plt.show()


    def plot_speed_loss(self, stroke_df):

        plt.figure(figsize=(12,5))

        plt.plot(

            stroke_df["Stroke"],

            stroke_df["SpeedDrop"]

        )

        plt.title("Speed Loss During Stroke")

        plt.xlabel("Stroke")

        plt.ylabel("m/s")

        plt.grid()

        plt.show()