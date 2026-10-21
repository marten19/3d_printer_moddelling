import numpy as np
import yaml
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

c = yaml.safe_load(open("src/constant.yaml"))

t = np.linspace(0, 1000, 1000)


def nozzle(t, x, u):
    T_n, v_R, i_L = x
    d_T = v_R**2 / (c["C_t_n"] * c["R_n"]) - (T_n - c["T_e"]) / (c["C_t_n"] * c["R_t_n"])
    d_v = i_L / c["C_n"] - v_R / (c["C_n"] * c["R_n"])
    d_i = u / c["L_n"] - v_R / c["L_n"]
    return [d_T, d_v, d_i]


def step_response(voltage=24):
    X0 = np.array([c["T_e"], 0, 0])
    sol = solve_ivp(nozzle, (t[0], t[-1]), X0, args=(voltage,), method="LSODA" ,t_eval=t)
    T_n = sol.y[0, :]

    plt.plot(t, T_n)
    plt.title("Nozzle step response")
    plt.xlabel("Time [s]")
    plt.ylabel("Temperature [°C]")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    step_response()