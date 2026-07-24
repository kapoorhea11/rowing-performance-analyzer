from pathlib import Path
import tempfile

from pipeline.real_data_pipeline import RealDataPipeline


def process_uploaded_csv(uploaded_file):
    """
    Analyze an uploaded SpeedCoach CSV and return the
    output session directory.
    """

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_csv = (
            Path(temp_dir)
            / uploaded_file.name
        )

        temp_csv.write_bytes(
            uploaded_file.getvalue()
        )

        pipeline = RealDataPipeline()

        session_directory = pipeline.process_session(
            temp_csv
        )

    return session_directory