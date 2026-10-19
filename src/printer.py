import numpy as np
from src.printer_states import *
import control as ct
import yaml
import matplotlib.pyplot as plt
from src.kinematics import *
from scipy.integrate import solve_ivp


class Printer(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level.
    """

    t = 0
    dt = 0.1
    filament_loaded_flag = False
    filament_retracted_flag = False
    filament_empty_flag = False
    filament_color_change_flag = False
    wiping_done = False
    h_flag = False
    v_flag = False
    target_points = [(10, 10), (100, 10), (100, 100), (10, 100), (10, 10)]
    visited_points = []
    x = np.zeros(9)
    u = np.ones(3)
    simulation_events = []
    filament_used = 0
    
    c = yaml.safe_load(open("src/constant.yaml"))
    J_eq = c["J_m"] + 0.5 * c["m"] * c["r_m"] ** 2
    t_target_on = c["T_n"]
    t_target_off = 40
    
    A = np.array(
        [
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, c["K_m"] / J_eq, 0],
            [0, 0, 0, 0, 0, c["K_m"] / J_eq],
            [0, 0, -c["K_m"] / c["L_m"], 0, -c["R_m"] / c["L_m"], 0],
            [0, 0, 0, -c["K_m"] / c["L_m"], 0, -c["R_m"] / c["L_m"]],
        ]
    )

    B = np.array(
        [[0, 0], [0, 0], [0, 0], [0, 0], [1.0 / c["L_m"], 0], [0, 1.0 / c["L_m"]]]
    )

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
        return to_corexy(self.x[0], self.x[1], self.c["r_m"])[0]

    def get_y(self):
        return to_corexy(self.x[0], self.x[1], self.c["r_m"])[1]

    def add_sim_event(self, event, value, time_delay):
        self.simulation_events.append((event, value, time_delay))

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


    def process_sim_events(self):
        for event, value, time_delay in self.simulation_events:
            if self.t >= time_delay:
                self.on_event(event, value)
                self.simulation_events.remove((event, value, time_delay))

    def run(self, duration):
        while self.t < duration:
            self.step()
            self.process_sim_events()
            self.tick()
            self.add_telemetry()

    def add_telemetry(self):
        x, y = to_corexy(self.x[0], self.x[1], self.c["r_m"])
        temp = self.x[6]
        self.visited_points.append([x, y, temp, self.t, self.filament_used])
        

    def plot(self):
        pts = np.array(self.visited_points)
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 4))
        ax1.plot(pts[:, 0], pts[:, 1])
        ax2.plot(pts[:, 3], pts[:, 2])
        ax3.plot(pts[:, 3], pts[:, 4])
        plt.show()

    def sys(self, t, x, u):
        # dx = self.A @ x + self.B @ u
        dx = np.zeros(9)
        dx[:6] = self.A @ x[:6] + self.B @ u[:2]
        T, v, i = x[6], x[7], x[8]
        dx[6] = v**2 / (self.c["C_t_n"] * self.c["R_n"]) - (T - self.c["T_e"]) / (
            self.c["C_t_n"] * self.c["R_t_n"]
        )
        dx[7] = i / self.c["C_n"] - v / (self.c["C_n"] * self.c["R_n"])
        dx[8] = u[2] / self.c["L_n"] - v / self.c["L_n"]
        return dx

    def step(self):
        sol = solve_ivp(
            self.sys, (self.t, self.t + self.dt), self.x, args=(self.u,), method="LSODA"
        )
        self.x = sol.y[:, -1]
        self.t += self.dt
        self.printbed_guard()
        self.filament_usage()

    def printbed_guard(self):
        self.h_flag = False
        self.v_flag = False
        x, y = to_corexy(self.x[0], self.x[1], self.c["r_m"])
        x_guard = np.clip(x, 0, self.c["d_x"])
        y_guard = np.clip(y, 0, self.c["d_y"])
        if x != x_guard or y != y_guard:
            self.x[0], self.x[1] = to_motor(x_guard, y_guard, self.c["r_m"])
            vel_x, vel_y = to_corexy(self.x[2], self.x[3], self.c["r_m"])
            if x != x_guard:
                vel_x = 0
                self.v_flag = True
            if y != y_guard:
                vel_y = 0
                self.h_flag = True
            self.x[2], self.x[3] = to_motor(vel_x, vel_y, self.c["r_m"])
    
    # not extremly accurate since it might not actually be in Printing state at that point but step -1 or +1
    def filament_usage(self):
        if isinstance(self.state, PrintingState) and len(self.visited_points) > 2:
            x0, y0 = self.visited_points[-2][:2]
            x1, y1 = self.visited_points[-1][:2]
            self.filament_used += np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        
        
    def feedback(self, x_ref, y_ref, heating, kp=0.1):
        # For now ill try with a p controller
        theta_l, theta_r = to_motor(x_ref, y_ref, self.c["r_m"])
        e_l = theta_l - self.x[0]
        e_r = theta_r - self.x[1]

        heating_value = 0
        temp_at_target = False
        if heating:
            if self.x[6] < self.t_target_on:
                heating_value = 40
            else:
                temp_at_target = True
        else:
            if self.x[6] < self.t_target_off:
                temp_at_target = True

        self.u = np.array([kp * e_l, kp * e_r, heating_value])
        return abs(e_l) < 1e-3 and abs(e_r) < 1e-3 and temp_at_target


if __name__ == "__main__":
    printer = Printer()
    printer.add_sim_event("C", True, printer.t + 20)
    printer.add_sim_event("F", True, printer.t + 100)

    printer.run(200)
    printer.plot()
