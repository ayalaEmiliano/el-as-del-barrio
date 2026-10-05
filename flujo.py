from automathon import DFA

RESULTADO = {'c': 'q0', 't': 'q7'}                     # nueva mano o terminar
TRANSICIONES = {
    'q0': {'r': 'q1'},                                 # INICIO
    'q1': {'n': 'q3', 'p': 'q2', 's': 'q3', 'x': 'q5'},  # REPARTO
    'q2': {'p': 'q2', 's': 'q3', 'x': 'q5'},           # TURNO_JUGADOR
    'q3': {'h': 'q3', 'v': 'q4', 'd': 'q5', 'e': 'q6'},  # TURNO_CASA
    'q4': RESULTADO, 'q5': RESULTADO, 'q6': RESULTADO,  # GANA / PIERDE / EMPATE
    'q7': {},                                          # FIN
}
AFD_FLUJO = DFA(q=set(TRANSICIONES), sigma=set('rpsxhnvdect'), delta=TRANSICIONES,
                initial_state='q0', f={'q7'})

# TODO: función de traducción que genere estos eventos a partir de las manos
