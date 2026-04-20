import numpy as np
from scipy.integrate import solve_ivp
from common import *


def compute_gravity_acceleration(positions, masses):
    """
    Vectorizado.
    positions: (N, 3)
    masses: (N,)
    """
    r_ij = positions[None, :, :] - positions[:, None, :]  # (N, N, 3)
    dist = np.linalg.norm(r_ij, axis=2)

    # Avoid division by zero
    np.fill_diagonal(dist, np.inf)


    inv_dist3 = 1.0 / dist**3

    acc = G * np.sum(
        masses[None, :, None] * r_ij * inv_dist3[:, :, None],
        axis=1
    )

    return acc

def smooth_window(t, t0, t1):
    """
    Smoothly ramps from 0→1→0 over [t0, t1]
    """
    if t <= t0 or t >= t1:
        return 0.0

    x = (t - t0) / (t1 - t0)  # normalize to [0,1]
    return 0.5 * (1 - np.cos(np.pi * x))
def nbody_equations(t, y, masses, burns, **kwargs):
    N = len(masses)

    # Split positions and velocities
    positions = y[: 3 * N].reshape((N, 3))
    velocities = y[3 * N :].reshape((N, 3)) / VELOCITY_FACTOR

    accelerations = np.zeros_like(positions)
    accelerations += compute_gravity_acceleration(positions, masses)

    accelerations /= VELOCITY_FACTOR

    for tt, duration, direction in burns:
        accelerations[0] += smooth_window(t, tt - duration / 2, tt + duration / 2) * direction

    # lo que hacemos acá es asegurarnos que el origen de coordenadas sea el cuerpo 0, que es Artemis
    accelerations[1:] -= accelerations[0]
    accelerations[0] = np.zeros_like(accelerations[0])
    velocities[1:] -= velocities[0]
    velocities[0] = np.zeros_like(velocities[0])
    dydt = np.concatenate([velocities.flatten() * VELOCITY_FACTOR, accelerations.flatten() * VELOCITY_FACTOR])
    return dydt

def integrate_system(y0, t_eval, **kwargs):
    sol = solve_ivp(
        fun=lambda t, y: nbody_equations(t, y, **kwargs),
        t_span=(np.min(t_eval), np.max(t_eval)),
        y0=y0,
        method="DOP853",
        rtol=RTOL,
        atol=ATOL,
        dense_output=False,
        t_eval=t_eval,
    )
    return sol

def run_simulation(time_range, horizon_data, **kwargs):

    m0 = []
    for k in NOMBRES:
        m0.append(MASSES[k] * MASS_FACTOR)
    m0 = np.array(m0)
    n_bodies = len(NOMBRES)

    y0 = horizon_data[0].reshape(2, 3, n_bodies)
    y0[1] *= VELOCITY_FACTOR
    y0 = y0.transpose(0, 2, 1).flatten()

    sol = integrate_system(y0, time_range, masses = m0, **kwargs)
    solu = sol.y
    time_range = sol.t
    n_times = len(time_range)
    y_interp = solu.reshape(2, n_bodies, 3, n_times)
    y_interp[1] /= VELOCITY_FACTOR
    y_interp = y_interp.transpose(3, 0, 2, 1)
    y_interp = y_interp.reshape(n_times, 6, n_bodies)
    return time_range, y_interp
