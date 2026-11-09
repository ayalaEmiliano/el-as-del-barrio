// Una mano recorre el AFD de puntaje carta por carta.
// La salida g de la máquina de Moore dice cómo está la mano después de cada carta.
const PALOS = ["♠", "♥", "♦", "♣"];
const VALORES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const SALIDAS = { S: "segura", R: "riesgosa", A: "alta", V: "21", P: "pasada" };

// el 10, J, Q y K son el mismo símbolo T del autómata
function simbolo(carta) {
  return ["10", "J", "Q", "K"].includes(carta.valor) ? "T" : carta.valor;
}

// mazo infinito con reemplazo: cada carta sale al azar entre las 52
function cartaAlAzar() {
  return {
    valor: VALORES[Math.floor(Math.random() * VALORES.length)],
    palo: PALOS[Math.floor(Math.random() * PALOS.length)],
  };
}

class Mano {
  constructor() {
    this.cartas = [];
    this.estado = PUNTAJE.inicial; // D0
    this.salidas = []; // lo que fue emitiendo el Moore
  }

  agregar(carta) {
    this.cartas.push(carta);
    this.estado = PUNTAJE.f[this.estado][simbolo(carta)];
    this.salidas.push(this.salida());
  }

  salida() {
    return PUNTAJE.g[this.estado];
  }

  valor() {
    return PUNTAJE.valor[this.estado]; // 22 si está en X
  }
}
