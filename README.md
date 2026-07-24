# 🚣 Rowing Performance Analyzer

A Python-based rowing analytics platform that transforms raw GPS rowing session data into detailed performance metrics, fatigue analysis, coaching insights, and an interactive dashboard.

This project automatically processes rowing session CSV files, identifies individual strokes, evaluates rowing technique and consistency, detects fatigue trends, generates visualizations, and produces coach-style reports for athletes and coaches.

---

## Features

- Automatic SpeedCoach CSV import
- Data validation and cleaning
- Stroke detection and segmentation
- Stroke-by-stroke performance analysis
- Boat speed analysis
- Stroke rate analysis
- Distance-per-stroke calculations
- Session segmentation
- Fatigue detection
- Session scoring (0–100)
- Coach report generation
- Automatic graphs
- Interactive Streamlit dashboard
- Multi-session comparison
- Downloadable reports

---

# Dashboard

The Streamlit dashboard provides an interactive interface for exploring rowing performance.

### Dashboard Features

- Session selector
- Compare multiple sessions
- Performance score cards
- Speed trends
- Stroke rate trends
- Distance per stroke
- Fatigue analysis
- Coach summary
- Stroke-by-stroke data table
- CSV downloads
- Report downloads

---

# Project Structure

```
rowing-performance-analyzer/
│
├── config/
│
├── dashboard/
│   └── app.py
│
├── data/
│   └── sessions/
│
├── loaders/
│
├── modules/
│
├── outputs/
│   └── sessions/
│
├── pipeline/
│
├── simulator/
│
├── utils/
│
├── visualizations/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# Analysis Pipeline

The analysis pipeline consists of several stages:

```
SpeedCoach CSV

        │

        ▼

Data Validation

        │

        ▼

Data Cleaning

        │

        ▼

Stroke Detection

        │

        ▼

Stroke Analysis

        │

        ▼

Session Segmentation

        │

        ▼

Fatigue Detection

        │

        ▼

Performance Scoring

        │

        ▼

Coach Report Generation

        │

        ▼

Graphs + Dashboard + Reports
```

---

# Session Outputs

Each processed rowing session generates:

```
outputs/
└── sessions/
    └── session_name/
        ├── data/
        │   ├── stroke_analysis.csv
        │   └── session_summary.csv
        │
        ├── figures/
        │   ├── boat_speed.png
        │   ├── stroke_rate.png
        │   ├── distance_per_stroke.png
        │   ├── stroke_score.png
        │   └── fatigue_trend.png
        │
        ├── reports/
        │   └── coach_report.txt
        │
        └── source_file.txt
```

---

# Performance Metrics

The analyzer evaluates multiple aspects of rowing performance, including:

- Boat speed
- Stroke rate
- Distance per stroke
- Stroke duration
- Stroke consistency
- Session consistency
- Fatigue progression
- Segment performance
- Overall session quality

---

# Session Score

Each rowing session receives an overall score from **0–100** based on several weighted performance metrics.

The scoring system evaluates:

- Speed retention
- Distance per stroke
- Rhythm control
- Speed consistency

The resulting score is summarized as a coach-friendly overall rating.

---

# Fatigue Detection

The fatigue detection algorithm analyzes changes in rowing performance throughout the session.

Metrics evaluated include:

- Speed decline
- Stroke efficiency
- Distance per stroke
- Segment-to-segment trends

The system determines whether sustained fatigue is present and provides a confidence assessment.

---

# Coach Report

A coaching report is automatically generated for every session.

The report includes:

- Overall session rating
- Session score
- Strongest performance area
- Primary improvement opportunity
- Fatigue assessment
- Personalized coaching recommendation

---

# Interactive Dashboard

The Streamlit dashboard enables coaches and athletes to explore session data visually.

Included views:

- Overview
- Performance Charts
- Fatigue Analysis
- Coach Report
- Stroke Data
- Session Comparison

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/rowing-performance-analyzer.git

cd rowing-performance-analyzer
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Analyzer

Analyze rowing sessions:

```bash
python3 main.py
```

The program automatically processes selected SpeedCoach CSV files and generates analysis results.

---

# Running the Dashboard

Launch the Streamlit dashboard:

```bash
python3 -m streamlit run dashboard/app.py
```

Open:

```
http://localhost:8501
```

---

# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Streamlit

---

# Future Improvements

Potential future enhancements include:

- Heart rate integration
- Machine learning performance prediction
- Athlete benchmarking
- Crew synchronization analysis
- Live telemetry support
- Cloud-based data storage
- Mobile dashboard
- Seasonal trend analysis

---

# License

This project is intended for educational and research purposes.

---

# Author

Developed as an independent software engineering project focused on sports analytics, rowing biomechanics, and performance visualization.