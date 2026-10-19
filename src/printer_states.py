from src.state import State
import time


# Start of our states
class PrintingState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_tick(self, printer):
        if printer.filament_color_change_flag:
            printer.filament_color_change_flag = False
            return StopCState()
        elif printer.filament_empty_flag:
            printer.filament_empty_flag = False
            return StopCState()
        return self


class StopCState(State):
    def on_tick(self, printer):
        printer.x_saved = printer.get_x()
        printer.y_saved = printer.get_y()
        return ToTowerCState()


class StopFState(State):
    def on_tick(self, printer):
        printer.x_saved = printer.get_x()
        printer.y_saved = printer.get_y()
        return ToTowerFState()


class ToTowerCState(State):
    def on_enter(self, printer):
        printer.add_sim_event("x", 0, time.time() + 2)
        printer.add_sim_event("y", 0, time.time() + 3)

    def on_tick(self, printer):
        if printer.get_x() == 0 and printer.get_y() == 0:
            return WipingCState()
        return self


class ToTowerFState(State):
    def on_enter(self, printer):
        printer.add_sim_event("x", 0, time.time() + 2)
        printer.add_sim_event("y", 0, time.time() + 3)

    def on_tick(self, printer):
        if printer.get_x() == 0 and printer.get_y() == 0:
            return WipingFState()
        return self


class WipingCState(State):
    def on_enter(self, printer):
        printer.add_sim_event("wiping_done", True, time.time() + 1)

    def on_tick(self, printer):
        if printer.wiping_done:
            printer.wiping_done = False
            return RetractFilamentState()
        return self


class WipingFState(State):
    def on_enter(self, printer):
        printer.add_sim_event("wiping_done", True, time.time() + 1)

    def on_tick(self, printer):
        if printer.wiping_done:
            printer.wiping_done = False
            return CoolingNozzleState()
        return self


class RetractFilamentState(State):
    def on_enter(self, printer):
        printer.add_sim_event("retracted", True, time.time() + 1)

    def on_tick(self, printer):
        if printer.filament_retracted_flag:
            return CoolingNozzleState()
        return self


class CoolingNozzleState(State):
    def on_enter(self, printer):
        printer.add_sim_event("temperature", 20, time.time() + 5)

    def on_tick(self, printer):
        if printer.get_temperature() <= 30:
            return LoadFilamentState()
        return self


class LoadFilamentState(State):
    def on_enter(self, printer):
        printer.add_sim_event("loaded", True, time.time() + 1)

    def on_tick(self, printer):
        if printer.filament_loaded_flag:
            return HeatingNozzleState()
        return self


class HeatingNozzleState(State):
    def on_enter(self, printer):
        printer.add_sim_event("temperature", 220, time.time() + 5)

    def on_tick(self, printer):
        if printer.get_temperature() >= 220:
            return ResumeState()
        return self


class ResumeState(State):
    def on_enter(self, printer):
        printer.add_sim_event("x", printer.x_saved, time.time() + 2)
        printer.add_sim_event("y", printer.y_saved, time.time() + 3)

    def on_tick(self, printer):
        if printer.get_x() == printer.x_saved and printer.get_y() == printer.y_saved:
            return PrintingState()
        return self
