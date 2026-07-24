import numpy as np
import pandas as pd
import streamlit as st

import tempfile

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import process_session


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Rowing Performance Analyzer",
    page_icon="🚣",
    layout="wide",
)


# ---------------------------------------------------------
# FILE LOCATIONS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSIONS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "sessions"
)

SOURCE_SESSIONS_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "sessions"
)


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------

def normalize_session_name(
    name,
):
    """
    Create a simplified name used to match an output folder
    to its original CSV file.
    """

    file_stem = Path(name).stem

    return "".join(
        character.lower()
        for character in file_stem
        if character.isalnum()
    )


def get_session_display_name(
    session_directory,
):
    """
    Return the original CSV filename for an output session.
    """

    source_name_file = (
        session_directory
        / "source_file.txt"
    )

    if source_name_file.exists():
        stored_name = source_name_file.read_text(
            encoding="utf-8"
        ).strip()

        if stored_name:
            return stored_name

    if SOURCE_SESSIONS_DIRECTORY.exists():
        csv_files = list(
            SOURCE_SESSIONS_DIRECTORY.glob(
                "*.csv"
            )
        )

        output_key = normalize_session_name(
            session_directory.name
        )

        matching_files = [
            csv_file
            for csv_file in csv_files
            if normalize_session_name(
                csv_file.name
            ) == output_key
        ]

        if len(matching_files) == 1:
            return matching_files[0].name

    return session_directory.name


