"""
Genera web/automatas.js con las tablas de los cuatro autómatas.
Así la página usa exactamente las mismas funciones de transición que el código Python
(una sola fuente de verdad). Correr cada vez que se cambie flujo.py, puntaje.py, pila.py o turing.py:

    python exportar_web.py
"""
import json
import os

from flujo import TRANSICIONES
from puntaje import AFD, nombre, g, valor
from pila import F_AP, Q0 as Q0_AP, Z0, F as F_PILA
from turing import F_MT, Q0 as Q0_MT, FINALES, B

NOMBRES_FLUJO = {'q0': 'INICIO', 'q1': 'REPARTO', 'q2': 'TURNO_JUGADOR', 'q3': 'TURNO_CASA',
                 'q4': 'GANA', 'q5': 'PIERDE', 'q6': 'EMPATE', 'q7': 'FIN'}

# el AFD de puntaje con los nombres del informe (D0, B11, X...) en vez de "['p1', 'p11']"
nombres = {q: nombre(q) for q in AFD.q}
assert len(set(nombres.values())) == len(AFD.q), 'dos estados con el mismo nombre'

automatas = {
    'FLUJO': {'inicial': 'q0', 'finales': ['q7'], 'nombres': NOMBRES_FLUJO, 'f': TRANSICIONES},
    'PUNTAJE': {
        'inicial': nombres[AFD.initial_state],
        'f': {nombres[q]: {c: nombres[d] for c, d in fila.items()} for q, fila in AFD.delta.items()},
        'g': {nombres[q]: g(q) for q in AFD.q},
        'valor': {nombres[q]: valor(q) for q in AFD.q},
    },
    'PILA': {'inicial': Q0_AP, 'fondo': Z0, 'finales': sorted(F_PILA),
             'f': {f'{q},{c},{z}': list(destino) for (q, c, z), destino in F_AP.items()}},
    'TURING': {'inicial': Q0_MT, 'blanco': B, 'finales': FINALES,
               'f': {f'{q},{c}': list(destino) for (q, c), destino in F_MT.items()}},
}

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'automatas.js')
with open(ruta, 'w', encoding='utf-8', newline='\r\n') as archivo:
    archivo.write('// Archivo generado por exportar_web.py a partir de flujo.py, puntaje.py, pila.py y turing.py.\n')
    archivo.write('// No editar a mano: si cambia un autómata, volver a correr python exportar_web.py\n\n')
    for nombre_js, tabla in automatas.items():
        archivo.write(f'const {nombre_js} = {json.dumps(tabla, ensure_ascii=False, sort_keys=True)};\n\n')
print(f'Generado {ruta}')
