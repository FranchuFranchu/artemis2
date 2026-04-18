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
from main_mpl import main_mpl
from main_ipy import main_ipy

DATOS = {}

for i in NOMBRES:
    DATOS[i] = horizons_vector_to_dataframe(f"horizon-{i}.txt")


time_range, horizon_data = interpolate_horizon_data(DATOS, PROGRESS)
np.set_printoptions(linewidth=160)

t = main_mpl(time_range, horizon_data)
print(t)
