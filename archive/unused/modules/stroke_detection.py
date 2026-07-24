from scipy.signal import find_peaks


class StrokeDetector:
    """
    Detect rowing strokes from the smoothed speed signal.
    """

    def __init__(
        self,
        dataframe,
        distance=15,
        prominence=0.02,
    ):
        self.df = dataframe
        self.distance = distance
        self.prominence = prominence

    def detect(self):
        """
        Return the indices of detected stroke peaks.
        """

        peaks, _ = find_peaks(
            self.df["SmoothSpeed"],
            distance=self.distance,
            prominence=self.prominence,
        )

        return peaks