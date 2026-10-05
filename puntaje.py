"""
Autómata de puntaje del Blackjack.
Define un AFND donde el As abre dos caminos (vale 1 u 11), lo convierte en AFD
con automathon (construcción de subconjuntos) y le agrega una salida de Moore
que informa cómo está la mano después de cada carta.
"""
import ast
from automathon import NFA

SIGMA_E = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']   # T = 10, J, Q, K
VALOR = {'A': 1, 'T': 10, **{str(n): n for n in range(2, 10)}}


def f_afnd(i, c):
    """f(p_i, c): el As abre dos caminos. Si una suma pasa de 21, ese camino muere."""
    destinos = [i + 1, i + 11] if c == 'A' else [i + VALOR[c]]
    return {f'p{j}' for j in destinos if j <= 21}


delta = {f'p{i}': {c: f_afnd(i, c) for c in SIGMA_E if f_afnd(i, c)} for i in range(21)}
AFND = NFA(q={f'p{i}' for i in range(22)}, sigma=set(SIGMA_E), delta=delta,
           initial_state='p0', f={'p21'})
AFD = AFND.get_dfa()            # construcción de subconjuntos (automathon no agrega el estado vacío)


def nombre(estado):
    """"['p1', 'p11']" -> B11 (mano blanda), "['p16']" -> D16 (dura)"""
    valores = sorted(int(p[1:]) for p in ast.literal_eval(estado))
    return ('B' if len(valores) == 2 else 'D') + str(valores[-1])


def g(estado):
    """Salida de Moore: S segura, R riesgosa, A alta, V veintiuno (P pasada se maneja aparte)"""
    valores = [int(p[1:]) for p in ast.literal_eval(estado)]
    v = max(valores)
    if v == 21:
        return 'V'
    if v >= 17:
        return 'A'
    return 'S' if len(valores) == 2 or v <= 11 else 'R'

# TODO: agregar el estado X (mano pasada) para completar el AFD -> 33 estados
