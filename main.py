from pipeline.real_data_pipeline import RealDataPipeline
from utils.result_exporter import ResultExporter
from visualizations.session_plots import SessionPlotGenerator
from loaders.data_loader import DataLoader
import re
from pathlib import Path



def create_session_output_directory(
    selected_file,
):
    """
    Create a safe output folder name from the selected CSV filename.
    """

    if selected_file is None:
        session_name = "current_session"
    else:
        session_name = Path(
            selected_file
        ).stem

    safe_session_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        session_name,
    ).strip("_")

    output_directory = (
        Path("outputs")
        / "sessions"
        / safe_session_name
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_directory


def print_header():
    print("=" * 60)
    print("ROWING PERFORMANCE ANALYZER")
    print("=" * 60)
    print()


def print_clean_data(
    stroke_df,
):
    print("\nCLEAN STROKE DATA\n")

    print(
        stroke_df.head()
    )


def print_session_overview(
    stroke_df,
):
    valid_strokes = len(
        stroke_df
    )

    duration_seconds = float(
        stroke_df["Time"].max()
        - stroke_df["Time"].min()
    )

    duration_minutes = (
        duration_seconds / 60.0
    )

    distance_meters = float(
        stroke_df["Distance"].max()
        - stroke_df["Distance"].min()
    )

    average_speed = float(
        stroke_df["Speed"].mean()
    )

    average_stroke_rate = float(
        stroke_df["StrokeRate"].mean()
    )

    average_distance_per_stroke = float(
        stroke_df[
            "DistancePerStroke"
        ].mean()
    )

    average_stroke_duration = float(
        stroke_df[
            "StrokeDuration"
        ].mean()
    )

    print("\nSESSION OVERVIEW\n")

    print(
        f"Valid strokes: {valid_strokes}"
    )

    print(
        "Duration: "
        f"{duration_minutes:.1f} minutes"
    )

    print(
        "Distance: "
        f"{distance_meters:.1f} meters"
    )

    print(
        "Average speed: "
        f"{average_speed:.2f} m/s"
    )

    print(
        "Average stroke rate: "
        f"{average_stroke_rate:.1f} spm"
    )

    print(
        "Average distance per stroke: "
        f"{average_distance_per_stroke:.2f} m"
    )

    print(
        "Average stroke duration: "
        f"{average_stroke_duration:.2f} s"
    )


def print_session_segments(
    segment_summary,
):
    print("\nSESSION SEGMENTS\n")

    if (
        segment_summary is None
        or segment_summary.empty
    ):
        print(
            "No continuous rowing segments were found."
        )

        return

    print(
        segment_summary
    )


def print_fatigue_analysis(
    fatigue_summary,
):
    print("\nFATIGUE ANALYSIS\n")

    print(
        "Segments analyzed: "
        f"{fatigue_summary.get('segments_analyzed', 0)}"
    )

    fatigue_detected = fatigue_summary.get(
        "fatigue_detected",
        False,
    )

    if not fatigue_detected:
        print(
            "Fatigue detected: No"
        )

        confidence_rating = fatigue_summary.get(
            "fatigue_confidence_rating",
            "No confirmed decline",
        )

        print(
            "Confidence status: "
            f"{confidence_rating}"
        )

        return

    print(
        "Fatigue detected: Yes"
    )

    print(
        "Detected in segment: "
        f"{fatigue_summary.get('fatigue_segment')}"
    )

    fatigue_confidence = fatigue_summary.get(
        "fatigue_confidence",
        0.0,
    )

    fatigue_confidence_rating = fatigue_summary.get(
        "fatigue_confidence_rating",
        "Unknown",
    )

    print(
        "Confidence: "
        f"{fatigue_confidence:.1f}% "
        f"({fatigue_confidence_rating})"
    )

    baseline_start_stroke = fatigue_summary.get(
        "baseline_start_stroke"
    )

    baseline_end_stroke = fatigue_summary.get(
        "baseline_end_stroke"
    )

    if (
        baseline_start_stroke is not None
        and baseline_end_stroke is not None
    ):
        print(
            "Baseline strokes: "
            f"{baseline_start_stroke}–"
            f"{baseline_end_stroke}"
        )

    fatigue_start_stroke = fatigue_summary.get(
        "fatigue_start_stroke"
    )

    if fatigue_start_stroke is not None:
        print(
            "Estimated fatigue start stroke: "
            f"{fatigue_start_stroke}"
        )

    fatigue_start_time = fatigue_summary.get(
        "fatigue_start_time"
    )

    if fatigue_start_time is not None:
        print(
            "Estimated fatigue start time: "
            f"{fatigue_start_time / 60.0:.1f} minutes"
        )

    fatigue_start_distance = fatigue_summary.get(
        "fatigue_start_distance"
    )

    if fatigue_start_distance is not None:
        print(
            "Estimated fatigue start distance: "
            f"{fatigue_start_distance:.1f} meters"
        )

    maximum_severity = fatigue_summary.get(
        "maximum_fatigue_severity",
        0.0,
    )

    print(
        "Maximum fatigue severity: "
        f"{maximum_severity:.2f}"
    )


def print_segment_fatigue_results(
    fatigue_summary,
):
    print("\nSEGMENT FATIGUE RESULTS\n")

    segment_results = fatigue_summary.get(
        "segment_results",
        [],
    )

    if not segment_results:
        print(
            "No segments were available for fatigue analysis."
        )

        return

    for result in segment_results:
        segment_number = result.get(
            "segment"
        )

        print(
            f"Segment {segment_number}:"
        )

        print(
            "  Strokes: "
            f"{result.get('strokes', 0)}"
        )

        if not result.get(
            "analyzed",
            False,
        ):
            print(
                "  Status: Not analyzed"
            )

            print(
                "  Reason: "
                f"{result.get('reason', 'Unknown reason')}"
            )

            print()

            continue

        if not result.get(
            "fatigue_detected",
            False,
        ):
            print(
                "  Fatigue detected: No"
            )

            print(
                "  Confidence status: "
                f"{result.get('confidence_rating')}"
            )

            print()

            continue

        print(
            "  Fatigue detected: Yes"
        )

        print(
            "  Fatigue start stroke: "
            f"{result.get('fatigue_start_stroke')}"
        )

        fatigue_start_time = result.get(
            "fatigue_start_time"
        )

        if fatigue_start_time is not None:
            print(
                "  Fatigue start time: "
                f"{fatigue_start_time / 60.0:.1f} minutes"
            )

        confidence_score = result.get(
            "confidence_score",
            0.0,
        )

        confidence_rating = result.get(
            "confidence_rating",
            "Unknown",
        )

        print(
            "  Confidence: "
            f"{confidence_score:.1f}% "
            f"({confidence_rating})"
        )

        print(
            "  Longest sustained signal: "
            f"{result.get('longest_signal_run', 0)} strokes"
        )

        print()


def print_coach_report(
    coach_report,
):
    print("\nCOACH REPORT\n")

    overall_rating = coach_report.get(
        "session_rating",
        coach_report.get(
            "overall_rating",
            "Not available",
        ),
    )

    session_score = coach_report.get(
        "session_score",
        0.0,
    )

    strongest_area = coach_report.get(
        "strongest_area",
        "Not available",
    )

    strongest_area_score = coach_report.get(
        "strongest_area_score",
        0.0,
    )

    weakest_area = coach_report.get(
        "weakest_area",
        "Not available",
    )

    weakest_area_score = coach_report.get(
        "weakest_area_score",
        0.0,
    )

    fatigue_message = coach_report.get(
        "fatigue_message",
        coach_report.get(
            "fatigue_finding",
            "Not available",
        ),
    )

    recommendation = coach_report.get(
        "recommendation",
        "Not available",
    )

    print(
        "Overall rating: "
        f"{overall_rating}"
    )

    print(
        "Session score: "
        f"{session_score:.1f}/100"
    )

    print(
        "Strongest area: "
        f"{strongest_area} "
        f"({strongest_area_score:.1f}/100)"
    )

    print(
        "Main area to improve: "
        f"{weakest_area} "
        f"({weakest_area_score:.1f}/100)"
    )

    print(
        "Fatigue finding: "
        f"{fatigue_message}"
    )

    print(
        "Recommendation: "
        f"{recommendation}"
    )


def print_component_scores(
    coach_report,
):
    print("\nCOMPONENT SCORES\n")

    component_scores = coach_report.get(
        "component_scores",
        {},
    )

    if not component_scores:
        print(
            "No component scores are available."
        )

        return

    for component_name, score in component_scores.items():
        print(
            f"{component_name}: {score:.1f}/100"
        )


def generate_graphs(
    stroke_df,
    fatigue_summary,
    output_directory,
):
    print("\nGENERATING GRAPHS\n")

    figure_directory = (
        Path(output_directory)
        / "figures"
    )

    plot_generator = SessionPlotGenerator(
        dataframe=stroke_df,
        fatigue_summary=fatigue_summary,
        output_directory=str(
            figure_directory
        ),
    )

    figure_paths = (
        plot_generator.generate_all()
    )

    for figure_path in figure_paths:
        print(
            f"Saved: {figure_path}"
        )


def export_results(
    stroke_df,
    fatigue_summary,
    session_score,
    coach_report,
    output_directory,
):
    print("\nEXPORTING RESULTS\n")

    data_directory = (
        Path(output_directory)
        / "data"
    )

    report_directory = (
        Path(output_directory)
        / "reports"
    )

    exporter = ResultExporter(
        stroke_dataframe=stroke_df,
        fatigue_summary=fatigue_summary,
        session_score=session_score,
        coach_report=coach_report,
        data_directory=str(
            data_directory
        ),
        report_directory=str(
            report_directory
        ),
    )

    export_paths = exporter.export_all()

    for export_path in export_paths:
        print(
            f"Saved: {export_path}"
        )

def process_session(
    session_file,
    show_full_results=True,
):
    """
    Analyze one CSV session and save its outputs.

    Returns a small summary used by batch mode.
    """

    print("\n" + "=" * 60)
    print(f"ANALYZING: {session_file.name}")
    print("=" * 60)

    data_loader = DataLoader(
        csv_file=session_file
    )

    dataframe = data_loader.load()

    session_output_directory = (
        create_session_output_directory(
            session_file
        )
    )

    source_file_name = session_file.name

    source_name_file = (
        session_output_directory
        / "source_file.txt"
    )

    source_name_file.write_text(
        source_file_name,
        encoding="utf-8",
    )

    print(
        "Session output folder: "
        f"{session_output_directory}"
    )

    pipeline = RealDataPipeline(
        dataframe=dataframe
    )

    (
        stroke_df,
        segment_summary,
        fatigue_summary,
        session_score,
        coach_report,
    ) = pipeline.run()

    if show_full_results:
        print_clean_data(
            stroke_df
        )

        print_session_overview(
            stroke_df
        )

        print_session_segments(
            segment_summary
        )

        print_fatigue_analysis(
            fatigue_summary
        )

        print_segment_fatigue_results(
            fatigue_summary
        )

        print_coach_report(
            coach_report
        )

        print_component_scores(
            coach_report
        )

    generate_graphs(
        stroke_df=stroke_df,
        fatigue_summary=fatigue_summary,
        output_directory=(
            session_output_directory
        ),
    )

    export_results(
        stroke_df=stroke_df,
        fatigue_summary=fatigue_summary,
        session_score=session_score,
        coach_report=coach_report,
        output_directory=(
            session_output_directory
        ),
    )

    return {
        "session": session_file.name,
        "status": "Success",
        "valid_strokes": len(stroke_df),
        "session_score": float(
            session_score
        ),
        "fatigue_detected": bool(
            fatigue_summary.get(
                "fatigue_detected",
                False,
            )
        ),
        "output_directory": str(
            session_output_directory
        ),
    }

def choose_analysis_mode(
    session_files,
):
    """
    Let the user select one session or analyze every session.
    """

    if not session_files:
        raise FileNotFoundError(
            "No CSV files were found in data/sessions."
        )

    print("\nAVAILABLE ROWING SESSIONS\n")

    print("0. Analyze all sessions")

    for number, session_file in enumerate(
        session_files,
        start=1,
    ):
        print(
            f"{number}. {session_file.name}"
        )

    while True:
        selection = input(
            "\nSelect an option: "
        ).strip()

        try:
            selected_number = int(
                selection
            )
        except ValueError:
            print(
                "Please enter one of the numbers shown above."
            )
            continue

        if selected_number == 0:
            return session_files

        if (
            1
            <= selected_number
            <= len(session_files)
        ):
            return [
                session_files[
                    selected_number - 1
                ]
            ]

        print(
            "That option is not available."
        )
def print_batch_summary(
    successful_sessions,
    failed_sessions,
):
    """
    Print a concise summary after processing multiple sessions.
    """

    print("\n" + "=" * 60)
    print("BATCH ANALYSIS SUMMARY")
    print("=" * 60)

    print(
        "\nSuccessful sessions: "
        f"{len(successful_sessions)}"
    )

    for result in successful_sessions:
        fatigue_status = (
            "Yes"
            if result["fatigue_detected"]
            else "No"
        )

        print(
            f"\n- {result['session']}"
        )

        print(
            "  Valid strokes: "
            f"{result['valid_strokes']}"
        )

        print(
            "  Session score: "
            f"{result['session_score']:.1f}/100"
        )

        print(
            "  Fatigue detected: "
            f"{fatigue_status}"
        )

        print(
            "  Output: "
            f"{result['output_directory']}"
        )

    print(
        "\nFailed sessions: "
        f"{len(failed_sessions)}"
    )

    for failure in failed_sessions:
        print(
            f"\n- {failure['session']}"
        )

        print(
            "  Error: "
            f"{failure['error']}"
        )

def main():
    print_header()

    session_loader = DataLoader()

    session_files = (
        session_loader.find_session_files()
    )

    selected_sessions = (
        choose_analysis_mode(
            session_files
        )
    )

    analyze_all = (
        len(selected_sessions)
        > 1
    )

    successful_sessions = []
    failed_sessions = []

    for session_file in selected_sessions:
        try:
            result = process_session(
                session_file=session_file,
                show_full_results=(
                    not analyze_all
                ),
            )

            successful_sessions.append(
                result
            )

        except ValueError as error:
            error_message = str(
                error
            )

            if (
                "Not enough valid baseline data"
                in error_message
            ):
                print(
                    "\nSESSION SKIPPED"
                )

                print(
                    f"Session: {session_file.name}"
                )

                print(
                    "Reason: Not enough valid rowing data "
                    "to calculate a reliable baseline."
                )

                failed_sessions.append(
                    {
                        "session": session_file.name,
                        "error": (
                            "Skipped: insufficient valid "
                            "baseline data"
                        ),
                    }
                )

            else:
                print(
                    "\nERROR ANALYZING SESSION"
                )

                print(
                    f"Session: {session_file.name}"
                )

                print(
                    f"Error: {error_message}"
                )

                failed_sessions.append(
                    {
                        "session": session_file.name,
                        "error": error_message,
                    }
                )

        except Exception as error:
            print(
                "\nERROR ANALYZING SESSION"
            )

            print(
                f"Session: {session_file.name}"
            )

            print(
                f"Error: {error}"
            )

            failed_sessions.append(
                {
                    "session": session_file.name,
                    "error": str(error),
                }
            )

    if analyze_all:
        print_batch_summary(
            successful_sessions=(
                successful_sessions
            ),
            failed_sessions=(
                failed_sessions
            ),
        )

    if failed_sessions:
        print(
            "\nSome sessions could not be analyzed."
        )

    elif successful_sessions:
        print(
            "\nAnalysis completed successfully."
        )

if __name__ == "__main__":
    main()