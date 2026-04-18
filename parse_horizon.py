"""
este archivo se encarga de parsear los datos que exporté del sistema de la NASA
en arrays
"""

import re
import pandas as pd
import numpy as np
from common import *


def horizons_vector_to_dataframe(filepath):
    """
    Dado un path, devuelve un dataframe con los datos de un archivo.
    """
    records = []

    with open(filepath, "r") as f:
        lines = f.readlines()

    in_data = False
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line == "$$SOE":
            in_data = True
            i += 1
            continue

        if line == "$$EOE":
            break

        if in_data:
            jd_match = re.match(r"^\s*([0-9]+\.[0-9]+)\s*=\s*(.*)$", line)

            if jd_match:
                jd = float(jd_match.group(1))
                calendar = jd_match.group(2).strip()

                # Position
                pos_line = lines[i + 1].strip()
                pos_vals = dict(re.findall(r"([XYZ])\s*=\s*([-\d.E+]+)", pos_line))

                # Velocity
                vel_line = lines[i + 2].strip()
                vel_vals = dict(re.findall(r"(V[XYZ])\s*=\s*([-\d.E+]+)", vel_line))

                # Optional extra line
                extra_vals = {}
                if i + 3 < len(lines):
                    extra_line = lines[i + 3].strip()
                    matches = re.findall(r"([A-Z]{2})\s*=\s*([-\d.E+]+)", extra_line)
                    if matches:
                        extra_vals = dict(matches)
                        i += 1  # consume extra line

                # Merge all values
                record = {
                    "jd": jd,
                    "calendar": calendar,
                    **pos_vals,
                    **vel_vals,
                    **extra_vals,
                }

                records.append(record)
                i += 3

        i += 1

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Convert numeric columns
    for col in df.columns:
        if col not in ["calendar"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["datetime"] = (
        df["calendar"]
        .str.replace("A.D. ", "", regex=False)
        .str.replace(" TDB", "", regex=False)
    )

    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%b-%d %H:%M:%S.%f")

    df[["X", "Y", "Z", "VX", "VY", "VZ"]] *= DISTANCE_FACTOR
    return df

def interpolate_horizon_data(DATOS, frac=1):
    """
    devuelve un array N x 6 x M con (x, y, z, vx, vy, vz) con unidades normalizadas
    """

    t_min = min(df["datetime"].min() for df in DATOS.values()).to_datetime64().astype("datetime64[s]").astype("int64")
    t_max = max(df["datetime"].max() for df in DATOS.values()).to_datetime64().astype("datetime64[s]").astype("int64")


    time_grid = np.arange(t_min, t_min + (t_max - t_min) * frac, TIMESTEP)

    N = len(time_grid)
    M = len(NOMBRES)

    result = np.zeros((N, 6, M))

    cols = ["X", "Y", "Z", "VX", "VY", "VZ"]

    datos_artemis = []
    for j, name in enumerate(NOMBRES):
        df = DATOS[name]

        # Convert body time to seconds
        t_body = df["datetime"].values.astype("datetime64[s]").astype("int64")

        for k, col in enumerate(cols):
            values = df[col].values
            # Interpolate onto global grid
            interp_vals = np.interp(
                time_grid, t_body, values, left=values[0], right=values[-1]
            )
            if len(datos_artemis) <= k:
                datos_artemis.append(interp_vals)
                interp_vals = np.zeros_like(interp_vals)
            else:
                interp_vals -= datos_artemis[k]

            result[:, k, j] = interp_vals
    return time_grid, result
