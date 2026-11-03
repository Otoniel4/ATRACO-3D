# Corrección de la prueba integrada R8

Alain rechazó la prueba R7: animaciones insuficientes, puertas y colisiones, ausencia de peatones, mapa con traslado, árboles en calzada y bolsa lateral. Esta revisión trabaja sobre esos fallos. Mantiene Unity **6000.3.27f2**, el mapa **4 × 4 km** y el elenco low poly existente. No declara aprobado el juego ni completa las tareas del GDD.

## Qué cambia

- **Caminar y correr:** seis clips por personaje, incluyendo una carrera propia de 16 fotogramas a 24 fps. Un Blend Tree mezcla reposo, caminar y correr según la velocidad real. El importador conserva la animación en el sitio y el constructor comprueba que Walk y Run muevan el pie después de importar. Se fuerza la evaluación del Animator para evitar que el recorte de render detenga la pose.
- **Bolsa y cámara:** la bolsa del ladrón queda centrada en la espalda, con correas ajustadas y pesos al pecho. La cámara inicial se coloca detrás del personaje. Los otros modelos y sus proporciones se conservan.
- **Puertas:** nueve modelos nuevos propios con marcos, tiradores y zócalos visibles. Ocho accesos dobles giran y el taller usa persiana. Las hojas tienen colisión. Los compradores reservan apertura al entrar/salir; el planificador espera si la puerta todavía bloquea el paso.
- **Colisiones y rutas:** se incluyen los vehículos estacionados. Las superficies con triángulos enormes reciben una malla física subdividida, conservando su geometría. El planificador calcula rodeos con obstáculos dinámicos; considera al jugador y las consultas de cápsula contra la arquitectura. La interpolación espera si el jugador ocupa el siguiente tramo. La cápsula del jugador también colisiona con los cuerpos de NPC.
- **Población:** además de las tres tiendas activas, se añaden **4.153 recorridos** de acera distribuidos por la ciudad. Se seleccionan hasta cuatro recorridos cercanos, con tres peatones por recorrido y reutilización mediante pool. Las compras conservan su población propia. La población empieza cuando la zona está cargada y observa la posición del jugador.
- **Compras:** los tres grafos se contrastan con la geometría estática del mapa. Se eliminan nodos/aristas que tocaban obstáculos y se ajustan los puestos al componente conectado. El mayor ajuste, en restaurante, mide aproximadamente 0,72 m. El agarre de mano se serializa en los prefabs; antes se perdía al cargar la escena.
- **Mapa:** M abre un plano con calles, río, edificios, lugares y un marcador de posición/orientación. No cambia la posición del jugador. La lista muestra distancias; ya no hay botones de viaje.
- **Árboles:** el constructor comprueba la base real de cada árbol importado contra calzadas y asfalto de estacionamiento. Si encuentra una base dentro, la desplaza a un borde libre de asfalto y registra cuántas movió en `TreePlacement.json`. La auditoría Blender de la fuente no reprodujo troncos sobre las mallas originales de calzada; falta confirmar el resultado importado de Unity. Los recorridos de peatones también dejan 0,65 m alrededor de los troncos: se retiraron 117 recorridos que no cumplían ese margen.

## Probar en Unity

1. Detén Play y espera a que termine la compilación. Si quedó abierto un aviso de guardado del intento anterior, pulsa Cancel.
2. Pulsa **Alarma → Crear y probar juego**. La versión R8 prepara otra escena; no reutiliza la escena R7 defectuosa. Reutiliza modelos/materiales de ciudad ya preparados, e importa el elenco y las puertas R8. Crear los prefabs con sus colisiones todavía puede tardar varios minutos.
3. Espera la carga de la zona. Debes ver el personaje desde atrás y la bolsa sobre su espalda.
4. Mantén W unos segundos; después W + Shift. Comprueba dos movimientos distintos de piernas y brazos. Repite con F1–F4.
5. Acércate al mercado: las puertas deben abrirse antes de cruzar. Intenta pasar por un escaparate cerrado y rodea a un peatón. Comprueba que no atravieses esos cuerpos. Ponte en un paso de NPC y apártate: deben esperar o rodear y retomar su recorrido.
6. Observa las aceras y la compra durante tres minutos. Debe haber peatones, clientes y dependiente; comprueba productos, fila, pago, recibo y salida. El contador superior incluye paseantes y compradores.
7. Pulsa M. El mapa debe mostrar tu posición sin trasladarte. Cierra con M y comprueba que sigues en el mismo sitio.
8. Revisa árboles y estacionamientos al caminar. Si queda un tronco sobre asfalto, indica el lugar o muestra el mapa abierto con tu marcador.

