Simulación de la trayectoria de Artemis II.

## Cómo usar.

Con una instalación de `python`, `python main.py` lanza una ventana interactiva de matplotlib que muestra la trayectoria de la nave simulada comparada con la real.

Requiere los siguientes paquetes: `matplotlib scipy numpy pandas`

En mi caso también requirió `PyQt5` para la interfaz de usuario.

La simulación arranca antes de la inyección trans-lunar y termina cuando 
el cohete toca la atmósfera.

En azul se muestra la trayectoria "real", de referencia, tomada de datos reales de la NASA. En naranja se muestra la trayectoria simulada usando las condiciones iniciales y los parámetros de la inyección translunar.

Los puntos azules y naranjas son isócronas de ambas simulaciones. También hay una animación mostrando ambas. En rojo se marca el momento de la maniobra orbital.

## Parámetros

La UI tiene sliders que permiten cambiar los parámetros de la trayectoria

Los parámetros son los parámetros de la inyección trans-lunar, que es la maniobra orbitan en la que el cohete prende sus motores para aumentar su apogeo hasta que llega a la Luna.

Los parámetros son:
- `tiempo` el momento en el que que se centra el impulso
- `duración` es la duración del impulso
- `prograda`, `radial`, y `normal` son las tres direcciones relativas al marco de referencia de la nave que cambian la dirección del impulso. `prograda` apunta hacia la direccion de movimiento de la nave, `normal` apunta afuera de la pantalla, y `radial` es su producto vectorial. Tienen unidades de velocidad, porque miden cuanto cambia la velocidad de la nave.

Los parámetros por defecto son los que encontré que mejor se ajustan a la trayectoria de la nave. Intenté que el tiempo de llegada y el ángulo en el que toca la atmósfera cuando regresa sea lo más similar posible.

Probé varias maneras de encontrar las características del impulso real, pero al final lo que funcionó mejor fue ajustarlos manualemente. Por eso, aunque la trayectoria que encontré yo es muy parecida a la real, no creo que sea la misma; es posible que la nave en realidad haya tenido otro impulso inicial en un momento ligeramente distinto que le dio una trayectoria similar.

## Estructura

- `simulation.py` contiene el código de la simulación y el integrador numérico propiamente dicho.
- `parse_horizon.py` parsea los datos de entrada que fueron exportados desde la NASA acá: https://ssd.jpl.nasa.gov/horizons/app.html
- `main_mpl.py` presenta una interfaz para cambiar los parámetros.
- `common.py` tiene parámetros comunes a toda la simulación. Si te anda lento cambia esto.
- `process.ipynb` tiene graficos lindos.

metodo de integracion: DOP853

## Transparencia

Bastante del código inicial fue hecho con asistencia de ChatGPT. Este es el diálogo completo que tuve: https://chatgpt.com/share/69e3f297-11a4-83e9-b1ac-566a3ebc1b04

Haciendo este proyecto aprendí mucho sobre los detalles y las mejores maneras de hacer una simulación numérica, mucho con asistencia de ChatGPT.
