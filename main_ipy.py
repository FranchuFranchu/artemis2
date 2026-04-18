import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from scipy.interpolate import interp1d
import pandas as pd
from matplotlib import pyplot as plt
from scipy.integrate import solve_ivp
from simulation import *
from parse_horizon import *
from common import *
from pprint import pprint
import numpy as np
from dateutil.parser import parse
from scipy.signal import savgol_filter


def main_ipy(time_range, horizon_data):
    # ---- precompute reference ----
    mid = len(time_range)//2
    h_heights = np.linalg.norm(horizon_data[mid:, 0:3, 1], axis=1)
    min_height = np.min(h_heights)
    h_time = time_range[mid + np.argmin(h_heights)]

    traj_ref = -horizon_data[:, :, 1]
    traj_moon = horizon_data[:, :, 2] - horizon_data[:, :, 1]

    selected_times = np.array([
        *np.linspace(0, len(time_range)-1, 10).astype("int64"),
        mid + np.argmin(h_heights)
    ])

    # ---- main update function ----
    def update(t0, dur, prog, rad, norm, inten, frame):
        frame = int(frame)
        params = np.array([t0, dur, prog, rad, norm, inten])

        # run simulation
        time_out, sim = run_simulation(
            time_range,
            horizon_data,
            burns=[
                (t0,
                dur,
                B @ np.array([prog, rad, norm]),
                inten),
            ]
        )

        traj_sim = -sim[:, :, 1]

        # ---- compute metrics ----
        heights = np.linalg.norm(sim[mid:, 0:3, 1], axis=1)
        arg = np.argmin(np.maximum(heights - min_height, 0))
        sim_min_time = time_out[mid + arg]
        delta_h = (heights - min_height)[arg]

        # ---- plot ----
        plt.figure(figsize=(6,6))

        # reference
        plt.plot(traj_ref[:,1], traj_ref[:,0], "-", color="tab:blue", label="Referencia")
        plt.plot(traj_ref[:,1][selected_times], traj_ref[:,0][selected_times], "o", color="tab:blue")

        # simulation
        plt.plot(traj_sim[:,1], traj_sim[:,0], "--", color="tab:orange", label="Simulación")
        plt.plot(traj_sim[:,1][selected_times], traj_sim[:,0][selected_times], "o", color="tab:orange")

        plt.plot(traj_ref[frame,1], traj_ref[frame,0], "o", color="tab:blue")
        plt.plot(traj_sim[frame,1], traj_sim[frame,0], "o", color="tab:orange")
        # moon
        plt.plot(traj_moon[:,1], traj_moon[:,0], color="tab:green", alpha=0.3, label="Luna")
        plt.plot(traj_moon[frame,1], traj_moon[frame,0], "o", color="tab:green")

        # Earth
        circle = plt.Circle((0,0), ATMOS_HEIGHT)
        plt.gca().add_artist(circle)

        plt.axis("equal")
        plt.xlim(-0.4, 0.05)
        plt.ylim(-0.2, 0.05)
        plt.xlabel("x [Tm]")
        plt.ylabel("y [Tm]")
        plt.legend()

        # text info
        plt.title(f"{delta_h / DISTANCE_FACTOR:.0f} km | ΔT: {(sim_min_time - h_time)/60:.2f} min")

        plt.show()

    # ---- sliders ----
    def r(p0):
        return sorted([p0 * 0.99, p0 * 1.005])

    return interact(
        update,
        t0=FloatSlider(min=p0[0]-60*5, max=p0[0]+60*5, step=1, value=p0[0]),
        dur=FloatSlider(min=0, max=400, step=1, value=p0[1]),
        prog=FloatSlider(min=r(p0[2])[0], max=r(p0[2])[1], step=0.1, value=p0[2]),
        rad=FloatSlider(min=-10, max=10, step=0.1, value=p0[3]),
        norm=FloatSlider(min=-10, max=10, step=0.1, value=p0[4]),
        inten=FloatSlider(min=0, max=10, step=0.1, value=p0[5]),
        frame=FloatSlider(min=0, max=len(time_range)-1, step=1, value=0)

    )
