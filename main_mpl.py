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
from datetime import datetime


def main_mpl(time_range, horizon_data):
    # ---- figure ----
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.1, bottom=0.45)

    mid = len(time_range)//2
    h_heights = np.linalg.norm(horizon_data[mid:, 0:3, 1], axis=1)
    min_height = np.min(h_heights)
    h_time = time_range[mid+np.argmin(h_heights)]
    # Plot HORIZONS trajectory once (Artemis = index 1)
    traj_ref = -horizon_data[:, :, 1]
    traj_moon = horizon_data[:, :, 2]-horizon_data[:, :, 1]
    line_ref, = ax.plot(traj_ref[:, 1], traj_ref[:, 0], "-", color="tab:blue")
    selected_times = np.array([*np.linspace(0,len(time_range)-1,10).astype("int64"), mid+np.argmin(h_heights)])
    dots_ref, = ax.plot(traj_ref[:, 1][selected_times], traj_ref[:, 0][selected_times], "o", color="tab:blue")


    # Simulation line (empty initially)
    line_sim, = ax.plot([], [], "--", color="tab:orange")
    dots_sim, = ax.plot([], [], "o", color="tab:orange")
    dot_burn, = ax.plot([], [], "o", color="tab:red", label="Maniobra")

    # Moving points
    point_ref, = ax.plot([], [], "o", label="Referencia",color="tab:blue")
    point_sim, = ax.plot([], [], "o", label="Simulación",color="tab:orange")
    point_mun, = ax.plot([], [], "o", label="Luna",color="tab:green")

    earth = plt.Circle((0, 0), ATMOS_HEIGHT)
    ax.add_artist(earth)
    ax.set_aspect("equal")
    ax.legend()
    ax.set_xlim(-0.4, 0.05)
    ax.set(xlabel="x [Tm]", ylabel="y [Tm]")
    ax.set_ylim(-0.2, 0.05)

    # Error text
    text = ax.text(0.02, 0.70, "", transform=ax.transAxes)

    # ---- sliders ----
    sliders = []
    labels = ["tiempo", "duración", "prógrada", "radial", "normal", "intensidad"]

    def r(p0):
        delta = p0 * 1e-2
        return sorted([p0 - delta, p0 + delta])

    ranges = [
        (p0[0] - 60 * 30, p0[0] + 60 * 30),
        (0, 1000),
        r(p0[2]),
        (-1e-6, 1e-6),
        (-1e-6, 1e-6),
    ]

    fmt_funcs = (
        lambda i: f'{datetime.fromtimestamp(i)}',
        lambda i: f'{i} s',
        lambda i: f'{i / DISTANCE_FACTOR * 1000} m/s',
        lambda i: f'{i / DISTANCE_FACTOR * 1000} m/s',
        lambda i: f'{i / DISTANCE_FACTOR * 1000} m/s',
    )
    for i in range(5):
        ax_s = plt.axes([0.1, 0.35 - i*0.05, 0.6, 0.03])
        slider = Slider(ax_s, labels[i], ranges[i][0], ranges[i][1], valinit=p0[i])
        sliders.append(slider)

    # ---- update function ----
    def update(_):
        for s, f in zip(sliders, fmt_funcs):
            s.valtext.set_text(f(s.val))
        params = np.array([s.val for s in sliders])

        # run simulation
        time_out, sim = run_simulation(
            time_range,
            horizon_data,
            burns=[
                (params[0],
                params[1],
                # convertir a aceleraciom maxima
                2 * B @ np.array(params[2:5]) / params[1],
                )]
        )

        deltav = np.linalg.norm(B @ np.array(params[2:5]))  / DISTANCE_FACTOR * 1000
        traj_sim = -sim[:, :, 1]
        sim_cache["traj"] = traj_sim

        # update plot
        line_sim.set_data(traj_sim[:, 1], traj_sim[:, 0])

        dots_sim.set_data(traj_sim[:, 1][selected_times], traj_sim[:, 0][selected_times])

        burn_time = np.searchsorted(time_out, params[0])
        dot_burn.set_data([traj_sim[:, 1][burn_time]], [traj_sim[:, 0][burn_time]])

        heights = np.linalg.norm(sim[mid:, 0:3, 1], axis=1)
        arg = np.argmin(np.maximum(heights - min_height, 0))
        print(arg)
        sim_min_time = time_out[mid+arg]
        delta_h = (heights - min_height)[arg]

        text.set_text(f"Llegada a la tierra:\nΔH =     {delta_h / DISTANCE_FACTOR:.0f}km\nΔT =     {(sim_min_time - h_time)/60:.2f} min\nManiobra:\nΔV =    {deltav:.2f} m/s\nΔV real =    {388} m/s ")

        fig.canvas.draw_idle()

    # connect sliders
    for s in sliders:
        s.on_changed(update)

    for s, f in zip(sliders, fmt_funcs):
        s.valtext.set_text(f(s.val))
    # ---- reset button ----
    reset_ax = plt.axes([0.8, 0.05, 0.1, 0.04])
    button = Button(reset_ax, "Reset")

    def reset(event):
        for i, s in enumerate(sliders):
            s.set_val(p0[i])

    # ---- animation ----
    playing = {"state": False}
    sim_cache = {"traj": None}
    frame_idx = {"i": 0}

    def animate(frame):
        if sim_cache["traj"] is None:
            return

        i = frame_idx["i"]
        traj_sim = sim_cache["traj"]

        if i >= len(traj_ref):
            frame_idx["i"] = 0
            i = 0

        # update points
        point_ref.set_data([traj_ref[i,1]], [traj_ref[i,0]])
        point_sim.set_data([traj_sim[i,1]], [traj_sim[i,0]])
        point_mun.set_data([traj_moon[i,1]], [traj_moon[i,0]])

        frame_idx["i"] += len(traj_ref) // FRAME_COUNT

    ani = FuncAnimation(fig, animate, interval=ANIM_INTERVAL)
    ani.event_source.start()

    button.on_clicked(reset)
    update(0)
    plt.show()
