# Rowing Performance Analyzer

## Purpose

This project analyzes per-stroke NK SpeedCoach CSV data to evaluate rowing performance, identify continuous rowing segments, detect sustained fatigue-related decline, calculate stroke-quality scores, and generate coach-friendly reports and visualizations.

## Current Capabilities

- Loads NK SpeedCoach CSV data
- Cleans and standardizes per-stroke rowing data
- Calculates rowing-performance metrics
- Separates continuous rowing segments from interruptions and cooldown periods
- Detects sustained fatigue independently within each eligible segment
- Assigns fatigue-confidence ratings
- Calculates session and component scores
- Generates a written coach report
- Exports detailed CSV results
- Generates performance graphs

## Pipeline

The analysis pipeline runs in this order:

1. Data loading
2. Data standardization
3. Real stroke analysis
4. Session segmentation
5. Segment-aware fatigue detection
6. Stroke scoring
7. Coach report generation
8. Visualization generation
9. Result export

## Session Classification

Every valid stroke is assigned one of three classifications:

- `Rowing segment`
- `Short rowing segment`
- `Transition/Cooldown`

Only valid rowing segments receive a `SessionSegment` number.

Short rowing segments remain visible in the results but may be excluded from fatigue analysis if they contain fewer than the required number of strokes.

Transition and cooldown strokes are excluded from fatigue analysis so that stopping does not produce a false fatigue result.

## Fatigue Detection

Fatigue detection is performed independently within each qualifying rowing segment.

The detector:

- establishes an early-segment performance baseline
- calculates rolling rowing metrics
- measures speed and distance-per-stroke decline
- checks whether decline is sustained
- avoids carrying fatigue across interruptions
- assigns a confidence score and confidence rating

A fatigue signal is not considered confirmed unless the decline persists for the required duration.

## Current Example Result

The current SpeedCoach session contains:

- 426 valid strokes
- 399 strokes in the main rowing segment
- 12 strokes in a short rowing segment
- 15 transition/cooldown strokes
- 2 identified rowing segments
- no confirmed sustained fatigue decline
- session score of approximately 74.5/100

## Output Files

The project generates:

```text
outputs/
├── data/
│   ├── session_summary.csv
│   └── stroke_analysis.csv
├── figures/
│   ├── 01_boat_speed.png
│   ├── 02_stroke_rate.png
│   ├── 03_distance_per_stroke.png
│   ├── 04_stroke_score.png
│   └── 05_fatigue_trend.png
└── reports/
    └── coach_report.txt