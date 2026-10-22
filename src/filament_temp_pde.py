import numpy as np
import matplotlib.pyplot as plt
import yaml

time_sim = 10
plot_num_lines = 10

length = 0.1
speed = 0.05

dx = 0.001
dt = 0.02

c = yaml.safe_load(open("src/constant.yaml"))
k_pla = c["k_pla"]
C_pla = c["C_pla"]
rho_pla = c["rho_pla"]
k_prime = k_pla / (rho_pla * C_pla)

T_e = c["T_e"]
T_bed = c["T_b"]
T_n = c["T_n"]
L_side = c["filament_width"]
U_bed = c["U_bed"]
U_air = c["U_air"]


A_bed = L_side * dx
A_air = 3 * A_bed
Volume = dx * L_side * L_side
A = L_side * L_side

num_points = int(length / dx)
num_step = int(time_sim / dt)
plot_step = int(num_step / plot_num_lines)


def pde_sim():
    T = np.array([T_n])
    step = 0
    while step < num_step:
        if len(T) < speed * step * dt / dx + 1 and len(T) < num_points:
            T = np.append(T, [T_n])

        if len(T) == num_points:
            T_insulated = np.concatenate(([T[-1]], T, [T[0]]))
        else:
            T_insulated = np.concatenate(([T[0]], T, [T[-1]]))

        T_gradiant_2 = np.gradient(np.gradient(T_insulated, dx), dx)[1:-1]
        Q_air = U_air * A_air * (T - T_e)
        Q_bed = U_bed * A_bed * (T - T_bed)
        f = -(Q_air + Q_bed) / Volume
        f_prime = f / (rho_pla * C_pla)
        d_T = k_prime * T_gradiant_2 + f_prime
        T = T + dt * d_T

        if not (step % plot_step) and not step == 0:
            x = np.arange(len(T)) * dx * 1000
            plt.plot(x, T, label=f"t = {step * dt} s")
        step += 1

        if T.max() - T.min() < 1 and len(T) >= num_points:
            print("Simulation stopped, filament cooled down at t: ", step * dt, "s")
            break

    plt.title("Filament temperature")
    plt.xlabel("Fillament printed [mm]")
    plt.ylabel("temperature [°C]")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    pde_sim()
