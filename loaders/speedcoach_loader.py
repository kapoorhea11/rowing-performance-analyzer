from loaders.data_standardizer import DataStandardizer
import pandas as pd
from io import StringIO

from loaders.column_mapper import ColumnMapper


class SpeedCoachLoader:

    def __init__(self, filename):

        self.filename = filename

    def load(self):

        with open(self.filename, "r") as file:

            lines = file.readlines()

        # -------------------------
        # Find "Per-Stroke Data:"
        # -------------------------

        start = None

        for i, line in enumerate(lines):

            if line.strip() == "Per-Stroke Data:":

                start = i + 2      # skip title + blank line

                break

        if start is None:

            raise ValueError(
                "Per-Stroke Data section not found."
            )

        # -------------------------
        # Read only the Per-Stroke table
        # -------------------------

        table = []

        for line in lines[start:]:

            if line.strip() == "":

                break

            table.append(line)

        csv_text = "".join(table)

        df = pd.read_csv(
            StringIO(csv_text)
        )

        # Remove units row
        df = df.iloc[1:].reset_index(drop=True)

        # Rename columns
        mapper = (
            ColumnMapper(df)
            .rename_columns()
        )

        df = mapper.get_dataframe()

        standardizer = (
            DataStandardizer(df)
            .convert_time()
            .convert_numeric()
            .remove_empty_columns()
)

        df = standardizer.get_dataframe()

        return df