def find_completed_sessions():
    """
    Find session folders that contain both required CSV files.
    """

    if not SESSIONS_OUTPUT_DIRECTORY.exists():
        return []

    completed_sessions = []

    for session_directory in sorted(
        SESSIONS_OUTPUT_DIRECTORY.iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        if not session_directory.is_dir():
            continue

        summary_file = (
            session_directory
            / "data"
            / "session_summary.csv"
        )

        stroke_file = (
            session_directory
            / "data"
            / "stroke_analysis.csv"
        )

        if (
            summary_file.exists()
            and stroke_file.exists()
        ):
            completed_sessions.append(
                session_directory
            )

    return completed_sessions


def load_session_data(
    session_directory_string,
):
    """
    Load summary data, stroke data, and coach report.
    """

    session_directory = Path(
        session_directory_string
    )

    summary_file = (
        session_directory
        / "data"
        / "session_summary.csv"
    )

    stroke_file = (
        session_directory
        / "data"
        / "stroke_analysis.csv"
    )

    report_file = (
        session_directory
        / "reports"
        / "coach_report.txt"
    )

    summary_df = pd.read_csv(
        summary_file
    )

    stroke_df = pd.read_csv(
        stroke_file
    )

    if report_file.exists():
        coach_report = report_file.read_text(
            encoding="utf-8"
        )
    else:
        coach_report = (
            "No coach report was found "
            "for this session."
        )

    return (
        summary_df,
        stroke_df,
        coach_report,
    )


def get_summary_value(
    summary_df,
    column_name,
    default=None,
):
    """
    Safely retrieve one value from the session summary.
    """

    if (
        summary_df.empty
        or column_name not in summary_df.columns
    ):
        return default

    value = summary_df.iloc[0][
        column_name
    ]

    if pd.isna(value):
        return default

    return value


def format_yes_no(
    value,
):
    """
    Convert different stored values into Yes or No.
    """

    if isinstance(
        value,
        str,
    ):
        return (
            "Yes"
            if value.strip().lower()
            in {
                "true",
                "yes",
                "1",
            }
            else "No"
        )

    return (
        "Yes"
        if bool(value)
        else "No"
    )

def safe_float(
    value,
    default=0.0,
):
    """
    Safely convert a value to a float.
    """

    try:
        if value is None or pd.isna(value):
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_int(
    value,
    default=0,
):
    """
    Safely convert a value to an integer.
    """

    try:
        if value is None or pd.isna(value):
            return default

        return int(float(value))

    except (
        TypeError,
        ValueError,
    ):
        return default


def create_coach_quick_summary(
    summary_df,
):
    """
    Build a short coach-facing summary of the session.
    """

    session_score = safe_float(
        get_summary_value(
            summary_df,
            "SessionScore",
            0.0,
        )
    )

    session_rating = get_summary_value(
        summary_df,
        "SessionRating",
        "Not available",
    )

    strongest_area = get_summary_value(
        summary_df,
        "StrongestArea",
        "Not available",
    )

    weakest_area = get_summary_value(
        summary_df,
        "WeakestArea",
        "Not available",
    )

    fatigue_detected = get_summary_value(
        summary_df,
        "FatigueDetected",
        False,
    )

    fatigue_confidence_rating = get_summary_value(
        summary_df,
        "FatigueConfidenceRating",
        "Not available",
    )

    if session_score >= 90:
        status = "Excellent session"
        message_type = "success"

    elif session_score >= 80:
        status = "Strong session"
        message_type = "success"

    elif session_score >= 70:
        status = "Solid session with room to improve"
        message_type = "info"

    elif session_score >= 60:
        status = "Developing session"
        message_type = "warning"

    else:
        status = "Session needs focused improvement"
        message_type = "warning"

    if format_yes_no(fatigue_detected) == "Yes":
        fatigue_statement = (
            "Sustained performance decline was detected. "
            f"Confidence: {fatigue_confidence_rating}."
        )
    else:
        fatigue_statement = (
            "No sustained performance decline was detected."
        )

    summary_text = (
        f"**{status} — {session_score:.1f}/100**\n\n"
        f"- Overall rating: **{session_rating}**\n"
        f"- Strongest area: **{strongest_area}**\n"
        f"- Primary improvement area: **{weakest_area}**\n"
        f"- {fatigue_statement}"
    )

    return (
        message_type,
        summary_text,
    )


def create_metric_dictionary(
    summary_df,
):
    """
    Extract comparison metrics from one session summary.
    """

    return {
        "Session Score": safe_float(
            get_summary_value(
                summary_df,
                "SessionScore",
                0.0,
            )
        ),
        "Valid Strokes": safe_int(
            get_summary_value(
                summary_df,
                "ValidStrokes",
                0,
            )
        ),
        "Duration (min)": safe_float(
            get_summary_value(
                summary_df,
                "DurationMinutes",
                0.0,
            )
        ),
        "Distance (m)": safe_float(
            get_summary_value(
                summary_df,
                "DistanceMeters",
                0.0,
            )
        ),
        "Average Speed (m/s)": safe_float(
            get_summary_value(
                summary_df,
                "AverageSpeedMetersPerSecond",
                0.0,
            )
        ),
        "Average Stroke Rate (spm)": safe_float(
            get_summary_value(
                summary_df,
                "AverageStrokeRate",
                0.0,
            )
        ),
        "Average Distance per Stroke (m)": safe_float(
            get_summary_value(
                summary_df,
                "AverageDistancePerStroke",
                0.0,
            )
        ),
        "Fatigue Confidence (%)": safe_float(
            get_summary_value(
                summary_df,
                "FatigueConfidence",
                0.0,
            )
        ),
    }


def create_comparison_table(
    first_summary_df,
    second_summary_df,
    first_session_name,
    second_session_name,
):
    """
    Create a table comparing two rowing sessions.
    """

    first_metrics = create_metric_dictionary(
        first_summary_df
    )

    second_metrics = create_metric_dictionary(
        second_summary_df
    )

    comparison_rows = []

    for metric_name in first_metrics:
        first_value = first_metrics[
            metric_name
        ]

        second_value = second_metrics[
            metric_name
        ]

        difference = (
            second_value
            - first_value
        )

        comparison_rows.append(
            {
                "Metric": metric_name,
                first_session_name: first_value,
                second_session_name: second_value,
                "Change": difference,
            }
        )

    return pd.DataFrame(
        comparison_rows
    )


def choose_speed_column(
    stroke_df,
):
    """
    Choose the best available speed column.
    """

    preferred_columns = [
        "RollingSpeed",
        "Speed",
    ]

    for column_name in preferred_columns:
        if column_name in stroke_df.columns:
            return column_name

    return None


def create_normalized_speed_comparison(
    first_stroke_df,
    second_stroke_df,
    first_session_name,
    second_session_name,
):
    """
    Compare two sessions over normalized session progress.

    Sessions may contain different numbers of strokes, so each
    session is converted to a 0–100 percent progress scale.
    """

    first_speed_column = choose_speed_column(
        first_stroke_df
    )

    second_speed_column = choose_speed_column(
        second_stroke_df
    )

    if (
        first_speed_column is None
        or second_speed_column is None
    ):
        return None

    first_speed = pd.to_numeric(
        first_stroke_df[
            first_speed_column
        ],
        errors="coerce",
    ).dropna()

    second_speed = pd.to_numeric(
        second_stroke_df[
            second_speed_column
        ],
        errors="coerce",
    ).dropna()

    if (
        len(first_speed) < 2
        or len(second_speed) < 2
    ):
        return None

    normalized_progress = np.linspace(
        0,
        100,
        101,
    )

    first_original_progress = np.linspace(
        0,
        100,
        len(first_speed),
    )

    second_original_progress = np.linspace(
        0,
        100,
        len(second_speed),
    )

    first_normalized_speed = np.interp(
        normalized_progress,
        first_original_progress,
        first_speed.to_numpy(),
    )

    second_normalized_speed = np.interp(
        normalized_progress,
        second_original_progress,
        second_speed.to_numpy(),
    )

    comparison_df = pd.DataFrame(
        {
            "Session Progress (%)": normalized_progress,
            first_session_name: first_normalized_speed,
            second_session_name: second_normalized_speed,
        }
    )

    return comparison_df.set_index(
        "Session Progress (%)"
    )


def describe_comparison_change(
    difference,
    unit="",
    decimals=2,
):
    """
    Format a positive, negative, or unchanged difference.
    """

    if difference > 0:
        prefix = "+"

    else:
        prefix = ""

    return (
        f"{prefix}{difference:.{decimals}f}"
        f"{unit}"
    )


def display_metric_chart(
    dataframe,
    raw_column,
    rolling_column,
    title,
    y_axis_label,
):
    """
    Display raw and rolling metric lines.
    """

    required_columns = [
        "StrokeNumber",
        raw_column,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        st.warning(
            f"{title} cannot be displayed. "
            f"Missing columns: {missing_columns}"
        )
        return

    chart_columns = [
        raw_column
    ]

    if (
        rolling_column
        and rolling_column
        in dataframe.columns
    ):
        chart_columns.append(
            rolling_column
        )

    chart_df = (
        dataframe[
            [
                "StrokeNumber",
                *chart_columns,
            ]
        ]
        .dropna()
        .set_index(
            "StrokeNumber"
        )
    )

    st.subheader(
        title
    )

    st.line_chart(
        chart_df,
    )

    st.caption(
        y_axis_label
    )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title(
    "Session Controls"
)

st.sidebar.markdown("---")

st.sidebar.subheader(
    "Analyze New Session"
)

uploaded_file = st.sidebar.file_uploader(
    "Upload SpeedCoach CSV",
    type=["csv"],
)

if uploaded_file is not None:

    st.sidebar.success(
        uploaded_file.name
    )

    if st.sidebar.button(
        "🚀 Analyze Uploaded Session"
    ):

        with st.spinner(
            "Analyzing uploaded session..."
        ):

            with tempfile.TemporaryDirectory() as temp_dir:

                temporary_csv = (
                    Path(temp_dir)
                    / uploaded_file.name
                )

                temporary_csv.write_bytes(
                    uploaded_file.getvalue()
                )

                process_session(
                    session_file=temporary_csv,
                    show_full_results=False,
                )

                st.session_state["selected_session"] = uploaded_file.name

        st.success(
            "Analysis complete!"
        )

        st.session_state["selected_session"] = uploaded_file.name

        st.experimental_rerun()

import tempfile

st.sidebar.markdown("---")
st.sidebar.subheader("Analyze New Session")

uploaded_file = st.sidebar.file_uploader(
    "Upload a SpeedCoach CSV",
    type=["csv"],
)

analyze_uploaded = False

if uploaded_file is not None:
    st.sidebar.info(
        f"Selected: {uploaded_file.name}"
    )

    analyze_uploaded = st.sidebar.button(
        "🚀 Analyze Uploaded Session"
    )

if analyze_uploaded:

    with st.spinner("Analyzing uploaded session..."):

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_csv = (
                Path(temp_dir)
                / uploaded_file.name
            )

            temp_csv.write_bytes(
                uploaded_file.getvalue()
            )

            from pipeline.real_data_pipeline import (
                RealDataPipeline,
            )

            pipeline = RealDataPipeline()

            pipeline.process_session(
                temp_csv
            )

    st.success("Analysis complete!")

    st.experimental_rerun()

completed_sessions = (
    find_completed_sessions()
)

if not completed_sessions:
    st.error(
        "No completed sessions were found in "
        "`outputs/sessions`."
    )

    st.info(
        "Run `python3 main.py` and analyze at least "
        "one session before opening the dashboard."
    )

    st.stop()


session_directory_by_name = {
    get_session_display_name(
        session_directory
    ): session_directory
    for session_directory
    in completed_sessions
}

session_names = list(
    session_directory_by_name.keys()
)

dashboard_mode = st.sidebar.radio(
    "Dashboard View",
    options=[
        "Single Session",
        "Compare Sessions",
    ],
)

st.sidebar.markdown("---")

default_index = 0

if "selected_session" in st.session_state:

    uploaded_name = st.session_state["selected_session"]

    if uploaded_name in session_names:
        default_index = session_names.index(uploaded_name)

default_index = 0

if "selected_session" in st.session_state:

    session = st.session_state["selected_session"]

    if session in session_names:
        default_index = session_names.index(session)

selected_session_name = st.sidebar.selectbox(
    "Primary session",
    options=session_names,
    index=default_index,
)

selected_session_directory = (
    session_directory_by_name[
        selected_session_name
    ]
)

comparison_session_name = None
comparison_session_directory = None

if dashboard_mode == "Compare Sessions":
    comparison_options = [
        session_name
        for session_name in session_names
        if session_name != selected_session_name
    ]

    if comparison_options:
        comparison_session_name = (
            st.sidebar.selectbox(
                "Comparison session",
                options=comparison_options,
            )
        )

        comparison_session_directory = (
            session_directory_by_name[
                comparison_session_name
            ]
        )

    else:
        st.sidebar.warning(
            "At least two completed sessions are "
            "required for comparison."
        )

st.sidebar.write(
    f"Completed sessions: "
    f"{len(completed_sessions)}"
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "The dashboard reads previously generated "
    "analysis files. It does not alter the "
    "underlying rowing data."
)


# ---------------------------------------------------------
# LOAD SELECTED SESSION
# ---------------------------------------------------------

try:
    (
        summary_df,
        stroke_df,
        coach_report,
    ) = load_session_data(
        str(
            selected_session_directory
        )
    )

except Exception as error:
    st.error(
        "The selected session could not be loaded."
    )

    st.exception(
        error
    )

    st.stop()

comparison_summary_df = None
comparison_stroke_df = None
comparison_coach_report = None

if (
    dashboard_mode == "Compare Sessions"
    and comparison_session_directory is not None
):
    try:
        (
            comparison_summary_df,
            comparison_stroke_df,
            comparison_coach_report,
        ) = load_session_data(
            str(
                comparison_session_directory
            )
        )

    except Exception as error:
        st.error(
            "The comparison session could not be loaded."
        )

        st.exception(
            error
        )

        st.stop()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title(
    "🚣 Rowing Performance Analyzer"
)

st.subheader(
    selected_session_name
)

st.write(
    "Interactive analysis of rowing speed, "
    "stroke rate, stroke effectiveness, "
    "performance scoring, and sustained decline."
)

st.markdown("---")

st.subheader(
    "Coach's Quick Summary"
)

(
    quick_summary_type,
    quick_summary_text,
) = create_coach_quick_summary(
    summary_df
)

if quick_summary_type == "success":
    st.success(
        quick_summary_text
    )

elif quick_summary_type == "warning":
    st.warning(
        quick_summary_text
    )

else:
    st.info(
        quick_summary_text
    )

# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------

session_score = get_summary_value(
    summary_df,
    "SessionScore",
    0.0,
)

session_rating = get_summary_value(
    summary_df,
    "SessionRating",
    "Not available",
)

valid_strokes = get_summary_value(
    summary_df,
    "ValidStrokes",
    len(stroke_df),
)

duration_minutes = get_summary_value(
    summary_df,
    "DurationMinutes",
    0.0,
)

distance_meters = get_summary_value(
    summary_df,
    "DistanceMeters",
    0.0,
)

average_speed = get_summary_value(
    summary_df,
    "AverageSpeedMetersPerSecond",
    0.0,
)

average_stroke_rate = get_summary_value(
    summary_df,
    "AverageStrokeRate",
    0.0,
)

average_distance_per_stroke = (
    get_summary_value(
        summary_df,
        "AverageDistancePerStroke",
        0.0,
    )
)

fatigue_detected = get_summary_value(
    summary_df,
    "FatigueDetected",
    False,
)

fatigue_confidence_rating = (
    get_summary_value(
        summary_df,
        "FatigueConfidenceRating",
        "Not available",
    )
)

metric_column_1, metric_column_2, metric_column_3, metric_column_4 = (
    st.columns(
        4
    )
)

with metric_column_1:
    st.metric(
        "Session Score",
        f"{float(session_score):.1f}/100",
    )

    st.caption(
        f"Rating: {session_rating}"
    )

with metric_column_2:
    st.metric(
        "Valid Strokes",
        f"{int(valid_strokes)}",
    )

    st.caption(
        f"Duration: "
        f"{float(duration_minutes):.1f} min"
    )

with metric_column_3:
    st.metric(
        "Average Speed",
        f"{float(average_speed):.2f} m/s",
    )

    st.caption(
        f"Distance: "
        f"{float(distance_meters):.0f} m"
    )

with metric_column_4:
    st.metric(
        "Fatigue Detected",
        format_yes_no(
            fatigue_detected
        ),
    )

    st.caption(
        str(
            fatigue_confidence_rating
        )
    )

secondary_column_1, secondary_column_2 = (
    st.columns(
        2
    )
)

with secondary_column_1:
    st.metric(
        "Average Stroke Rate",
        f"{float(average_stroke_rate):.1f} spm",
    )

with secondary_column_2:
    st.metric(
        "Average Distance per Stroke",
        (
            f"{float(average_distance_per_stroke):.2f} m"
        ),
    )
if (
    dashboard_mode == "Compare Sessions"
    and comparison_summary_df is not None
):
    st.markdown("---")

    st.subheader(
        "Quick Comparison"
    )

    primary_metrics = create_metric_dictionary(
        summary_df
    )

    comparison_metrics = create_metric_dictionary(
        comparison_summary_df
    )

    score_change = (
        primary_metrics["Session Score"]
        - comparison_metrics["Session Score"]
    )

    speed_change = (
        primary_metrics["Average Speed (m/s)"]
        - comparison_metrics["Average Speed (m/s)"]
    )

    rate_change = (
        primary_metrics["Average Stroke Rate (spm)"]
        - comparison_metrics["Average Stroke Rate (spm)"]
    )

    dps_change = (
        primary_metrics[
            "Average Distance per Stroke (m)"
        ]
        - comparison_metrics[
            "Average Distance per Stroke (m)"
        ]
    )

    comparison_column_1, comparison_column_2, comparison_column_3, comparison_column_4 = (
        st.columns(
            4
        )
    )

    with comparison_column_1:
        st.metric(
            "Score Difference",
            describe_comparison_change(
                score_change,
                decimals=1,
            ),
        )

    with comparison_column_2:
        st.metric(
            "Speed Difference",
            describe_comparison_change(
                speed_change,
                unit=" m/s",
                decimals=2,
            ),
        )

    with comparison_column_3:
        st.metric(
            "Stroke Rate Difference",
            describe_comparison_change(
                rate_change,
                unit=" spm",
                decimals=1,
            ),
        )

    with comparison_column_4:
        st.metric(
            "DPS Difference",
            describe_comparison_change(
                dps_change,
                unit=" m",
                decimals=2,
            ),
        )

    st.caption(
        f"Values show {selected_session_name} "
        f"minus {comparison_session_name}."
    )

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

if dashboard_mode == "Compare Sessions":
    (
        overview_tab,
        comparison_tab,
        performance_tab,
        fatigue_tab,
        report_tab,
        data_tab,
    ) = st.tabs(
        [
            "Overview",
            "Session Comparison",
            "Performance Charts",
            "Fatigue Analysis",
            "Coach Report",
            "Stroke Data",
        ]
    )

else:
    (
        overview_tab,
        performance_tab,
        fatigue_tab,
        report_tab,
        data_tab,
    ) = st.tabs(
        [
            "Overview",
            "Performance Charts",
            "Fatigue Analysis",
            "Coach Report",
            "Stroke Data",
        ]
    )

    comparison_tab = None


# ---------------------------------------------------------
# OVERVIEW TAB
# ---------------------------------------------------------

with overview_tab:
    st.header(
        "Session Overview"
    )

    overview_column_1, overview_column_2 = (
        st.columns(
            2
        )
    )

    strongest_area = get_summary_value(
        summary_df,
        "StrongestArea",
        "Not available",
    )

    strongest_area_score = get_summary_value(
        summary_df,
        "StrongestAreaScore",
        0.0,
    )

    weakest_area = get_summary_value(
        summary_df,
        "WeakestArea",
        "Not available",
    )

    weakest_area_score = get_summary_value(
        summary_df,
        "WeakestAreaScore",
        0.0,
    )

    with overview_column_1:
        st.success(
            "Strongest Area"
        )

        st.write(
            f"**{strongest_area}**"
        )

        st.write(
            f"Score: "
            f"{float(strongest_area_score):.1f}/100"
        )

    with overview_column_2:
        st.warning(
            "Primary Area to Improve"
        )

        st.write(
            f"**{weakest_area}**"
        )

        st.write(
            f"Score: "
            f"{float(weakest_area_score):.1f}/100"
        )

    st.markdown("---")

    st.subheader(
        "Session Summary Table"
    )

    st.dataframe(
        summary_df
    )


# ---------------------------------------------------------
# SESSION COMPARISON TAB
# ---------------------------------------------------------

if (
    comparison_tab is not None
    and comparison_summary_df is not None
    and comparison_stroke_df is not None
):
    with comparison_tab:
        st.header(
            "Session Comparison"
        )

        st.write(
            f"Comparing **{selected_session_name}** "
            f"against **{comparison_session_name}**."
        )

        primary_score = safe_float(
            get_summary_value(
                summary_df,
                "SessionScore",
                0.0,
            )
        )

        comparison_score = safe_float(
            get_summary_value(
                comparison_summary_df,
                "SessionScore",
                0.0,
            )
        )

        primary_fatigue = format_yes_no(
            get_summary_value(
                summary_df,
                "FatigueDetected",
                False,
            )
        )

        comparison_fatigue = format_yes_no(
            get_summary_value(
                comparison_summary_df,
                "FatigueDetected",
                False,
            )
        )

        first_summary_column, second_summary_column = (
            st.columns(
                2
            )
        )

        with first_summary_column:
            st.subheader(
                selected_session_name
            )

            st.metric(
                "Session Score",
                f"{primary_score:.1f}/100",
            )

            st.write(
                f"Fatigue detected: "
                f"**{primary_fatigue}**"
            )

            st.write(
                "Strongest area: "
                f"**{get_summary_value(summary_df, 'StrongestArea', 'Not available')}**"
            )

            st.write(
                "Improvement area: "
                f"**{get_summary_value(summary_df, 'WeakestArea', 'Not available')}**"
            )

        with second_summary_column:
            st.subheader(
                comparison_session_name
            )

            st.metric(
                "Session Score",
                f"{comparison_score:.1f}/100",
            )

            st.write(
                f"Fatigue detected: "
                f"**{comparison_fatigue}**"
            )

            st.write(
                "Strongest area: "
                f"**{get_summary_value(comparison_summary_df, 'StrongestArea', 'Not available')}**"
            )

            st.write(
                "Improvement area: "
                f"**{get_summary_value(comparison_summary_df, 'WeakestArea', 'Not available')}**"
            )

        st.markdown("---")

        st.subheader(
            "Metric Comparison"
        )

        comparison_table = create_comparison_table(
            first_summary_df=summary_df,
            second_summary_df=comparison_summary_df,
            first_session_name=selected_session_name,
            second_session_name=comparison_session_name,
        )

        formatted_comparison_table = (
            comparison_table.copy()
        )

        numeric_columns = [
            selected_session_name,
            comparison_session_name,
            "Change",
        ]

        for column_name in numeric_columns:
            formatted_comparison_table[
                column_name
            ] = formatted_comparison_table[
                column_name
            ].round(
                2
            )

        st.dataframe(
            formatted_comparison_table
        )

        comparison_csv = (
            comparison_table
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )

        st.download_button(
            label="Download Comparison CSV",
            data=comparison_csv,
            file_name=(
                f"{selected_session_name}"
                f"_vs_{comparison_session_name}"
                "_comparison.csv"
            ),
            mime="text/csv",
        )

        st.markdown("---")

        st.subheader(
            "Speed Across Session Progress"
        )

        normalized_speed_df = (
            create_normalized_speed_comparison(
                first_stroke_df=stroke_df,
                second_stroke_df=comparison_stroke_df,
                first_session_name=selected_session_name,
                second_session_name=comparison_session_name,
            )
        )

        if normalized_speed_df is not None:
            st.line_chart(
                normalized_speed_df
            )

            st.caption(
                "Both sessions are placed on a common "
                "0–100% progress scale so sessions with "
                "different stroke counts can be compared."
            )

        else:
            st.warning(
                "There is not enough valid speed data "
                "to create the comparison chart."
            )

        st.markdown("---")

        st.subheader(
            "Comparison Interpretation"
        )

        score_difference = (
            primary_score
            - comparison_score
        )

        if abs(score_difference) < 0.5:
            st.info(
                "The two sessions received nearly "
                "identical overall scores."
            )

        elif score_difference > 0:
            st.success(
                f"{selected_session_name} scored "
                f"{score_difference:.1f} points higher "
                f"than {comparison_session_name}."
            )

        else:
            st.warning(
                f"{comparison_session_name} scored "
                f"{abs(score_difference):.1f} points "
                f"higher than {selected_session_name}."
            )

        primary_metrics = create_metric_dictionary(
            summary_df
        )

        comparison_metrics = create_metric_dictionary(
            comparison_summary_df
        )

        speed_difference = (
            primary_metrics[
                "Average Speed (m/s)"
            ]
            - comparison_metrics[
                "Average Speed (m/s)"
            ]
        )

        dps_difference = (
            primary_metrics[
                "Average Distance per Stroke (m)"
            ]
            - comparison_metrics[
                "Average Distance per Stroke (m)"
            ]
        )

        if speed_difference > 0:
            speed_statement = (
                f"The primary session was "
                f"{speed_difference:.2f} m/s faster "
                "on average."
            )

        elif speed_difference < 0:
            speed_statement = (
                f"The primary session was "
                f"{abs(speed_difference):.2f} m/s slower "
                "on average."
            )

        else:
            speed_statement = (
                "The two sessions had the same "
                "average speed."
            )

        if dps_difference > 0:
            dps_statement = (
                f"Distance per stroke was "
                f"{dps_difference:.2f} m higher "
                "in the primary session."
            )

        elif dps_difference < 0:
            dps_statement = (
                f"Distance per stroke was "
                f"{abs(dps_difference):.2f} m lower "
                "in the primary session."
            )

        else:
            dps_statement = (
                "The two sessions had the same "
                "average distance per stroke."
            )

        st.write(
            f"- {speed_statement}\n"
            f"- {dps_statement}\n"
            f"- Primary-session fatigue detected: "
            f"**{primary_fatigue}**\n"
            f"- Comparison-session fatigue detected: "
            f"**{comparison_fatigue}**"
        )

# ---------------------------------------------------------
# PERFORMANCE CHARTS TAB
# ---------------------------------------------------------

with performance_tab:
    st.header(
        "Performance Charts"
    )

    display_metric_chart(
        dataframe=stroke_df,
        raw_column="Speed",
        rolling_column="RollingSpeed",
        title="Boat Speed",
        y_axis_label=(
            "Speed measured in meters per second."
        ),
    )

    display_metric_chart(
        dataframe=stroke_df,
        raw_column="StrokeRate",
        rolling_column="RollingStrokeRate",
        title="Stroke Rate",
        y_axis_label=(
            "Stroke rate measured in strokes per minute."
        ),
    )

    display_metric_chart(
        dataframe=stroke_df,
        raw_column="DistancePerStroke",
        rolling_column=(
            "RollingDistancePerStroke"
        ),
        title="Distance per Stroke",
        y_axis_label=(
            "Distance traveled per stroke in meters."
        ),
    )

    if (
        "StrokeNumber"
        in stroke_df.columns
        and "StrokeScore"
        in stroke_df.columns
    ):
        st.subheader(
            "Stroke Performance Score"
        )

        stroke_score_chart = (
            stroke_df[
                [
                    "StrokeNumber",
                    "StrokeScore",
                ]
            ]
            .dropna()
            .set_index(
                "StrokeNumber"
            )
        )

        st.line_chart(
            stroke_score_chart,
        )

        st.caption(
            "Relative per-stroke performance score "
            "on a 0–100 scale."
        )


# ---------------------------------------------------------
# FATIGUE TAB
# ---------------------------------------------------------

with fatigue_tab:
    st.header(
        "Fatigue and Sustained Decline"
    )

    fatigue_column_1, fatigue_column_2, fatigue_column_3 = (
        st.columns(
            3
        )
    )

    fatigue_confidence = get_summary_value(
        summary_df,
        "FatigueConfidence",
        0.0,
    )

    maximum_fatigue_severity = (
        get_summary_value(
            summary_df,
            "MaximumFatigueSeverity",
            0.0,
        )
    )

    fatigue_start_stroke = get_summary_value(
        summary_df,
        "FatigueStartStroke",
        None,
    )

    with fatigue_column_1:
        st.metric(
            "Fatigue Detected",
            format_yes_no(
                fatigue_detected
            ),
        )

    with fatigue_column_2:
        st.metric(
            "Confidence",
            f"{float(fatigue_confidence):.1f}%",
        )

    with fatigue_column_3:
        if fatigue_start_stroke is None:
            fatigue_start_display = (
                "Not detected"
            )
        else:
            fatigue_start_display = (
                str(
                    int(
                        fatigue_start_stroke
                    )
                )
            )

        st.metric(
            "Estimated Start Stroke",
            fatigue_start_display,
        )

    st.write(
        "Confidence rating: "
        f"**{fatigue_confidence_rating}**"
    )

    if (
        maximum_fatigue_severity
        is not None
    ):
        st.write(
            "Maximum estimated decline severity: "
            f"**{float(maximum_fatigue_severity):.2f}**"
        )

    if (
        "StrokeNumber"
        in stroke_df.columns
        and "FatigueSeverity"
        in stroke_df.columns
    ):
        fatigue_chart = (
            stroke_df[
                [
                    "StrokeNumber",
                    "FatigueSeverity",
                ]
            ]
            .dropna()
            .set_index(
                "StrokeNumber"
            )
        )

        st.subheader(
            "Estimated Decline Trend"
        )

        st.area_chart(
            fatigue_chart,
        )

    st.info(
        "This fatigue result estimates sustained "
        "performance decline relative to the athlete's "
        "early-session baseline. It is not a medical "
        "measurement."
    )


# ---------------------------------------------------------
# COACH REPORT TAB
# ---------------------------------------------------------

with report_tab:
    st.header(
        "Coach Report"
    )

    st.code(
        coach_report,
        language=None,
    )

    report_file = (
        selected_session_directory
        / "reports"
        / "coach_report.txt"
    )

    if report_file.exists():
        st.download_button(
            label="Download Coach Report",
            data=report_file.read_bytes(),
            file_name=(
                f"{selected_session_name}"
                "_coach_report.txt"
            ),
            mime="text/plain",
        )


# ---------------------------------------------------------
# STROKE DATA TAB
# ---------------------------------------------------------

with data_tab:
    st.header(
        "Stroke-Level Data"
    )

    st.write(
        f"Rows: **{len(stroke_df)}**"
    )

    available_columns = (
        stroke_df.columns.tolist()
    )

    default_columns = [
        column
        for column in [
            "StrokeNumber",
            "Time",
            "Distance",
            "Speed",
            "StrokeRate",
            "DistancePerStroke",
            "StrokeScore",
            "FatigueSeverity",
            "SessionSegment",
            "SessionPhase",
        ]
        if column in available_columns
    ]

    selected_columns = (
        st.multiselect(
            "Choose columns to display",
            options=available_columns,
            default=default_columns,
        )
    )

    if selected_columns:
        displayed_df = stroke_df[
            selected_columns
        ]
    else:
        displayed_df = stroke_df

    search_text = st.text_input(
        "Search the displayed table"
    )

    if search_text:
        row_matches = (
            displayed_df
            .astype(str)
            .apply(
                lambda column: (
                    column.str.contains(
                        search_text,
                        case=False,
                        na=False,
                    )
                )
            )
            .any(
                axis=1
            )
        )

        displayed_df = displayed_df[
            row_matches
        ]

    st.dataframe(
        displayed_df,
        height=550,
    )

    stroke_csv = stroke_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )

    st.download_button(
        label="Download Stroke Analysis CSV",
        data=stroke_csv,
        file_name=(
            f"{selected_session_name}"
            "_stroke_analysis.csv"
        ),
        mime="text/csv",
    )