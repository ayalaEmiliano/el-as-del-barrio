// Lógica de la página: une los cuatro autómatas con la mesa.
// Cada acción del jugador es un símbolo del alfabeto del autómata de flujo,
// y los botones se habilitan solo si el estado actual tiene transición con ese símbolo.

let estadoFlujo = FLUJO.inicial;
let sesion = ""; // cadena de eventos que leyó el flujo
let jugador = new Mano();
let casa = new Mano();
let casaTapada = true;
let ocupado = false; // mientras hay una animación no se aceptan acciones
let numeroMano = 1;
const totales = { GANA: 0, PIERDE: 0, EMPATE: 0 };

const $ = (id) => document.getElementById(id);
const esperar = (ms) => new Promise((listo) => setTimeout(listo, ms));

// ---------- autómata de flujo ----------
function evento(simbolo) {
  const nuevo = moverFlujo(estadoFlujo, simbolo);
  if (nuevo === null) {
    throw new Error(`El flujo no tiene transición (${estadoFlujo}, ${simbolo})`);
  }
  estadoFlujo = nuevo;
  sesion += simbolo;
  dibujarFlujo();
}

function puede(simbolo) {
  return !ocupado && moverFlujo(estadoFlujo, simbolo) !== null;
}

function actualizarBotones() {
  $("btn-repartir").disabled = !puede("r");
  $("btn-pedir").disabled = !puede("p");
  $("btn-plantarse").disabled = !puede("s");
}

// ---------- dibujo de la mesa ----------
function crearCarta(carta, tapada) {
  const roja = carta.palo === "♥" || carta.palo === "♦";
  const div = document.createElement("div");
  div.className = "carta" + (tapada ? " tapada" : "");
  div.innerHTML = `
    <div class="interior">
      <div class="cara frente${roja ? " roja" : ""}">
        <div class="esquina arriba">${carta.valor}<span>${carta.palo}</span></div>
        <div class="centro">${carta.palo}</div>
        <div class="esquina abajo">${carta.valor}<span>${carta.palo}</span></div>
      </div>
      <div class="cara atras"></div>
    </div>`;
  return div;
}

function darCarta(mano, contenedor, tapada = false) {
  const carta = cartaAlAzar();
  mano.agregar(carta);
  $(contenedor).appendChild(crearCarta(carta, tapada));
  dibujarPuntajes();
}

function textoPuntaje(mano) {
  return mano.salida() === "P" ? "+21" : String(mano.valor()); // en X no hay valor, solo sabemos que pasó 21
}

function dibujarPuntajes() {
  const pj = $("puntaje-jugador");
  pj.textContent = jugador.cartas.length ? textoPuntaje(jugador) : "";
  pj.className = "puntaje salida-" + jugador.salida();

  const pc = $("puntaje-casa");
  if (casa.cartas.length === 0) {
    pc.textContent = "";
  } else if (casaTapada) {
    pc.textContent = "?";
    pc.className = "puntaje";
  } else {
    pc.textContent = textoPuntaje(casa);
    pc.className = "puntaje salida-" + casa.salida();
  }
  dibujarMoore();
}

function mensaje(texto) {
  $("mensaje").textContent = texto;
}

// ---------- panel: flujo ----------
function dibujarFlujo() {
  const contenedor = $("estados-flujo");
  contenedor.innerHTML = "";
  const clase = { q4: "gana", q5: "pierde", q6: "empate" };
  for (const [q, nombre] of Object.entries(FLUJO.nombres)) {
    const div = document.createElement("div");
    div.className = "estado";
    if (FLUJO.finales.includes(q)) div.classList.add("final");
    if (q === estadoFlujo) div.classList.add("activo");
    if (clase[q]) div.classList.add(clase[q]);
    div.innerHTML = `<b>${q}</b>${nombre.replace("_", " ")}`;
    contenedor.appendChild(div);
  }
  // se muestra la parte final de la cadena para que no se haga eterna
  const cadena = sesion.length > 40 ? "…" + sesion.slice(-40) : sesion;
  $("cadena-flujo").textContent = cadena || "λ";
  actualizarBotones();
}

// ---------- panel: puntaje (AFD + Moore) ----------
function dibujarMoore() {
  pintarMano(jugador, "estado-jugador", "salidas-jugador", false);
  pintarMano(casa, "estado-casa", "salidas-casa", casaTapada);
}

function pintarMano(mano, idEstado, idSalidas, oculta) {
  const visibles = oculta ? mano.salidas.slice(0, 1) : mano.salidas;
  $(idEstado).textContent = oculta && mano.cartas.length > 1 ? "?" : mano.estado;
  const contenedor = $(idSalidas);
  // solo se agregan las salidas nuevas, así la animación no se repite
  while (contenedor.children.length > visibles.length) contenedor.lastChild.remove();
  for (let i = contenedor.children.length; i < visibles.length; i++) {
    const span = document.createElement("span");
    span.className = "salida-" + visibles[i];
    span.textContent = visibles[i];
    contenedor.appendChild(span);
  }
}

