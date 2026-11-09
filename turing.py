"""
Máquina de Turing que decide el resultado de una mano.
En la cinta van los puntajes del jugador y de la casa en unario separados por #
(20 contra 18 -> 1111...#111...). La máquina tacha de a pares un 1 de cada lado
(X a la izquierda, Y a la derecha) y según de qué lado sobran termina en
GANA, PIERDE o EMPATE. Esos finales son los eventos v, d, e del autómata de flujo.
"""
B = '□'     # blanco

# f: (estado, lee) -> (estado nuevo, escribe, movimiento). L izquierda, R derecha, S no se mueve
F_MT = {
    ('q0', '1'): ('q1', 'X', 'R'),     # tacha un 1 del jugador
    ('q0', '#'): ('q4', '#', 'R'),     # el jugador no tiene más 1: mira si a la casa le quedan
    ('q1', '1'): ('q1', '1', 'R'),     # va hasta el #
    ('q1', '#'): ('q2', '#', 'R'),
    ('q2', 'Y'): ('q2', 'Y', 'R'),     # saltea los 1 de la casa ya tachados
    ('q2', '1'): ('q3', 'Y', 'L'),     # tacha la pareja
    ('q2', B):   ('q5', B, 'S'),       # la casa no tiene pareja: el jugador sumó más
    ('q3', '1'): ('q3', '1', 'L'),     # vuelve hasta la última X
    ('q3', '#'): ('q3', '#', 'L'),
    ('q3', 'Y'): ('q3', 'Y', 'L'),
    ('q3', 'X'): ('q0', 'X', 'R'),
    ('q4', 'Y'): ('q4', 'Y', 'R'),
    ('q4', '1'): ('q6', '1', 'S'),     # a la casa le sobra: la casa sumó más
    ('q4', B):   ('q7', B, 'S'),       # no sobra nada: mismo puntaje
}
Q0 = 'q0'
FINALES = {'q5': 'GANA', 'q6': 'PIERDE', 'q7': 'EMPATE'}   # sin transiciones (estados de parada)
EVENTO = {'GANA': 'v', 'PIERDE': 'd', 'EMPATE': 'e'}


def configuracion(cinta, cabezal, estado):
    """Notación de la cátedra: el estado va justo antes del símbolo que se está leyendo"""
    return ''.join(cinta[:cabezal]) + estado + ''.join(cinta[cabezal:])


def ejecutar(palabra):
    """Corre la MT. Devuelve el estado donde paró y la lista de configuraciones"""
    cinta = [B] + list(palabra) + [B]
    cabezal, estado = 1, Q0
    pasos = [configuracion(cinta, cabezal, estado)]
    while (estado, cinta[cabezal]) in F_MT:
        estado, cinta[cabezal], mov = F_MT[(estado, cinta[cabezal])]
        cabezal += {'L': -1, 'R': 1, 'S': 0}[mov]
        if cabezal == len(cinta):
            cinta.append(B)                       # la cinta es infinita a la derecha
        pasos.append(configuracion(cinta, cabezal, estado))
    return estado, pasos


def evento(jugador, casa):
    """Traducción puntajes -> evento del flujo. Si la casa se pasó (salida P del Moore) gana el jugador"""
    if casa > 21:
        return 'v'
    estado, _ = ejecutar('1' * jugador + '#' + '1' * casa)
    return EVENTO[FINALES[estado]]
