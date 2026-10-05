
"""
Pruebas del avance: recorre algunas manos en el autómata de puntaje
y algunas sesiones en el autómata de flujo
"""

from puntaje import AFND, AFD, nombre, g
from flujo import AFD_FLUJO

print(f'AFD de puntaje: {len(AFD.q)} estados (+ X = 33)')

for mano in ['AT', 'A55', 'TTA', 'A6', 'T6']:
    estado = AFD.initial_state
    for carta in mano:
        estado = AFD.delta[estado][carta]
    print(f'{mano:4} -> {nombre(estado):4} g={g(estado)}  21: {AFND.accept(mano)}')

for sesion in ['rnvt', 'rpst', 'rpshdt', 'rshhvcrxt', 'rpnhvt']:
    print(f'{sesion:10} {"ACEPTADA" if AFD_FLUJO.accept(sesion) else "rechazada"}')
