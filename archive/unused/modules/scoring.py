import numpy as np


class StrokeScorer:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def normalize(self, column, inverse=False):

        values = self.df[column]

        minimum = values.min()
        maximum = values.max()

        normalized = (
            values - minimum
        ) / (maximum - minimum + 1e-9)

        if inverse:
            normalized = 1 - normalized

        return normalized

    def calculate_scores(self):

        speed = self.normalize("MeanSpeed")

        power = self.normalize("PowerMean")

        efficiency = self.normalize("Efficiency")

        drag = self.normalize("Drag", inverse=True)

        fatigue = self.normalize("Fatigue", inverse=True)

        consistency = self.normalize("Consistency")

        self.df["Score"] = (

            speed * 0.25 +

            power * 0.25 +

            efficiency * 0.20 +

            drag * 0.10 +

            fatigue * 0.10 +

            consistency * 0.10

        ) * 100

        return self

    def grade(self):

        grades = []

        for score in self.df["Score"]:

            if score >= 90:
                grades.append("A")

            elif score >= 80:
                grades.append("B")

            elif score >= 70:
                grades.append("C")

            elif score >= 60:
                grades.append("D")

            else:
                grades.append("F")

        self.df["Grade"] = grades

        return self

    def get_dataframe(self):

        return self.df