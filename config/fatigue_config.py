FATIGUE_CONFIG = {
    # Strokes ignored at the start of each segment.
    "startup_strokes": 10,

    # Strokes used to calculate the early-session baseline.
    "baseline_strokes": 85,

    # Minimum segment length required for fatigue analysis.
    "minimum_segment_strokes": 120,

    # Consecutive fatigue signals required for confirmation.
    "confirmation_strokes": 8,

    # Relative decline thresholds.
    "speed_decline_threshold": 0.08,
    "distance_per_stroke_decline_threshold": 0.08,

    # Supporting stroke-rate threshold.
    "stroke_rate_change_threshold": 0.12,

    # Confidence-scoring parameters.
    "high_confidence_signal_strokes": 30,
    "high_confidence_decline_multiplier": 2.0,
}