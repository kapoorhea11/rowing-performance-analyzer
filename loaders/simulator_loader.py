from simulator.simulator import RowingSimulator


class SimulatorLoader:

    def load(self):

        simulator = RowingSimulator()

        return simulator.generate()