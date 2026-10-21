import numpy as np
import matplotlib.pyplot as plt

time_sim = 10
plot_num_lines = 8

length = 0.1
speed = 0.05


k_pla = 0.13
C_pla = 1800
rho_pla = 1240
k_prime = k_pla / (rho_pla * C_pla)
T_e = 21
T_bed = 60
T_n = 220
a = 0.0004
A = a * a
U_bed = 500
U_air = 10
T = np.array([T_n])
dx = 0.001
dt = 0.02


A_bed = a * dx
A_air = 3 * A_bed
Volume = dx * a * a

num_points = int(length / dx)


step = 0
num_step = int(time_sim/dt)
plot_step = int(num_step/plot_num_lines)

while step < num_step:
    # print(t)
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

    if not (step % plot_step):
        x = np.arange(len(T)) * dx * 1000
        plt.plot(x, T, label=f"t = {step * dt} s")
        print(len(T))
        print(step)
    step += 1

plt.title("Filament temperature")
plt.legend()
plt.show()
