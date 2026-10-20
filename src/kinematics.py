def to_corexy(theta_l, theta_r, r_m):
    x = (theta_l + theta_r) * r_m / 2
    y = (theta_l - theta_r) * r_m / 2
    return x, y


def to_motor(x, y, r_m):
    theta_l = (x + y) / r_m
    theta_r = (x - y) / r_m
    return theta_l, theta_r
