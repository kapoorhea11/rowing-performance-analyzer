from pathlib import Path

from config.data_source import DATA_SOURCE, CSV_FILE
from loaders.simulator_loader import SimulatorLoader
from loaders.speedcoach_loader import SpeedCoachLoader


class DataLoader:
    """
    Chooses the correct data source.

    For SpeedCoach data, the loader can either:

    1. Load a specific CSV passed into the constructor.
    2. Let the user select a CSV from data/sessions.
    3. Fall back to the CSV configured in config/data_source.py.
    """

    def __init__(
        self,
        csv_file=None,
        sessions_directory="data/sessions",
    ):
        self.csv_file = csv_file
        self.sessions_directory = Path(
            sessions_directory
        )
        self.selected_file = None

    def find_session_files(self):
        """
        Return all CSV files in the sessions directory,
        sorted alphabetically.
        """

        if not self.sessions_directory.exists():
            return []

        return sorted(
            self.sessions_directory.glob("*.csv")
        )

    def choose_session_file(self):
        """
        Display available session files and ask the user
        which one should be analyzed.
        """

        session_files = self.find_session_files()

        if not session_files:
            configured_file = Path(CSV_FILE)

            if configured_file.exists():
                print(
                    "No CSV files were found in "
                    f"{self.sessions_directory}."
                )

                print(
                    "Using the configured CSV instead:"
                )

                print(
                    f"  {configured_file}"
                )

                return configured_file

            raise FileNotFoundError(
                "No SpeedCoach CSV files were found in "
                f"{self.sessions_directory}, and the configured "
                f"CSV does not exist: {configured_file}"
            )

        print("\nAVAILABLE ROWING SESSIONS\n")

        for number, session_file in enumerate(
            session_files,
            start=1,
        ):
            print(
                f"{number}. {session_file.name}"
            )

        while True:
            selection = input(
                "\nSelect a session number: "
            ).strip()

            try:
                selected_number = int(selection)
            except ValueError:
                print(
                    "Please enter one of the numbers shown above."
                )
                continue

            if not (
                1
                <= selected_number
                <= len(session_files)
            ):
                print(
                    "That session number is not available."
                )
                continue

            return session_files[
                selected_number - 1
            ]

    def resolve_speedcoach_file(self):
        """
        Determine which SpeedCoach file should be loaded.
        """

        if self.csv_file is not None:
            selected_file = Path(
                self.csv_file
            )

            if not selected_file.exists():
                raise FileNotFoundError(
                    "The selected SpeedCoach CSV does not exist: "
                    f"{selected_file}"
                )

            return selected_file

        return self.choose_session_file()

    def load(self):
        """
        Load data from the configured source.
        """

        data_source = DATA_SOURCE.upper()

        if data_source == "SIMULATOR":
            print("\nUsing Simulator\n")

            return SimulatorLoader().load()

        if data_source == "SPEEDCOACH":
            selected_file = (
                self.resolve_speedcoach_file()
            )

            self.selected_file = selected_file

            print("\nUsing SpeedCoach CSV")
            print(
                f"Selected session: "
                f"{selected_file.name}\n"
            )

            return SpeedCoachLoader(
                str(selected_file)
            ).load()

        raise ValueError(
            f"Unknown data source: {DATA_SOURCE}"
        )