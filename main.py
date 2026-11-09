
"""
Ejemplos de cada modelo: recorre algunas manos en el autómata de puntaje
y algunas sesiones en el autómata de flujo,
en el autómata de pila (balance) y en la máquina de Turing (resultado).
Las pruebas masivas están en pruebas.py
"""
import sys

from puntaje import AFND, AFD, nombre, g
from flujo import AFD_FLUJO
from pila import acepta, mostrar
from turing import ejecutar, evento, FINALES

try:
    sys.stdout.reconfigure(errors='replace')            # por si la consola no muestra algún símbolo
except AttributeError:
    pass

print(f'AFD de puntaje: {len(AFD.q)} estados (con X)')

for mano in ['AT', 'A55', 'TTA', 'A6', 'T6', 'T95']:
    estado = AFD.initial_state
    for carta in mano:
        estado = AFD.delta[estado][carta]
    print(f'{mano:4} -> {nombre(estado):4} g={g(estado)}  21: {AFND.accept(mano)}')

for sesion in ['rnvt', 'rpst', 'rpshdt', 'rshhvcrxt', 'rpnhvt']:
    print(f'{sesion:10} {"ACEPTADA" if AFD_FLUJO.accept(sesion) else "rechazada"}')

print('\nMT: jugador#casa en unario')
for jugador, casa in [(20, 18), (17, 19), (19, 19), (2, 1)]:
    estado, pasos = ejecutar('1' * jugador + '#' + '1' * casa)
    print(f'{jugador:2} vs {casa:2} -> {FINALES[estado]:6} ({len(pasos) - 1} pasos)  evento {evento(jugador, casa)}')
print('2 vs 1:', ' ├─ '.join(ejecutar('11#1')[1]))

print('\nAP: sesiones sin pérdida (ganadas >= perdidas)')
mano = 'rsh' + evento(20, 18)          # la MT decide el evento de la mano
for sesion in [mano + 't', 'rxc' + mano + 't', 'rxcrxc' + mano + 't', 'rshdcrshet']:
    print(f'{sesion:16} {"ACEPTADA" if acepta(sesion) else "rechazada"}')
print(mostrar('rxcrshvt'))
