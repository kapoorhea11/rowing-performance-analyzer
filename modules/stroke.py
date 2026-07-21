from dataclasses import dataclass


@dataclass
class Stroke:

    number: int

    start_time: float

    end_time: float

    duration: float

    peak_speed: float

    min_speed: float

    mean_speed: float

    peak_acceleration: float

    peak_jerk: float

    speed_loss: float