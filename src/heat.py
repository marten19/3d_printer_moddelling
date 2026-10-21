import numpy as np
import matplotlib.pyplot as plt

k = 1
rho = 1
C = 1
f = 1

k_prime = k/(rho*C)
f_prime = 0#f/(rho*C)
T_e = 21

T = np.array([x**2 for x in range(20)])
plt.plot(range(len(T)),T)
print(T)
dx = 1
dt = 0.1

for t in range(100000):
    T_gradiant_2 = np.gradient(np.gradient(T,dx),dx)/dx**2
    d_T = (k_prime * T_gradiant_2 + f_prime)
    T = T + dt * d_T
    
plt.plot(range(len(T)),T)
plt.show()