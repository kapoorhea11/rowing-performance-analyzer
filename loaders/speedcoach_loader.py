import pandas as pd


class SpeedCoachLoader:

    def __init__(self, filename):

        self.filename = filename

    def load(self):

        df = pd.read_csv(self.filename)

        return df