// ---------- panel: máquina de Turing ----------
function dibujarCinta(cinta, cabezal, estado) {
  const contenedor = $("cinta");
  contenedor.innerHTML = "";
  cinta.forEach((simbolo, i) => {
    const celda = document.createElement("div");
    celda.className = "celda";
    if (simbolo === "X") celda.classList.add("x");
    if (simbolo === "Y") celda.classList.add("y");
    if (simbolo === "#") celda.classList.add("sep");
    if (i === cabezal) {
      celda.classList.add("cabezal");
      celda.dataset.estado = estado;
    }
    celda.textContent = simbolo;
    contenedor.appendChild(celda);
  });
  const celdaCabezal = contenedor.children[cabezal];
  if (celdaCabezal) {
    contenedor.scrollLeft = celdaCabezal.offsetLeft - contenedor.clientWidth / 2;
  }
}

// corre la MT y la anima en más o menos un segundo y medio (son cientos de pasos)
async function animarTuring(palabra) {
  const corrida = ejecutarTuring(palabra);
  const cinta = [TURING.blanco, ...palabra, TURING.blanco];
  const total = corrida.pasos.length;
  const porCuadro = Math.max(1, Math.ceil(total / 90));
  dibujarCinta(cinta, 1, TURING.inicial);
  for (let i = 0; i < total; i++) {
    const paso = corrida.pasos[i];
    cinta[paso.cabezal] = paso.escribe;
    const cabezal = paso.cabezal + { L: -1, R: 1, S: 0 }[paso.mov];
    if (cabezal === cinta.length) cinta.push(TURING.blanco);
    if (i % porCuadro === 0 || i === total - 1) {
      dibujarCinta(cinta, cabezal, paso.nuevo);
      $("info-mt").innerHTML = `Paso <b>${i + 1}</b> de ${total} · estado <b>${paso.nuevo}</b>`;
      await esperar(16);
    }
  }
  $("info-mt").innerHTML = `<b>${corrida.resultado}</b> en ${total} pasos (estado final ${corrida.estado})`;
  return corrida;
}

// ---------- panel: autómata de pila ----------
function dibujarPila() {
  const pila = pilaActual(sesion);
  const contenedor = $("pila");
  contenedor.innerHTML = "";
  const maximo = 7; // si la pila crece mucho se muestran las de arriba y cuántas faltan
  [...pila].slice(0, maximo).forEach((simbolo) => {
    const ficha = document.createElement("div");
    ficha.className = "ficha " + simbolo;
    ficha.textContent = simbolo;
    contenedor.appendChild(ficha);
  });
  if (pila.length > maximo) {
    const resto = document.createElement("div");
    resto.className = "ficha mas";
    resto.textContent = `+${pila.length - maximo}`;
    contenedor.appendChild(resto);
  }
  const balance = (pila.match(/G/g) || []).length - (pila.match(/P/g) || []).length;
  const pill = $("balance-display");
  pill.textContent = `Balance ${balance > 0 ? "+" : ""}${balance}`;
  pill.className = "pill balance" + (balance > 0 ? " positivo" : balance < 0 ? " negativo" : "");
  $("pila-texto").textContent =
    balance > 0 ? `Vas ganando por ${balance}` : balance < 0 ? `Vas perdiendo por ${-balance}` : "Sesión pareja";
}

// ---------- una mano ----------
function limpiarMesa() {
  jugador = new Mano();
  casa = new Mano();
  casaTapada = true;
  $("cartas-jugador").innerHTML = "";
  $("cartas-casa").innerHTML = "";
  dibujarPuntajes();
}

async function repartir() {
  if (!puede("r")) return;
  ocupado = true;
  actualizarBotones();
  limpiarMesa();
  mensaje("Repartiendo…");
  darCarta(jugador, "cartas-jugador");
  await esperar(320);
  darCarta(casa, "cartas-casa");
  await esperar(320);
  darCarta(jugador, "cartas-jugador");
  await esperar(320);
  darCarta(casa, "cartas-casa", true); // la segunda de la casa va boca abajo
  await esperar(350);
  evento("r");

  if (jugador.salida() === "V") {
    mensaje("¡Blackjack natural!");
    evento("n");
    await esperar(700);
    await turnoCasa();
    return;
  }
  mensaje("¿Pedís o te plantás?");
  ocupado = false;
  actualizarBotones();
}

async function pedir() {
  if (!puede("p")) return;
  ocupado = true;
  actualizarBotones();
  darCarta(jugador, "cartas-jugador");
  await esperar(400);

  if (jugador.salida() === "P") {
    // el Moore avisa que la mano se pasó: el evento es x en lugar de p
    evento("x");
    mensaje("Te pasaste de 21");
    await esperar(500);
    await revelarCasa();
    await finMano("Te pasaste de 21.", "");
    return;
  }
  evento("p");
  if (jugador.salida() === "V") {
    mensaje("¡21! Te plantás");
    await esperar(600);
    evento("s");
    await turnoCasa();
    return;
  }
  mensaje("¿Pedís o te plantás?");
  ocupado = false;
  actualizarBotones();
}

