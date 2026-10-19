from printer_states import *
import time


class Printer(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level.
    """

    filament_loaded_flag = False
    filament_retracted_flag = False
    filament_empty_flag = False
    filament_color_change_flag = False
    wiping_done = False
    temperature = 200
    x = 5
    y = 5
    simulation_events = []

    def __init__(self):
        self.state = PrintingState()

    def tick(self):
        new_state = self.state.on_tick(self)
        if new_state != self.state:
            self.state = new_state
            self.state.on_enter(self)
        self.state = new_state

    def get_temperature(self):
        return self.temperature

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def add_sim_event(self, event, value, time_delay):
        self.simulation_events.append((event, value, time_delay / 10))

    def on_event(self, event, value):
        if event == "C":
            self.filament_color_change_flag = value
        elif event == "F":
            self.filament_empty_flag = value
        elif event == "wiping_done":
            self.wiping_done = value
        elif event == "retracted":
            self.filament_retracted_flag = value
        elif event == "loaded":
            self.filament_loaded_flag = value
        elif event == "temperature":
            self.temperature = value
        elif event == "x":
            self.x = value
        elif event == "y":
            self.y = value

    def process_sim_events(self):
        t = time.time()
        for event, value, time_delay in self.simulation_events:
            if t >= time_delay:
                self.on_event(event, value)
                self.simulation_events.remove((event, value, time_delay))

    def run(self):
        while True:
            self.process_sim_events()
            time.sleep(0.1)
            self.tick()


if __name__ == "__main__":
    printer = Printer()
    printer.add_sim_event("C", True, time.time() + 1)
    printer.add_sim_event("F", True, time.time() + 20)

    printer.run()
