from pathlib import Path

import pandas as pd
import streamlit as st


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


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------

def find_completed_sessions():
    """
    Find session folders that contain both required CSV files.
    """

    if not SESSIONS_OUTPUT_DIRECTORY.exists():
        return []

    completed_sessions = []

    for session_directory in sorted(
        SESSIONS_OUTPUT_DIRECTORY.iterdir()
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
        use_container_width=True,
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


session_names = [
    session_directory.name
    for session_directory
    in completed_sessions
]

selected_session_name = (
    st.sidebar.selectbox(
        "Choose a rowing session",
        options=session_names,
    )
)

selected_session_directory = (
    SESSIONS_OUTPUT_DIRECTORY
    / selected_session_name
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


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title(
    "🚣 Rowing Performance Analyzer"
)

st.subheader(
    selected_session_name.replace(
        "_",
        " ",
    )
)

st.write(
    "Interactive analysis of rowing speed, "
    "stroke rate, stroke effectiveness, "
    "performance scoring, and sustained decline."
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


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

overview_tab, performance_tab, fatigue_tab, report_tab, data_tab = (
    st.tabs(
        [
            "Overview",
            "Performance Charts",
            "Fatigue Analysis",
            "Coach Report",
            "Stroke Data",
        ]
    )
)


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
        summary_df,
        use_container_width=True,
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
            use_container_width=True,
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
            use_container_width=True,
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

    st.text(
        coach_report
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
        use_container_width=True,
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