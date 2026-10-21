import numpy as np
import matplotlib.pyplot as plt


k_pla = 0.13
C_pla = 1800
rho_pla = 1240
k_prime = k_pla/(rho_pla*C_pla)
T_e = 21
T_bed = 60
a = 0.1
A = a*a
U_bed = 500
U_air = 10 




T = np.array([x**2 for x in range(20)])
plt.plot(range(len(T)),T)
print(T)
dx = 0.001
dt = 0.1


A_bed = a * dx
A_air = 3 * A_bed
Volume = dx * a * a



for t in range(10000):
    T_insulated = np.concatenate(([T[0]],T,[T[-1]]))
    T_gradiant_2 = np.gradient(np.gradient(T_insulated,dx),dx)[1:-1]
    Q_air = U_air * A_air * (T - T_e)
    Q_bed = U_bed * A_bed * (T - T_bed)
    f = -(Q_air + Q_bed) / Volume
    f_prime = f / (rho_pla * C_pla)
    f_prime = 0
    d_T = (k_prime * T_gradiant_2 + f_prime)
    T = T + dt * d_T
    if not(t % 1000):
        plt.plot(range(len(T)),T)
        
    
    
plt.plot(range(len(T)),T)
plt.show()