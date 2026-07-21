"""
Global settings for the rowing performance analyzer.
"""

# -------------------------
# Simulation Settings
# -------------------------

SIMULATION_DURATION = 600        # seconds

STROKE_RATE = 30                 # strokes/min

TIME_STEP = 0.05                 # 20 Hz

BOAT_MASS = 114                  # kg (8+ shell + crew estimate)

AVERAGE_SPEED = 4.8              # m/s

NOISE_LEVEL = 0.03

TRUE_DRAG = 0.095

RANDOM_SEED = 42

# -------------------------
# Signal Processing
# -------------------------

SMOOTHING_WINDOW = 21

SMOOTHING_POLYORDER = 3

# -------------------------
# Stroke Detection
# -------------------------

MIN_STROKE_DISTANCE = 15

# -------------------------
# Plot Settings
# -------------------------

FIGURE_WIDTH = 12

FIGURE_HEIGHT = 6