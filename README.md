# El As del Barrio

Trabajo final de Fundamentos Teoricos de la Informatica (UNPSJB, 2026).
Blackjack modelado con un automata de flujo (AFD), un automata de puntaje (AFND -> AFD -> Moore), un automata de pila que lleva el balance de la sesion (ganadas vs perdidas) y una maquina de Turing que compara los puntajes y decide si la mano se gana, se pierde o se empata.

Para jugar en el navegador: abrir `web/index.html` (doble clic, no hace falta instalar nada ni tener internet).

Version por consola y pruebas:

```
pip install -r requirements.txt
python partida.py     # jugar en la terminal
python main.py        # ejemplos de cada automata
python pruebas.py     # pruebas automaticas (las del informe, seccion 5.2)
python exportar_web.py  # regenera web/automatas.js si se cambia algun automata
```

Archivos:

- `flujo.py`: AFD del flujo de la partida
- `puntaje.py`: AFND -> AFD -> Moore del puntaje de la mano
- `pila.py`: AP del balance de la sesion (acepta las sesiones sin perdida)
- `turing.py`: MT que compara jugador#casa en unario (GANA / PIERDE / EMPATE)
- `partida.py`: la partida por consola, une los cuatro modelos
- `main.py`: ejemplos de cada automata por separado
- `pruebas.py`: pruebas automaticas con semillas fijas (puntaje contra el calculo directo, minimizacion, MT para todos los pares de puntajes, sesiones simuladas)
- `web/`: la version web (index.html, style.css, logica.js, Mano.js, maquinas.js). `automatas.js` lo genera `exportar_web.py` con las mismas tablas de los .py
- `jflap/`: los mismos automatas en JFLAP (`balance_pila.jff` es de tipo pda, `comparar_mt.jff` de tipo turing) y sus grafos
- `docs/`: el informe del avance y el informe final (Word y PDF)

Estado: entrega final.

Integrantes: Ayala Emiliano, Curallan Lucas, Pintado Jose, Vilte Elias.