Los controles restantes se conservan: ratón para cámara, Esc para liberar cursor, clic derecho para recuperarlo, F6 para catálogo y V para vuelo de revisión. El vuelo sigue siendo una herramienta de prueba.

## Evidencia disponible

- Cinco asambleas compiladas contra las DLL instaladas de Unity.
- Dieciocho personajes y nueve puertas reimportados en Blender; variación del pie medida en Walk/Run. La selección de acciones en la prueba distingue las acciones del esqueleto de las del objeto bolsa.
- Pruebas de puerta cerrada/abierta, rodeo del jugador y reservas sin cruce frontal. Se corrigió un caso donde usar distancias que ignoraban el obstáculo hacía oscilar al NPC.
- 191.739 comprobaciones de dominio; doce compradores atendidos y 34 compras en la prueba base. Prueba adicional de 180 s sobre los tres grafos corregidos, sin rutinas fallidas.
- Dieciocho puestos de compra/fila distintos y conectados. Desnivel máximo entre nodos: 0,17 m.
- Lámina de seis poses, animación de carrera y puerta en `renders/`. Son renders de Blender, no capturas de Unity. El transporte del Blender MCP conectado está cerrado; se utilizó Blender 4.5.15 portable de forma aislada.

**La prueba de Unity sigue pendiente de Alain.** El constructor ejecutará las comprobaciones de clips importados, puertas, agarres y población configurada antes de publicar la escena. Si falla, no la declara completa y conserva las escenas anteriores.

El registro de la nueva carpeta generada incluye `AcceptanceBuild.json`, `TreePlacement.json`, `BuildReport.json` o `BuildFailure.json`. Durante Play, `RuntimeReview.json` registra la carga, el máximo de NPC observados y si se detectó movimiento de pies al caminar/correr. Un campo sin observar no equivale a una prueba aprobada.

## Archivos y límites

Fuentes activas: `Scripts/City/PlaytestR7`, `Scripts/City/Editor/PlaytestR7`, `Scripts/AI/CityLifeR5` y `Scripts/City/Editor/CityLifeR5`. Se mantienen sus asambleas y GUID; no se instalan clases duplicadas. Fuentes y arte R8: `Art/BlenderScripts/PlaytestR8~`. La carpeta R7 sigue siendo necesaria para las exportaciones de ciudad. **Conserva las carpetas Generated anteriores**, porque la nueva escena puede referenciar sus modelos y materiales.

Los recorridos de acera no cruzan calzadas: semáforos y circulación vial siguen siendo tareas posteriores. Las compras completas se mantienen en mercado, joyería y restaurante. Los otros accesos reúnen su diseño y puertas, sin inventar tareas de compra adicionales. Continúa siendo una prueba local; no se implementa ni se valida red, atracos, combate o conducción en esta corrección. Rigs Generic propios; Humanoid final y pulido de agarres siguen pendientes.

Para reproducir el arte con Blender 4.5.15: ejecuta `build_characters.py`, `finalize_backpack.py`, `build_doors.py`, `build_layout.py`, `filter_street_trees.py`, `repair_shop_graph.py` y `draw_map.py` (este último con Python/Pillow). `review_sources.py` localiza las entregas propias previas. `render_review.py`, `render_motion.py` y `validate_exports.py` producen las vistas y verificaciones. Los recursos no se descargaron de internet.

## Explicación para aprender

El modelo, sus clips y el controlador deben comprobarse juntos: tener un archivo llamado Walk no garantiza que mueva el esqueleto importado. El Blend Tree usa la velocidad medida para elegir la pose. El planificador reserva destinos y aristas; ahora también calcula sus distancias considerando los pasos bloqueados. La presentación de compras mantiene su agarre serializado y las puertas reciben solicitudes de paso. Cada pieza conserva una responsabilidad: importar, animar, planificar, mostrar el mapa o registrar la prueba. Compilar comprueba tipos y referencias; los contactos y el aspecto final requieren la prueba real del editor.
