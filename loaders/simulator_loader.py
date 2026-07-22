from simulator.simulator import RowingSimulator

from loaders.data_validator import DataValidator
from loaders.data_cleaner import DataCleaner


class SimulatorLoader:

    def load(self):

        simulator = RowingSimulator()

        df = simulator.generate()

        validator = (
            DataValidator(df)
            .check_required_columns(
                ["Time", "Speed"]
            )
            .remove_duplicate_rows()
            .sort_by_time()
            .reset_index()
        )

        df = validator.get_dataframe()

        cleaner = (
            DataCleaner(df)
            .remove_negative_speed()
            .interpolate()
            .clip_speed()
        )

        return cleaner.get_dataframe()