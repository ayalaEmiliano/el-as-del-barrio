// Funciones que recorren los autómatas usando las tablas de automatas.js.
// No tocan la página: así se pueden probar solas y la lógica queda igual que en Python.

// ---------- autómata de flujo (AFD) ----------
function moverFlujo(estado, simbolo) {
  const destino = FLUJO.f[estado][simbolo];
  return destino === undefined ? null : destino; // null = no hay transición (bloqueo)
}

function aceptaFlujo(cadena) {
  let estado = FLUJO.inicial;
  for (const simbolo of cadena) {
    estado = moverFlujo(estado, simbolo);
    if (estado === null) return false;
  }
  return FLUJO.finales.includes(estado);
}

// ---------- autómata de pila (AP del balance) ----------
// devuelve las configuraciones (lo que falta leer, estado, pila con el tope a la izquierda)
function recorridoPila(cadena) {
  let estado = PILA.inicial;
  let pila = PILA.fondo;
  let resto = cadena + "Δ";
  const pasos = [{ resto, estado, pila }];
  while (resto.length > 0) {
    const transicion = PILA.f[`${estado},${resto[0]},${pila[0]}`];
    if (!transicion) break; // bloqueo
    estado = transicion[0];
    pila = transicion[1] + pila.slice(1);
    resto = resto.slice(1);
    pasos.push({ resto, estado, pila });
  }
  return pasos;
}

function aceptaPila(cadena) {
  const pasos = recorridoPila(cadena);
  const ultimo = pasos[pasos.length - 1];
  return ultimo.resto === "" && PILA.finales.includes(ultimo.estado);
}

// pila después de los eventos jugados hasta ahora (para dibujarla)
function pilaActual(cadena) {
  const pasos = recorridoPila(cadena);
  return pasos[pasos.length - 1].pila;
}

// ---------- máquina de Turing (compara jugador#casa en unario) ----------
// guarda cada paso para poder animar la cinta
function ejecutarTuring(palabra) {
  const B = TURING.blanco;
  const cinta = [B, ...palabra, B];
  let cabezal = 1;
  let estado = TURING.inicial;
  const pasos = [];
  let transicion = TURING.f[`${estado},${cinta[cabezal]}`];
  while (transicion) {
    const [nuevo, escribe, mov] = transicion;
    pasos.push({ estado, cabezal, lee: cinta[cabezal], escribe, mov, nuevo });
    cinta[cabezal] = escribe;
    estado = nuevo;
    cabezal += { L: -1, R: 1, S: 0 }[mov];
    if (cabezal === cinta.length) cinta.push(B); // la cinta sigue a la derecha
    if (pasos.length > 100000) throw new Error("La MT no para"); // por las dudas
    transicion = TURING.f[`${estado},${cinta[cabezal]}`];
  }
  return { estado, resultado: TURING.finales[estado], cinta, cabezal, pasos };
}

const EVENTO_MT = { GANA: "v", PIERDE: "d", EMPATE: "e" };

// traducción puntajes -> evento del flujo (si la casa se pasó gana el jugador sin usar la MT)
function eventoResultado(jugador, casa) {
  if (casa > 21) return "v";
  const corrida = ejecutarTuring("1".repeat(jugador) + "#" + "1".repeat(casa));
  return EVENTO_MT[corrida.resultado];
}
