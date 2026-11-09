"""
Pruebas automáticas de los cuatro modelos (las que se citan en el informe, sección 5.2).
Usa semillas fijas, así cada corrida da los mismos números.

Uso: python pruebas.py
"""
import random
import sys

from flujo import AFD_FLUJO
from puntaje import AFD, SIGMA_E, VALOR, nombre, valor
from pila import acepta, F_AP
from turing import ejecutar, FINALES
from partida import Partida

try:
    sys.stdout.reconfigure(errors='replace')            # por si la consola no muestra algún símbolo
except AttributeError:
    pass


def puntaje_directo(mano):
    """Puntaje calculado sin autómata: un As vale 11 si no pasa la mano. 22 = pasada"""
    total = sum(VALOR[c] for c in mano)
    if 'A' in mano and total + 10 <= 21:
        total += 10
    return total if total <= 21 else 22


def probar_puntaje(manos=200_000):
    """El AFD de puntaje contra el cálculo directo, con manos al azar de 0 a 8 cartas"""
    azar, errores = random.Random(2026), 0
    for _ in range(manos):
        mano = [azar.choice(SIGMA_E) for _ in range(azar.randint(0, 8))]
        estado = AFD.initial_state
        for carta in mano:
            estado = AFD.delta[estado][carta]
        errores += valor(estado) != puntaje_directo(mano)
    print(f'Puntaje: {manos} manos al azar contra el cálculo directo, {errores} errores')
    return errores


def probar_minimo():
    """Minimización del AFD de puntaje como reconocedor (finales = manos que valen 21)"""
    estados = list(AFD.q)
    clase = {q: q != 'X' and valor(q) == 21 for q in estados}
    while True:
        firma = {q: (clase[q], tuple(clase[AFD.delta[q][c]] for c in SIGMA_E)) for q in estados}
        if len(set(firma.values())) == len(set(clase.values())):
            break
        clase = firma
    grupos = {}
    for q in estados:
        grupos.setdefault(firma[q], []).append(nombre(q))
    equivalentes = [sorted(g) for g in grupos.values() if len(g) > 1]
    print(f'Puntaje: {len(estados)} estados, AFD mínimo de {len(grupos)}; equivalentes: {equivalentes}')
    return 0 if (len(estados), len(grupos)) == (33, 32) else 1


def probar_turing():
    """La MT para todos los pares de puntajes de 0 a 21"""
    errores = 0
    for jugador in range(22):
        for casa in range(22):
            estado, _ = ejecutar('1' * jugador + '#' + '1' * casa)
            esperado = 'GANA' if jugador > casa else 'PIERDE' if jugador < casa else 'EMPATE'
            errores += FINALES.get(estado) != esperado
    print(f'MT: {22 * 22} pares de puntajes (0 a 21), {errores} errores')
    return errores


def probar_partida(sesiones=3000):
    """Sesiones completas por consola con respuestas al azar (algunas inválidas).
    El flujo tiene que aceptar la sesión y el AP coincidir con el conteo de ganadas y perdidas"""
    errores = manos = 0
    for semilla in range(sesiones):
        azar = random.Random(semilla)
        partida = Partida(entrada=lambda _: azar.choice(['p', 's', 'c', 'c', 't', 'x', '']),
                          salida=lambda *_: None, azar=azar)
        partida.jugar()
        sesion = partida.sesion
        manos += sesion.count('r')
        sin_perdida = sesion.count('v') >= sesion.count('d') + sesion.count('x')
        errores += not AFD_FLUJO.accept(sesion) or acepta(sesion) != sin_perdida
    print(f'Partida: {sesiones} sesiones simuladas ({manos} manos), {errores} errores')
    return errores


if __name__ == '__main__':
    print(f'AP: {len(F_AP)} transiciones')
    total = probar_puntaje() + probar_minimo() + probar_turing() + probar_partida()
    print('TODO BIEN' if total == 0 else f'HAY {total} ERRORES')
    sys.exit(1 if total else 0)
