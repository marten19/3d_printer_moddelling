from src.state import State


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
        elif printer.feedback(printer.target_points[0][0],printer.target_points[0][1]):
            return NextPointState()
        return self
    

class NextPointState(State):
    def on_tick(self, printer):
        printer.target_points.pop(0)
        if len(printer.target_points) >= 1:
            return PrintingState()
        return StopIdleState()
        
class StopIdleState(State):
    def on_tick(self, printer):
            if not printer.feedback(0,0) or len(printer.target_points) < 1:
                return self
            return PrintingState()
              

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
    def on_tick(self, printer):
        if printer.feedback(0.0, 0.0):
            return WipingCState()
        return self

class ToTowerFState(State):
    def on_tick(self, printer):
        if printer.feedback(0.0, 0.0):
            return WipingFState()
        return self


class WipingCState(State):
    def on_enter(self, printer):
        printer.add_sim_event("wiping_done", True, printer.t + 1)

    def on_tick(self, printer):
        if printer.wiping_done:
            printer.wiping_done = False
            return RetractFilamentState()
        return self
        


class WipingFState(State):
    def on_enter(self, printer):
        printer.add_sim_event("wiping_done", True, printer.t + 1)

    def on_tick(self, printer):
        if printer.wiping_done:
            printer.wiping_done = False
            return CoolingNozzleState()
        return self


class RetractFilamentState(State):
    def on_enter(self, printer):
        printer.add_sim_event("retracted", True, printer.t + 1)

    def on_tick(self, printer):
        if printer.filament_retracted_flag:
            return CoolingNozzleState()
        return self


class CoolingNozzleState(State):
    def on_enter(self, printer):
        printer.add_sim_event("temperature", 20, printer.t + 1)

    def on_tick(self, printer):
        if printer.get_temperature() <= 30:
            return LoadFilamentState()
        return self


class LoadFilamentState(State):
    def on_enter(self, printer):
        printer.add_sim_event("loaded", True, printer.t + 1)

    def on_tick(self, printer):
        if printer.filament_loaded_flag:
            return HeatingNozzleState()
        return self


class HeatingNozzleState(State):
    def on_enter(self, printer):
        printer.add_sim_event("temperature", 220, printer.t + 1)

    def on_tick(self, printer):
        if printer.get_temperature() >= 220:
            return ResumeState()
        return self


class ResumeState(State):
    def on_tick(self, printer):
        if printer.feedback(printer.x_saved,printer.y_saved):
            return PrintingState()
        return self
