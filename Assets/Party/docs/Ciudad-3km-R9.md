# Alarma: revisión R9, ciudad de 3 × 3 km

Esta revisión corrige la prueba rechazada. Mantiene Unity **6000.3.27f2**, los personajes low poly propios y las versiones anteriores. La prueba funcional dentro de Unity y la aprobación visual siguen pendientes de Alain.

## Probar en Unity

1. Detén Play si está activo. Activa Unity y espera a que termine de compilar.
2. Pulsa **Alarma → Crear y probar juego**. El mismo botón detecta R9 y construye una escena nueva; no reutiliza la escena fallida R8. Respalda las escenas abiertas antes de preparar contenido.
3. Espera la primera importación: se preparan 153 partes de ciudad, los personajes, materiales y colliders. Puede tardar varios minutos. Si cancela o falla, conserva la Console para identificar el primer error rojo.
4. Aparecerás dentro de **El Escondite**. Camina hacia la fachada, atraviesa el acceso central y aléjate: las dos hojas deben abrirse y cerrarse. No debe aparecer ninguna puerta suelta en el centro del local.
5. Sal a la zona comercial contigua. Visita **Mini Todo**, **Brilla**, **Café Pánico**, **Buena Pinta** y **Don Trueque**. Observa al menos dos minutos: elegir producto, tomarlo de la estantería, llevarlo, esperar turno, entregarlo, cobrar y salir. El contador «Compras» y la caja deben aumentar.
6. Mantén **Shift + WASD** para correr y suelta Shift para caminar. Comprueba los cuatro personajes con F1–F4. **M** muestra el plano de 3 × 3 km y tu posición. Ratón: cámara; Esc libera el cursor; clic derecho lo captura. V y F6 siguen disponibles para revisar ciudad y modelos.
7. Recorre ambos sentidos de las puertas, acércate a una fila y cruza el paso de un peatón. Revisa que no atraviesen mobiliario ni se atasquen. Informa de cualquier fallo visible antes de aprobar esta corrección.

## Cambios

- Ciudad recortada físicamente a **3000 × 3000 m**, sin encoger casas o personas. La zona comercial está organizada en parcelas escalonadas que dejan libre la avenida diagonal.
- Inicio en un escondite con sofá, taquillas y tablero. Tiene **cuatro puntos reservados de aparición** para el futuro grupo. La sesión actual continúa siendo local; Lobby/Relay y la sincronización online pertenecen a su siguiente tarea.
- Se reconstruyen el escondite y cinco comercios con entradas de 2,4 m, mobiliario, letreros, caja y mercancía según su función. Los demás edificios de la ciudad permanecen como ambientación; no se atribuye una rutina de compra a cada edificio del mapa.
- Los FBX de ciudad, puertas y productos incluyen tres anclas conocidas. El constructor comprueba su orientación y posición al importar. Esto evita colocar las puertas y la geometría usando suposiciones sobre los ejes del FBX.
- Productos independientes por tienda: cartón de leche, estuche de joyería, café, ropa doblada y herramientas. El NPC toma el objeto visible, lo presenta en caja y recibe el comprobante. Las estaciones se reservan; la fila y el cobro se gestionan por cliente. La reposición visual permite repetir la prueba.
- Hasta veinte compradores repartidos entre cinco tiendas, cinco dependientes y peatones de acera cercanos. La animación al esperar usa reposo; al desplazarse, su velocidad sigue el avance real.
- Carrera propia nueva en los dieciocho modelos: apoyo alterno, fase de vuelo, rodillas flexionadas, inclinación del tronco y codos doblados. Es animación low poly de prototipo, pendiente de revisar en el juego.
- Se conservan hojas y pasto con viento y se añaden macetas completas fuera de los accesos. Ya no se trasladan árboles mediante una prueba de asfalto en dos dimensiones antes de comprobar los ejes importados.

## Comprobaciones realizadas

| Comprobación fuera de Unity | Resultado |
| --- | --- |
| Compilación contra las DLL instaladas | 5 asambleas correctas |
| Tamaño real de la geometría | 3000 × 3000 m |
| FBX de ciudad exportados con tres anclas | 153 de 153; 42.531 objetos de malla |
| Personajes reimportados, clips Walk/Run muestreados | 18 de 18 |
| Productos y tipos de puerta reimportados | 7 productos/utilería y 3 puertas |
| Puestos de selección y fila | 30 distintos y conectados |
| Compras simuladas sobre los cinco grafos finales | 10 por tienda en 180 s |
| Dominio, fila, cobro, cancelación y tráfico | 191.739 comprobaciones; separación mínima 0,495 m |
| Geometría nueva frente al borde de calzada | Separación mínima 4 m |

