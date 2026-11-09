"""
Partida de Blackjack por consola. Une los cuatro modelos del trabajo:
- el autómata de puntaje (AFD + salida de Moore) lleva cada mano carta por carta,
- la máquina de Turing compara los puntajes y decide el resultado (v, d, e),
- el autómata de flujo controla en qué fase de la partida estamos,
- el autómata de pila lleva el balance de la sesión (ganadas vs perdidas).

Uso: python partida.py
"""
import random
import sys

from flujo import TRANSICIONES, AFD_FLUJO
from puntaje import AFD, g, valor
from pila import acepta, recorrido
from turing import ejecutar, EVENTO, FINALES

# Mazo francés con reemplazo: 13 valores, el 10, J, Q y K son el símbolo T del autómata
CARTAS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SIMBOLO = {c: ('T' if c in ('10', 'J', 'Q', 'K') else c) for c in CARTAS}
PALOS = ['♠', '♥', '♦', '♣']
SALIDA = {'S': 'segura', 'R': 'riesgosa', 'A': 'alta', 'V': '¡21!', 'P': 'pasada'}
ESTADOS_FLUJO = {'q0': 'INICIO', 'q1': 'REPARTO', 'q2': 'TURNO_JUGADOR', 'q3': 'TURNO_CASA',
                 'q4': 'GANA', 'q5': 'PIERDE', 'q6': 'EMPATE', 'q7': 'FIN'}


class Mano:
    """Una mano recorre el AFD de puntaje; la salida g del Moore dice cómo está"""

    def __init__(self):
        self.cartas = []
        self.estado = AFD.initial_state

    def agregar(self, carta):
        self.cartas.append(carta)
        self.estado = AFD.delta[self.estado][SIMBOLO[carta[:-1]]]

    def salida(self):
        return g(self.estado)

    def valor(self):
        return valor(self.estado)

    def mostrar(self, ocultar_segunda=False):
        if ocultar_segunda:
            return f'{self.cartas[0]} ??'
        return f'{" ".join(self.cartas)}  ->  {self.valor() if self.salida() != "P" else "+21"} ({SALIDA[self.salida()]})'


class Partida:
    def __init__(self, entrada=input, salida=print, azar=None):
        self.entrada, self.decir = entrada, salida      # se pueden cambiar para las pruebas
        self.azar = azar or random.Random()
        self.estado = 'q0'                              # estado del autómata de flujo
        self.sesion = ''                                # eventos leídos por el flujo

    # --- autómata de flujo ---
    def evento(self, simbolo):
        """Le pasa un evento al AFD de flujo. Si no hay transición es un error del programa"""
        if simbolo not in TRANSICIONES[self.estado]:
            raise RuntimeError(f'El flujo no tiene transición ({self.estado}, {simbolo})')
        self.estado = TRANSICIONES[self.estado][simbolo]
        self.sesion += simbolo

    def carta(self):
        return self.azar.choice(CARTAS) + self.azar.choice(PALOS)

    def preguntar(self, texto, opciones):
        while True:
            try:
                respuesta = self.entrada(texto).strip().lower()
            except EOFError:                            # se cerró la entrada: terminamos la partida
                return opciones[-1]
            if respuesta in opciones:
                return respuesta
            self.decir(f'  Opción no válida. Escribí {" o ".join(opciones)}.')

    # --- una mano ---
    def jugar_mano(self):
        jugador, casa = Mano(), Mano()
        for _ in range(2):
            jugador.agregar(self.carta())
            casa.agregar(self.carta())
        self.evento('r')
        self.decir(f'\nCasa:    {casa.mostrar(ocultar_segunda=True)}')
        self.decir(f'Jugador: {jugador.mostrar()}')

        if jugador.salida() == 'V':                     # 21 con las dos primeras cartas
            self.decir('¡Blackjack natural!')
            self.evento('n')
        else:
            while True:
                if self.preguntar('¿Pedís (p) o te plantás (s)? ', ['p', 's']) == 's':
                    self.evento('s')
                    break
                jugador.agregar(self.carta())
                self.decir(f'Jugador: {jugador.mostrar()}')
                if jugador.salida() == 'P':             # el Moore avisa que se pasó
                    self.evento('x')
                    break
                self.evento('p')
                if jugador.salida() == 'V':             # con 21 no tiene sentido seguir pidiendo
                    self.decir('Llegaste a 21, te plantás.')
                    self.evento('s')
                    break

        if self.estado == 'q3':                         # TURNO_CASA
            self.decir(f'Casa:    {casa.mostrar()}')
            while casa.salida() in ('S', 'R'):          # regla de la casa: pide con S o R
                casa.agregar(self.carta())
                self.evento('h')
                self.decir(f'Casa pide: {casa.mostrar()}')
            if casa.salida() == 'P':
                self.decir('La casa se pasó.')
                self.evento('v')
            else:
                fin, pasos = ejecutar('1' * jugador.valor() + '#' + '1' * casa.valor())
                self.decir(f'MT: {jugador.valor()} contra {casa.valor()} en unario -> '
                           f'{FINALES[fin]} ({len(pasos) - 1} pasos)')
                self.evento(EVENTO[FINALES[fin]])
        else:
            self.decir('Te pasaste de 21.')
            self.decir(f'Casa:    {casa.mostrar()}')

        self.decir(f'Resultado: {ESTADOS_FLUJO[self.estado]}')
        return ESTADOS_FLUJO[self.estado]

    def balance(self):
        """Lee la pila del AP después de los eventos de la sesión"""
        _, _, pila = recorrido(self.sesion)[-1]
        return pila.count('G') - pila.count('P')

    # --- la sesión completa ---
    def jugar(self):
        self.decir('=== El As del Barrio ===')
        self.decir('La casa pide con menos de 17 y se planta con 17 o más.')
        while True:
            self.jugar_mano()
            b = self.balance()
            self.decir(f'Balance de la sesión (pila del AP): {"+" if b > 0 else ""}{b}')
            if self.preguntar('¿Otra mano (c) o terminar (t)? ', ['c', 't']) == 't':
                self.evento('t')
                break
            self.evento('c')

        self.decir(f'\nEventos de la sesión: {self.sesion}')
        self.decir(f'Autómata de flujo: {"ACEPTADA" if AFD_FLUJO.accept(self.sesion) else "rechazada"}')
        if acepta(self.sesion):
            self.decir('Autómata de pila: ACEPTADA, terminaste sin pérdida.')
        else:
            self.decir('Autómata de pila: rechazada, la casa te ganó más manos.')
        self.decir('¡Gracias por jugar!')


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')        # por si la consola no muestra los palos
    except AttributeError:
        pass
    try:
        Partida().jugar()
    except KeyboardInterrupt:
        print('\nPartida cortada.')
