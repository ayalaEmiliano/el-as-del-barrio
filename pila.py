"""
Autómata de pila del balance de la sesión.
Lee la misma cadena de eventos que el autómata de flujo y usa la pila para
contar cuántas manos ganó y perdió el jugador. Acepta las sesiones que
terminan sin pérdida (ganadas >= perdidas). Un AFD no puede hacerlo porque
la diferencia entre ganadas y perdidas no tiene límite.
"""
from flujo import TRANSICIONES

SIGMA_P = ['Z', 'G', 'P']      # Z fondo de pila, G mano ganada de más, P mano perdida de más
GANA = {'v'}                   # GANA (q4)
PIERDE = {'d', 'x'}            # PIERDE (q5): la casa gana o el jugador se pasa


def push(simbolo, tope):
    """Qué se apila según el evento leído y el tope que se sacó"""
    if simbolo in GANA:
        return {'Z': 'GZ', 'G': 'GG', 'P': ''}[tope]       # una P se cancela con la ganada
    if simbolo in PIERDE:
        return {'Z': 'PZ', 'P': 'PP', 'G': ''}[tope]       # una G se cancela con la perdida
    return tope                                            # resto de eventos: se vuelve a poner el tope


# f: (estado, lee, pop) -> (estado nuevo, push). Sale del AFD de flujo, así las dos tablas coinciden
F_AP = {(q, c, z): (destino, push(c, z))
        for q, fila in TRANSICIONES.items() for c, destino in fila.items() for z in SIGMA_P}
F_AP[('q7', 'Δ', 'Z')] = ('q8', 'Z')     # terminó empatado
F_AP[('q7', 'Δ', 'G')] = ('q8', 'G')     # terminó ganando
# con P en el tope no hay transición: bloqueo, la sesión cerró con pérdida

Q0, Z0, F = 'q0', 'Z', {'q8'}           # q8 = SIN_PERDIDA


def recorrido(cadena):
    """Lista de configuraciones (lo que falta leer, estado, pila con el tope a la izquierda)"""
    estado, pila, resto = Q0, Z0, cadena + 'Δ'
    pasos = [(resto, estado, pila)]
    while resto:
        clave = (estado, resto[0], pila[0])
        if clave not in F_AP:
            break                                          # bloqueo
        estado, apilar = F_AP[clave]
        pila, resto = apilar + pila[1:], resto[1:]
        pasos.append((resto, estado, pila))
    return pasos


def acepta(cadena):
    resto, estado, _ = recorrido(cadena)[-1]
    return resto == '' and estado in F


def mostrar(cadena):
    """Configuraciones con la notación de la cátedra: (resto, estado, pila) ├─ ..."""
    return ' ├─ '.join(f'({r or "λ"}, {q}, {p})' for r, q, p in recorrido(cadena))
