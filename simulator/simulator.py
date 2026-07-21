import numpy as np
import pandas as pd

from config.settings import *


class RowingSimulator:

    def __init__(self):

        np.random.seed(RANDOM_SEED)

    def generate(self):

        t = np.arange(
            0,
            SIMULATION_DURATION,
            TIME_STEP
        )

        stroke_period = 60 / STROKE_RATE

        speed = np.zeros(len(t))

        speed[0] = AVERAGE_SPEED

        drive_fraction = 0.38

        for i in range(1, len(t)):

            phase = (t[i] % stroke_period) / stroke_period

            if phase < drive_fraction:

                accel = (
                    3.2
                    * np.sin(
                        np.pi * phase / drive_fraction
                    )
                )

            else:

                accel = -TRUE_DRAG * speed[i - 1] ** 2

            speed[i] = speed[i - 1] + accel * TIME_STEP

            if speed[i] < 0.5:
                speed[i] = 0.5

        speed += np.random.normal(
            0,
            NOISE_LEVEL,
            len(speed)
        )

        df = pd.DataFrame({

            "Time": t,

            "Speed": speed

        })

        return df