import numpy as np
from src.printer_states import *
import time
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
    dt = 0.01
    filament_loaded_flag = False
    filament_retracted_flag = False
    filament_empty_flag = False
    filament_color_change_flag = False
    wiping_done = False
    target_points = [(0.1, 0.0), (0.1, 0.1), (0.0, 0.1), (0.0, 0.0)]
    visited_points = []
    
    temperature = 200
    x = np.zeros(6)
    u = np.ones(2)
    # y = 5
    simulation_events = []
    c = yaml.safe_load(open("src/constant.yaml"))
    J_eq = c["J_m"] + 0.5 * c["m"] * c["r_m"] ** 2
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

    B = np.array([[0, 0], [0, 0], [0, 0], [0, 0], [1.0 / c["L_m"], 0], [0, 1.0 / c["L_m"]]])


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
        return self.x[0]

    def get_y(self):
        return self.x[1]

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

    def run(self, duration):
        while self.t < duration:
            # print(self.t)
            self.step()
            # self.feedback()
            # self.process_sim_events()
            # time.sleep(0.1)
            self.tick()
            self.add_telemetry()
            # if printer.state = 

    def add_telemetry(self):
        x, y = to_corexy(self.x[0], self.x[1], self.c["r_m"])
        self.visited_points.append([x, y])

    def plot(self):
        pts = np.array(self.visited_points) * 1000   # m -> mm
        plt.plot(pts[:, 0], pts[:, 1])
        plt.show()

        
    def sys(self, t, x, u):
        dx = self.A @ x + self.B @ u
        return dx
    
    def step(self):
        sol = solve_ivp(self.sys, (self.t, self.t + self.dt), self.x,
                        args=(self.u,), method="LSODA")
        self.x = sol.y[:, -1]
        self.t += self.dt
        # print(to_corexy(self.x[0], self.x[1], self.c["r_m"]))
        
    def feedback(self, x, y, kp = 0.1):
        # For now ill try with a p controller
        theta_l , theta_r = to_motor(x , y, self.c["r_m"])
        e_l = theta_l - self.x[0]
        e_r = theta_r - self.x[1]
        self.u = np.array([kp * e_l, kp * e_r])
        return abs(e_l) < 1e-3 and abs(e_r) < 1e-3
    
        
    
        
        
        
        
        
        
        
if __name__ == "__main__":
    printer = Printer()
    # for i in range(100000):
    #     printer.feedback(0.2,0.1)
    #     printer.step()
    
    # printer.add_sim_event("C", True, time.time() + 1)
    # printer.add_sim_event("F", True, time.time() + 20)

    printer.run(200)
    printer.plot()
