class CoachFeedback:

    def __init__(self, dataframe):

        self.df = dataframe

    def analyze(self):

        comments = []

        if self.df["BoatRun"].mean() > 8:

            comments.append(
                "Excellent boat run."
            )

        else:

            comments.append(
                "Boat run can be improved."
            )

        if self.df["Fatigue"].mean() > 8:

            comments.append(
                "Fatigue increased noticeably."
            )

        else:

            comments.append(
                "Fatigue remained stable."
            )

        if self.df["Consistency"].mean() > 90:

            comments.append(
                "Very consistent stroke rhythm."
            )

        else:

            comments.append(
                "Stroke rhythm varied during the session."
            )

        if self.df["SpeedDrop"].mean() < 0.5:

            comments.append(
                "Excellent recovery control."
            )

        else:

            comments.append(
                "Speed drops too much during recovery."
            )

        return comments