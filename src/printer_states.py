from src.state import State
import numpy as np

class StartState(State):
    def on_tick(self, printer):
        printer.x_saved, printer.y_saved = printer.target_points[0] 
        if printer.filament_empty_flag:
            return ToTowerFState()
        return HeatingNozzleState()
    
class PrintingState(State):
    def on_tick(self, printer):
        if printer.filament_color_change_flag:
            printer.filament_color_change_flag = False
            return StopCState()
        elif printer.filament_empty_flag:
            return StopCState()
        elif printer.feedback(
            printer.target_points[0][0], printer.target_points[0][1], True
        ):
            return NextPointState()
        return self
    
    def filament_rate(self, printer, x):
        k = printer.c["filament_width"]**2
        v = printer.c["r_m"] / np.sqrt(2) * np.sqrt(x[2]**2 + x[3]**2)
        return -k * v


class NextPointState(State):
    def on_tick(self, printer):
        printer.target_points.pop(0)
        if len(printer.target_points) >= 1:
            return PrintingState()
        return StopIdleState()


class StopIdleState(State):
    def on_tick(self, printer):
        if not printer.feedback(0, 0, False) or len(printer.target_points) < 1:
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
    def on_enter(self, printer):
        printer.homing_flags_reset()

    def on_tick(self, printer):
        printer.feedback(-100, -100, True)
        if printer.h_flag and printer.v_flag:
            return WipingCState()
        return self


class ToTowerFState(State):
    def on_enter(self, printer):
        printer.homing_flags_reset()

    def on_tick(self, printer):
        printer.feedback(-100, -100, True)
        print(printer.x[0],printer.x[1])
        if printer.h_flag and printer.v_flag:
            return WipingFState()
        return self


class WipingCState(State):
    def on_enter(self, printer):
        printer.x[9] = 0
        
    def on_tick(self, printer):
        printer.feedback(0, 0, True)
        if printer.wiping_done:
            printer.wiping_done = False
            return RetractFilamentState()
        return self
    
    def filament_rate(self, printer, x):
        return -printer.c["V_f"]




class WipingFState(State):
    def on_enter(self, printer):
        printer.x[9] = 0
        
    def on_tick(self, printer):
        printer.feedback(0, 0, True)
        if printer.wiping_done:
            printer.wiping_done = False
            return CoolingNozzleState()
        return self
    
    def filament_rate(self, printer, x):
        return -printer.c["V_f"]



class RetractFilamentState(State):
    def on_enter(self, printer):
        printer.x[9] = 0
        
    def on_tick(self, printer):
        printer.feedback(0, 0, True)
        if printer.filament_retracted_flag:
            return CoolingNozzleState()
        return self
    
    def filament_rate(self, printer, x):
        return printer.c["V_f"]

class CoolingNozzleState(State):
    def on_tick(self, printer):
        if printer.feedback(0.0, 0.0, False):
            return LoadFilamentState()
        return self

class LoadFilamentState(State):
    def on_enter(self, printer):
        printer.x[9] = printer.new_roll
        
    def on_tick(self, printer):
        if printer.filament_loaded_flag:
            return HeatingNozzleState()
        return self
    
    def filament_rate(self, printer, x):
        return -printer.c["V_f"]
    




class HeatingNozzleState(State):
    def on_tick(self, printer):
        if printer.feedback(0.0, 0.0, True):
            return ResumeState()
        return self


class ResumeState(State):
    def on_tick(self, printer):
        if printer.feedback(printer.x_saved, printer.y_saved, True):
            return PrintingState()
        return self
