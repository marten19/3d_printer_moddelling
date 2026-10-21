import numpy as np
from src.printer_states import *
from src.kinematics import *
import yaml
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


class Printer(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level.
    """

    t = 0
    dt = 0.01
    filament_loaded_flag = False
    filament_retracted_flag = False
    filament_empty_flag = False
    filament_color_change_flag = False
    wiping_done = False
    h_flag = False
    v_flag = False
    target_points = []
    visited_points = []
    x = np.zeros(10)
    u = np.ones(3)
    simulation_events = []
    new_roll = 100
    x[9] = new_roll

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
        self.state = StartState()

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
            if isinstance(self.state, StopIdleState):
                break

    def add_telemetry(self):
        self.visited_points.append(np.append(self.x, self.t))

    def plot(self):
        print(self.visited_points[0])
        pts = np.array(self.visited_points)
        t = pts[:, 10]
        x, y = to_corexy(pts[:, 0], pts[:, 1], self.c["r_m"])

        _, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
        ax1.plot(x, y)
        ax1.set_title("Toolhead path")

        ax2.plot(t, pts[:, 6])
        ax2.set_title("Nozzle temperature")

        ax3.plot(t, pts[:, 9])
        ax3.set_title("Filament on roll")
        plt.tight_layout()
        plt.show()

    def sys(self, t, x, u):
        dx = np.zeros(10)
        dx[:6] = self.A @ x[:6] + self.B @ u[:2]
        T, v, i = x[6], x[7], x[8]
        dx[6] = v**2 / (self.c["C_t_n"] * self.c["R_n"]) - (T - self.c["T_e"]) / (
            self.c["C_t_n"] * self.c["R_t_n"]
        )
        dx[7] = i / self.c["C_n"] - v / (self.c["C_n"] * self.c["R_n"])
        dx[8] = u[2] / self.c["L_n"] - v / self.c["L_n"]
        dx[9] = self.state.filament_rate(self, x)
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

    def filament_usage(self):
        self.filament_empty_flag = self.x[9] < 0
        self.filament_retracted_flag = self.x[9] > 10
        self.filament_loaded_flag = self.x[9] < self.new_roll - 10
        self.wiping_done = self.x[9] < -10

    def feedback(self, x_ref, y_ref, heater):
        temp = self.heater(heater)
        pos = self.move_to(x_ref, y_ref)
        return pos and temp

    def move_to(self, x_ref, y_ref, kp=0.8, kd=0.05):
        theta_l, theta_r = to_motor(x_ref, y_ref, self.c["r_m"])
        e_l = theta_l - self.x[0]
        e_r = theta_r - self.x[1]
        self.u[0:2] = np.array([kp * e_l - kd * self.x[2], kp * e_r - kd * self.x[3]])
        return abs(e_l) < 1e-3 and abs(e_r) < 1e-3

    def heater(self, status):
        T = self.x[6]
        if status:
            if T < self.t_target_on:
                self.u[2] = self.c["V_n"]
            else:
                self.u[2] = 0
            return T >= self.t_target_on

        self.u[2] = 0
        return T < self.t_target_off

    def homing_flags_reset(self):
        self.h_flag = True
        self.v_flag + True


if __name__ == "__main__":
    SQUARE = [(10, 10), (100, 10), (100, 100), (10, 100), (10, 10)]

    printer = Printer()
    printer.target_points = SQUARE
    printer.run(300)
    printer.plot()