async function plantarse() {
  if (!puede("s")) return;
  ocupado = true;
  evento("s");
  mensaje(`Te plantás con ${jugador.valor()}`);
  await esperar(500);
  await turnoCasa();
}

async function revelarCasa() {
  casaTapada = false;
  const tapada = document.querySelector("#cartas-casa .tapada");
  if (tapada) tapada.classList.remove("tapada");
  dibujarPuntajes();
  await esperar(650);
}

async function turnoCasa() {
  mensaje("Juega la casa");
  await revelarCasa();
  // regla de la casa: pide mientras la salida del Moore sea S o R
  while (casa.salida() === "S" || casa.salida() === "R") {
    darCarta(casa, "cartas-casa");
    evento("h");
    await esperar(700);
  }

  if (casa.salida() === "P") {
    mensaje("La casa se pasó");
    evento("v");
    await finMano(`La casa se pasó de 21. Vos tenías ${jugador.valor()}.`, "");
    return;
  }

  mensaje("La máquina de Turing compara los puntajes…");
  const corrida = await animarTuring("1".repeat(jugador.valor()) + "#" + "1".repeat(casa.valor()));
  evento(EVENTO_MT[corrida.resultado]);
  await finMano(
    `Tus ${jugador.valor()} contra ${casa.valor()} de la casa.`,
    `La MT terminó en ${corrida.resultado} después de ${corrida.pasos.length} pasos.`
  );
}

async function finMano(detalle, detalleMT) {
  const resultado = FLUJO.nombres[estadoFlujo]; // GANA, PIERDE o EMPATE
  totales[resultado]++;
  dibujarPila();
  mensaje({ GANA: "¡Ganaste la mano!", PIERDE: "La casa gana", EMPATE: "Empate" }[resultado]);
  await esperar(900);
  mostrarResultado(resultado, detalle, detalleMT);
}

// ---------- pantallas ----------
function mostrarResultado(resultado, detalle, detalleMT) {
  const titulo = $("resultado-titulo");
  titulo.textContent = { GANA: "¡GANASTE!", PIERDE: "PERDISTE", EMPATE: "EMPATE" }[resultado];
  titulo.className = { GANA: "gana", PIERDE: "", EMPATE: "empate" }[resultado];
  $("resultado-detalle").textContent = detalle;
  $("resultado-mt").textContent = detalleMT;
  $("resultado-screen").style.display = "flex";
  ocupado = false;
  actualizarBotones();
}

function otraMano() {
  if ($("resultado-screen").style.display === "none") return;
  $("resultado-screen").style.display = "none";
  evento("c");
  numeroMano++;
  $("mano-display").textContent = `Mano ${numeroMano}`;
  repartir().catch(mostrarError);
}

function terminar() {
  if ($("resultado-screen").style.display === "none") return;
  $("resultado-screen").style.display = "none";
  evento("t");
  mensaje("Fin de la partida");
  mostrarFin();
}

function mostrarFin() {
  $("fin-manos").textContent = numeroMano;
  $("fin-ganadas").textContent = totales.GANA;
  $("fin-perdidas").textContent = totales.PIERDE;
  $("fin-empates").textContent = totales.EMPATE;
  $("fin-cadena").textContent = sesion;

  const flujo = aceptaFlujo(sesion);
  const fFlujo = $("fin-flujo");
  fFlujo.textContent = `Autómata de flujo: ${flujo ? "ACEPTADA" : "rechazada"} (terminó en ${estadoFlujo} ${FLUJO.nombres[estadoFlujo]})`;
  fFlujo.className = "veredicto " + (flujo ? "si" : "no");

  const pila = aceptaPila(sesion);
  const fPila = $("fin-pila");
  fPila.textContent = pila
    ? "Autómata de pila: ACEPTADA, terminaste sin pérdida"
    : "Autómata de pila: rechazada, la casa te ganó más manos";
  fPila.className = "veredicto " + (pila ? "si" : "no");

  $("fin-screen").style.display = "flex";
}

function mostrarError(error) {
  console.error(error);
  mensaje("Ocurrió un error, recargá la página");
}

// ---------- botones y teclado ----------
$("btn-repartir").onclick = () => repartir().catch(mostrarError);
$("btn-pedir").onclick = () => pedir().catch(mostrarError);
$("btn-plantarse").onclick = () => plantarse().catch(mostrarError);
$("otra-btn").onclick = otraMano;
$("terminar-btn").onclick = terminar;
$("nuevo-btn").onclick = () => location.reload();

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.altKey || e.metaKey || e.repeat) return;
  const tecla = e.key.toLowerCase();
  if (tecla === "r") repartir().catch(mostrarError);
  if (tecla === "p") pedir().catch(mostrarError);
  if (tecla === "s") plantarse().catch(mostrarError);
  if (tecla === "c") otraMano();
  if (tecla === "t") terminar();
});

function initGame() {
  dibujarFlujo();
  dibujarPuntajes();
  dibujarPila();
  dibujarCinta([TURING.blanco, "1", "#", "1", TURING.blanco], 1, TURING.inicial);
  actualizarBotones();
}

initGame();
