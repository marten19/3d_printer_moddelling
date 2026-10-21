import numpy as np
import control as ct
import yaml
import matplotlib.pyplot as plt
from src.kinematics import *

c = yaml.safe_load(open("src/constant.yaml"))
J_eq = c["J_m"] + 0.5 * c["m"] * c["r_m"] ** 2
C1 = (c["L_m"] * J_eq) / (c["r_m"] * c["K_m"])
C2 = (c["R_m"] * J_eq) / (c["r_m"] * c["K_m"])
C3 = c["K_m"] / c["r_m"]

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
C = np.eye(6)
D = np.zeros((6, 2))

corexy = ct.StateSpace(A, B, C, D)

t = np.linspace(0, 0.5, 100000)
omega = 1 * np.pi * 100
sin_omega_t = np.sin(omega * t)
cos_omega_t = np.cos(omega * t)


def ellipse_input(K=1, L=3):
    d_x = -K * omega * sin_omega_t
    dd_x = -K * omega**2 * cos_omega_t
    ddd_x = K * omega**3 * sin_omega_t

    d_y = L * omega * cos_omega_t
    dd_y = -L * omega**2 * sin_omega_t
    ddd_y = -L * omega**3 * cos_omega_t

    u_x = C1 * ddd_x + C2 * dd_x + C3 * d_x
    u_y = C1 * ddd_y + C2 * dd_y + C3 * d_y

    u_m_l = u_x + u_y
    u_m_r = u_x - u_y
    U = np.vstack([u_m_l, u_m_r])

    theta_l_0 = K / c["r_m"]
    theta_r_0 = K / c["r_m"]
    omega_l_0 = (L * omega) / c["r_m"]
    omega_r_0 = -(L * omega) / c["r_m"]
    i_l_0 = (J_eq / c["K_m"]) * (-K * omega**2) / c["r_m"]
    i_r_0 = (J_eq / c["K_m"]) * (-K * omega**2) / c["r_m"]

    X0 = np.array([theta_l_0, theta_r_0, omega_l_0, omega_r_0, i_l_0, i_r_0])
    return U, X0


def heart_input():
    K = 10
    # x = K * (12 * sin_omega_t - 4 * np.sin(3 * omega * t))
    d_x = K * omega * (12 * cos_omega_t - 12 * np.cos(3 * omega * t))
    dd_x = K * omega**2 * (-12 * sin_omega_t + 36 * np.sin(3 * omega * t))
    ddd_x = K * omega**3 * (-12 * cos_omega_t + 108 * np.cos(3 * omega * t))

    y = K * (
        13 * cos_omega_t
        - 5 * np.cos(2 * omega * t)
        - 2 * np.cos(3 * omega * t)
        - np.cos(4 * omega * t)
    )
    d_y = (
        K
        * omega
        * (
            -13 * sin_omega_t
            + 10 * np.sin(2 * omega * t)
            + 6 * np.sin(3 * omega * t)
            + 4 * np.sin(4 * omega * t)
        )
    )
    dd_y = (
        K
        * omega**2
        * (
            -13 * cos_omega_t
            + 20 * np.cos(2 * omega * t)
            + 18 * np.cos(3 * omega * t)
            + 16 * np.cos(4 * omega * t)
        )
    )
    ddd_y = (
        K
        * omega**3
        * (
            13 * sin_omega_t
            - 40 * np.sin(2 * omega * t)
            - 54 * np.sin(3 * omega * t)
            - 64 * np.sin(4 * omega * t)
        )
    )

    u_x = C1 * ddd_x + C2 * dd_x + C3 * d_x
    u_y = C1 * ddd_y + C2 * dd_y + C3 * d_y

    u_m_l = u_x + u_y
    u_m_r = u_x - u_y
    U_ellipse = np.vstack([u_m_l, u_m_r])

    theta_l_0 = 5 * K / c["r_m"]
    theta_r_0 = -5 * K / c["r_m"]
    omega_l_0 = 0
    omega_r_0 = 0
    i_l_0 = (J_eq / c["K_m"]) * (41 * K * omega**2) / c["r_m"]
    i_r_0 = -(J_eq / c["K_m"]) * (41 * K * omega**2) / c["r_m"]
    X0 = np.array([theta_l_0, theta_r_0, omega_l_0, omega_r_0, i_l_0, i_r_0])
    return U_ellipse, X0


def input_response(U, X0):
    _, y_out = ct.forced_response(corexy, T=t, U=U, X0=X0)
    theta_l = y_out[0, :]
    theta_r = y_out[1, :]

    x, y = to_corexy(theta_l, theta_r, c["r_m"])

    plt.plot(x, y, label="Toolhead Path")
    plt.title("CoreXY")
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.axis("equal")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # U, X0 = ellipse_input(1,3)
    U, X0 = heart_input()
    input_response(U, X0)
