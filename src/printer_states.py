

from state import State

# Start of our states
class PrintingState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, printer, event):
        if event == 'C' or event == 'F':
            printer.flag = event
            return StoppedState()
        return self

class StoppedState(State):
    def on_tick(self, printer):
        printer.x_saved = printer.get_x()
        printer.y_saved = printer.get_y()
        return ToTowerState()

class ToTowerState(State):
    def on_tick(self, printer):
        if printer.get_x() == 0 and printer.get_y() == 0:
            print('Cooling Nozzle')
            return WipingState()
        return self
    
class WipingState(State):
    def on_event(self, printer, event):
        if event == 'wipping_finished' and printer.flag == 'C':
            printer.flag = 'none'
            return RetractFilamentState()
        elif event == 'wipping_finished' and printer.flag == 'F':
            printer.flag = 'none'
            return CoolingNozzleState()
        return self
    
class RetractFilamentState(State):
    def on_event(self, printer, event):
        if event == 'retracted':
            return CoolingNozzleState()
        return self

class CoolingNozzleState(State):
    def on_tick(self, printer):
        if printer.get_temperature() <= 30:
            return LoadFilamentState()
        return self
    
class LoadFilamentState(State):
    def on_event(self, printer, event):
        if event == 'loaded':
            return HeatingNozzleState()
        return self

class HeatingNozzleState(State):
    def on_tick(self, printer):
        if printer.get_temperature() >= 220:
            return ResumeState()
        return self

class ResumeState(State):
    def on_tick(self, printer):
        if printer.get_x() == printer.x_saved and printer.get_y() == printer.y_saved:
            return PrintingState()
        return self