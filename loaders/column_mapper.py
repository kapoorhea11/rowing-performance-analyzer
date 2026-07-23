class ColumnMapper:

    COLUMN_MAP = {

        "Elapsed Time": "Time",

        "Speed (GPS)": "Speed",

        "Stroke Rate": "StrokeRate",

        "Distance (GPS)": "Distance",

        "Distance/Stroke (GPS)": "DistancePerStroke",

        "Heart Rate": "HeartRate",

        "Power": "Power",

        "Total Strokes": "StrokeNumber"

    }

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    def rename_columns(self):
        self.df = self.df.rename(columns=self.COLUMN_MAP)
        return self

    def get_dataframe(self):
        return self.df