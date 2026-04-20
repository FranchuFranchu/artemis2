from dateutil.parser import parse
import numpy as np

# CONSTANTES DE RENDIMIENTO
# MAS GRANDE = MAS RAPIDO
TIMESTEP = 15
RTOL = 1e-9
ATOL = 1e-12
ANIM_INTERVAL = 30 # agrandar tambien ralentiza la animacion
# MAS GRANDE = ANIMACION MAS FLUIDA
FRAME_COUNT = 200

# constantes para normalizar todo y que la integracion numerica funcione bien
DISTANCE_FACTOR = 1e-6 #km -> Tm
MASS_FACTOR = 1e-27 # kg -> 1e27 kg
VELOCITY_FACTOR = 1
TIME_FACTOR = 1
# que porcentaje de la simulacion hacer
PROGRESS = 1.05
# datos de masas
NOMBRES = ["artemis", "earth", "moon", "sol", "jupiter"]
MASSES = {
    "artemis": 0,
    "sol": 1988410e24,
    "earth": 5.97219e24,
    "moon": 7.349e22,
    "jupiter": 1.898e27,
}
MASSES_ARR = np.array([MASSES[i] * MASS_FACTOR for i in NOMBRES])

G = (
    6.67430e-11 * (1e-3 * DISTANCE_FACTOR) ** 3 * MASS_FACTOR**-1
)
# altura de la atmosfera de la tierra = R_tierra + 100km
ATMOS_HEIGHT = DISTANCE_FACTOR * 6478

# Tiempo en el que se hace la TLI
BURN_1 = parse("2026-04-02T23:55:00Z").timestamp()

# los parametros que encontre yo
p0 = (BURN_1, 600, 9.65120184 * 1.26e-10 * 600 / 2, -3.74 * 1.26e-10 * 600 / 2, 0)
# Acá configuro el sistema de coordenadas para los sliders.
# velocidad de referencia de la nave en el punto del burn
# gracias kerbal space program
VELOCITY_VECTOR = np.array([-1.023724090798557E+01,.613753247030264E+00,1.634180436530357E-01])
POSITION = np.array([1.757820643319786E+03, 6.303688378369665E+03, 5.465041540948077E+02])
prograde = VELOCITY_VECTOR / np.linalg.norm(VELOCITY_VECTOR)
normal = np.cross(POSITION, prograde)
normal /= np.linalg.norm(normal)
radial = np.cross(prograde, normal)
B = np.column_stack((prograde, normal, radial))
# solve for coefficients
velocity = np.linalg.solve(B, VELOCITY_VECTOR)