Los renders incluidos son de **Blender**, no capturas de una partida de Unity. No se abrió Unity ni se ejecutó Play desde el agente. Compilar y simular el dominio no demuestra por sí solo que la integración visual y física haya quedado correcta.

## Comprobación al pulsar el botón

Antes de iniciar Play, el constructor guarda la escena y crea una escena de comprobación física aislada con los mismos prefabs y colliders importados. Comprueba los cuatro puntos del escondite, su recorrido de salida, el bloqueo de las ocho puertas de dos hojas y los seis accesos nuevos abiertos. Filtra los grafos contra obstáculos reales y vuelve a simular compras en cada tienda. Si algo falla, muestra el motivo y no publica la escena como lista.

En `Assets/Party/Generated/AlarmaPrueba_<fecha>/` quedan:

- `SpatialCalibration.json`: orientación, posición y error de las anclas importadas.
- `PhysicalAcceptance.json`: accesos, puestos del escondite y compras sobre la geometría importada. Solo se genera si pasan.
- `AcceptanceBuild.json`: clips y componentes preparados.
- `RuntimeReview.json`: lo observado durante **tu** Play: caminar/correr, población, compras/caja por tienda y rutinas fallidas. Se actualiza cada cinco segundos.

## Archivos creados o modificados

- Arte, recetas, FBX y evidencias nuevos: `Assets/Party/Art/BlenderScripts/PlaytestR9~/`.
- Fuentes activas actualizadas: `Assets/Party/Scripts/City/PlaytestR7/`, `Scripts/City/Editor/PlaytestR7/`, `Scripts/AI/CityLifeR5/` y `Scripts/City/Editor/CityLifeR5/`. Se conservan rutas, asambleas y GUID existentes.
- Guía: `Assets/Party/docs/Ciudad-3km-R9.md`; registro de alcance en AGENTS/TASKS y de autoría en LICENSES.
- `installation.json` enumera cada fuente modificada con SHA-256. Desde R9.2 el botón conserva solo la carpeta `Generated` vigente; si falla, la borra y deja el error en `Generated/AlarmaPlaytestFailure.json`.

## Regenerar el arte

Desde `PlaytestR9~`, usa Blender 4.5.x con `-b -P <script>` en este orden: `build_neighborhood.py`, `export_world.py`, `build_goods_doors.py`, `build_run.py`. Después ejecuta `finish_metadata.py` con Python y Pillow. `validate_assets.py`, `check_roads.py` y `render_reviews.py` revisan la exportación y generan vistas. Las recetas encuentran las fuentes propias anteriores junto a ellas; `ALARMA_PROJECT` permite indicar otro proyecto.

### Vegetación ligera (R9.3)

La ciudad que usa Unity sale de `Villa_Alarma_3000_R9_Ligera.blend`, no del `.blend` original. Para regenerarla:

1. `blender -b --factory-startup -P lighten_vegetation.py`: lee el original y guarda la versión ligera. Los presupuestos (`TREE_BUDGET`, `GRASS_BUDGET`, `PLANT_RATIO`) están al principio del script; el informe queda en `vegetation_lite.json`.
2. `ALARMA_R9_WORLD=Villa_Alarma_3000_R9_Ligera.blend blender -b --factory-startup -P export_world.py`: exporta las 153 celdas a `export/World`.

Sin la variable `ALARMA_R9_WORLD`, `export_world.py` vuelve a exportar la ciudad original.

Las medidas del barrio, posiciones y colores están al principio de `build_neighborhood.py`; los parámetros de carrera están al principio de `build_run.py`. Los `.blend` permiten editar directamente. Las fuentes de Unity se entregan separadas de las recetas de arte.

## Explicación para aprender

La forma del edificio, la puerta y los puntos de compra parten del mismo sistema de coordenadas. Las anclas verifican que Unity conserve esa relación al importar. Cada comprador sigue una máquina de estados; la tienda reserva mercancía, turnos y pagos. La presentación mueve el objeto visible según esos eventos. Así, las reglas de compra se prueban sin depender del render, y el constructor comprueba por separado la geometría real. Separar esas responsabilidades ayuda a localizar un fallo de rutas, uno de cobro o uno visual sin mezclar los tres.

No se cierra ninguna task ni se crea commit de cierre hasta la prueba y confirmación de Alain.
