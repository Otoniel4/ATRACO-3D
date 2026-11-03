# Ciudad viva R5 — Alarma

Entrega del **2 de noviembre de 2026**. Alain aprobó la dirección de vegetación R4 y pidió peatones que paseen, entren a comprar y objetos de locales más elaborados. Se mantienen Unity **6000.3.27f2**, URP **17.3.0**, el estilo low poly de colores planos y los **4.000 × 4.000 m**.

## Qué se entrega

Hay tres resultados relacionados, con distinto alcance:

1. **Revisión animada en Blender:** diez civiles en un distrito comercial. Se ve entrar, mirar productos, esperar turno, pagar y salir con bolsa; las puertas del minimercado se abren al acercarse. El vídeo muestra cuatro compras en 24 segundos. Esta revisión está simulada y horneada para inspección artística; no es una captura de Unity.
2. **Mapa completo actualizado:** nueve interiores con 103 instancias de objetos detallados, diez personajes de revisión en el minimercado y dos paseantes adicionales delante de cada uno de los otros ocho locales: **26 personajes animados**. Se conservan las celdas, la cámara acorazada, el arbolado y las máscaras de viento. Se sustituyen las tres antiguas figuras estáticas de escala. Los paseantes adicionales recorren explanadas cortas; no hay navegación autónoma por los 16 km² en este archivo.
3. **Prototipo local para Unity:** componentes C# de navegación, rutinas, colas, animación, puertas y población reutilizable. Un menú de editor prepara una escena pequeña con minimercado, ropa y restaurante, NavMesh, diez variantes, hasta 24 peatones y tres dependientes. El código se compiló contra las bibliotecas instaladas; su ejecución en Play y la importación visual necesitan la prueba de Alain.

**La sincronización online sigue pendiente del prototipo de red.** La escena preparada es local y no incorpora Lobby, Relay, NetworkObject ni NetworkAnimator. No se han declarado completas las Tasks 02, 04, 12 o 26. Tampoco implementa intimidación, tráfico, semáforos o combate.

## Objetos y personajes

Se construyeron **32 piezas propias**: estantería con productos y etiquetas, refrigerador, puesto de cobro con cinta y lector, frutas, canasta, bolsa, terminal, caja registradora, vitrina, busto para collares, escritorio con teclado, silla de oficina, cajero, poste de fila, perchero con prendas y colgadores, mesa de ropa, maniquí, cafetera, horno, pizza, mesa de comedor, gabinete de herramientas, compresor, estantería de equipos, casilleros, sofá, tablero de planificación, silla de comedor, puerta de bóveda, elevador de taller, cámara y reloj. Las piezas mantienen geometría simple, pero incorporan detalles que explican su función.

Se preservaron los diez civiles de la revisión R3: sus mallas y pesos no se editaron para esta entrega. Cada uno tiene cinco clips propios: **Idle, Walk, Browse, Pay y CarryWalk**; son **50 clips** en total. La marcha resuelve las piernas y anima el apoyo de los pies; las manos se relajan al andar y una mantiene la bolsa al salir. Son animaciones de estudio sobre nuestros rigs de 21 huesos, sin archivos de Mixamo. El constructor usa **Generic**, con clips de cada propio modelo; no declara validado un Avatar Humanoid ni el retargeting final.

Las compras son una rutina ambiental: producen un evento y una bolsa visible. No descuentan dinero de la banda, no alteran Cloud Save ni implementan inventarios o existencias comerciales.

## Abrir la revisión en Blender

1. Abre `Ciudad_Viva_Demo_R5.blend`, selecciona `LifeR5_AnimatedDistrict`, vuelve al fotograma **1** y pulsa **Espacio**.
2. La revisión dura 576 fotogramas a 24 fps. Cambia entre exterior e interior para mostrar la fila y la caja. Los techos se ocultan en esta demo para ver el interior; las piezas siguen separadas.
3. Abre `Villa_Alarma_Ciudad_Viva_R5.blend` para revisar el mapa completo. La escena inicial `CityR5_LifeStreet` enfoca el minimercado y conserva su techo. Las otras escenas `CityR5_*` permiten explorar la ciudad. Los NPC de este archivo también tienen trayectorias horneadas para la revisión.
4. `Objetos_Locales_R5.blend` contiene el kit y `Civiles_Animados_R5.blend` los civiles con clips editables. Las versiones anteriores permanecen disponibles.

El vídeo MP4 se renderizó a 960 × 720, 12 fps y 24 segundos: 288 imágenes reales. El GIF reduce la frecuencia para facilitar su revisión. El retorno al inicio de una rutina completa de compras no se presenta como un bucle de trayectoria sin cortes.

## Pasos para el editor de Unity

1. Espera la importación y compilación de los scripts instalados en `Assets/Party/Scripts/AI/CityLifeR5` y `Assets/Party/Scripts/City/Editor/CityLifeR5`. Mantén la versión actual de Unity.
2. Ejecuta **Alarma → Ciudad → Crear demo local R5**. El constructor lee esta entrega de `Assets/Party/Art/BlenderScripts/CityLifeR5~`. Copia solo las piezas y personajes del distrito a una carpeta nueva en `Assets/Party/Generated/CityLifeR5_<fecha>`, prepara materiales, clips, controladores, prefabs, marcadores y un NavMesh. Omite el FBX del mapa completo.
3. El menú conserva las escenas ya abiertas y crea la demo de forma aditiva. **Abre después únicamente la escena `Scenes/CityLife_R5.unity` recién creada antes de pulsar Play**, para evitar cámaras, luces o lógica de otra escena cargada. La carpeta generada aparece seleccionada en Project/Console. No se sobrescribe una escena existente.
4. Si aparece un error de importación o un punto fuera del NavMesh, revisa el objeto indicado en Console y los marcadores `Routine_<local>`. El constructor comprueba rutas completas desde la entrada a los destinos antes de guardar la escena. No se considera probado por el hecho de compilar C#.
5. En Play, usa **WASD** para mover la cámara de revisión, **Q/E** para bajar/subir, **Shift** para acelerar y el **botón derecho del ratón** para girar. Acércate al minimercado, la tienda de ropa y el restaurante.
6. Selecciona `Población local R5` para observar el recuento activo y el asset `Data/PedestrianSettings`: presupuesto, densidad por local, velocidades, distancias y tiempos. En cada `Routine_*` se ve el contador ambiental de compras.

Los modelos conservan escala 1 y colores planos. Las hojas del distrito reutilizan el shader de viento R3; si ya existe, se reutiliza. Si falta, el constructor importa nuestra copia incluida. Los materiales de vidrio se configuran transparentes. Los controladores usan clips en el sitio y `applyRootMotion = false`: el NavMeshAgent desplaza al personaje.

## Cómo probarlo

1. **Caminar:** observa piernas y brazos de varios civiles durante un minuto. Los peatones deben mantenerse en las veredas del distrito. No hay cruces controlados por semáforos en esta demo.
2. **Comprar:** sigue a un cliente desde la puerta al punto de productos, la fila y la caja. Debe detenerse, pagar, mostrar una bolsa y salir. El dependiente responde a la compra.
3. **Fila:** comprueba que solo paga el primero y que el siguiente espera hasta que el anterior se aparte. Cambia temporalmente `ShopperFraction` a 1 para aumentar las visitas; no todos los peatones tienen que entrar en cada vuelta.
4. **Puerta:** acércate con la cámara y observa a los NPC. Las hojas se abren por proximidad del peatón y se cierran después. La cámara no activa la puerta.
5. **Población:** aléjate más de 180 m con la cámara. Los peatones deben volver a sus pools; al regresar a menos de 120 m se reutilizan. Los tres dependientes de esta escena pequeña son fijos y se cuentan aparte del presupuesto de peatones.
6. **Recuperación:** durante Play, desactiva un cliente que esté en fila. Su ticket debe liberarse. Un destino que no pueda alcanzarse debe finalizar la rutina y devolver el NPC al pool, sin bloquear la fila.
7. **Arte y rendimiento:** revisa vidrio, colores, bolsas, escalas y Console. Usa el Profiler con la cámara a altura de persona. El mapa completo sigue siendo una fuente de diseño grande: necesita integración de sectores, LOD y streaming antes de valorar una sesión jugable de 4 km por lado.

No ejecutes esta demo como si ya fuese la ciudad sincronizada de una partida online. Las pruebas con Multiplayer Play Mode corresponden a la integración de red pendiente. La autoridad está separada mediante `CityLifeAuthority` para que esa integración pueda reemplazar la autoridad local; todavía no existe una implementación de red en esta entrega.

## Arquitectura para aprender

`PedestrianRoutine` decide el estado y depende de la interfaz `IPedestrianMotor`, no de NavMesh.
`PedestrianMovement` resuelve destinos y desplazamiento; `PedestrianPresentation` controla solo animación y bolsa.
`ShopQueue` conserva el orden y las reservas; el puesto se libera al apartarse del mostrador.
`ShopActivity` expone los puntos de interés y emite el evento de compra; el dependiente lo escucha.
`CityPopulationDirector` selecciona variantes y reutiliza instancias mediante Object Pool.
`PedestrianSettings` es un ScriptableObject para ajustar la población sin editar la lógica.
Esta separación aplica State, Observer, Factory/Pool y los principios de responsabilidad única y dependencia de interfaces.

## Archivos creados o modificados

| Ruta | Contenido |
| --- | --- |
| `Ciudad_Viva_Demo_R5.blend` | Diez civiles, puertas, rutinas de revisión y cámaras. |
| `Villa_Alarma_Ciudad_Viva_R5.blend` | Mapa de 4 × 4 km con nueve interiores y 26 personajes de revisión. |
| `Civiles_Animados_R5.blend` | Diez civiles y sus 50 clips propios. |
| `Objetos_Locales_R5.blend`, `Distrito_Comercial_R5.blend` | Kit de 32 objetos y distrito estático de tres negocios. |
| `export/Props/`, `export/Characters/` | 32 FBX de objetos y diez FBX de civiles, con cinco clips por modelo. |
| `export/District_CityLife_R5.fbx` | Distrito para construir la demo local. |
| `export/Map/Villa_Alarma_Ciudad_R5.fbx` | Mapa completo estático; los NPC se importan por separado. |
| `Unity/Runtime/` | Rutinas, cola, movimiento, presentación, población, puertas, cámara y configuración. |
| `Unity/Editor/` | Importación, controladores y constructor de escena. |
| `Unity/SharedSupport~/` | Shader de viento propio R3 y su `.meta`, reutilizados si hacen falta. |
| `tests/`, `run_domain_checks.py`, `compile_unity.py` | Comprobaciones independientes y compilación contra DLL instaladas. |
| `props.py`, `mesh_tools.py`, `build_props.py` | Generación de piezas. |
| `animation.py`, `build_characters.py` | Marcha, gestos y clips propios. |
| `build_district.py`, `preview_simulation.py`, `build_live_preview.py` | Distrito y revisión de rutinas en Blender. |
| `update_city.py`, `street_residents.py` | Integración en la copia del mapa y paseantes de cada local. |
| `fbx_utils.py`, `export_assets.py`, `validate_exports.py` | Exportación y reimportación de comprobación. |
| `render_animation.py`, `encode_preview.py`, `viewport_review.py` | Renders, vídeo y captura real del viewport. |
| `settings.json`, `*_catalog.json`, `*_placements.json`, `unity_*.json`, `materials.json` | Medidas, paleta y datos para regenerar/importar. |
| `baseline/` | Fuentes propias R3/R4 y manifiestos necesarios. |
| `renders/`, `*_validation.json`, `city_update.json` | Medios y resultados de verificación. |

Además se actualizan `AGENTS.md`, la prioridad de trabajo de `TASKS.md`, `Assets/Party/Art/README.md` y `Assets/Party/docs/LICENSES.md`. La guía se copia a `Assets/Party/docs/City-Life-R5.md`. Ninguna casilla de task ni commit de cierre se modifica por estas comprobaciones.

## Comprobaciones y límites

- Las 20 comprobaciones del dominio cubren fila acotada, orden, doble registro, espera, pago, reserva hasta apartarse, cancelación, reinicio de pool, destinos rechazados, timeout y tiempo de observación desde la llegada.
- Runtime y editor se compilan con C# 9 contra las DLL de Unity 6000.3.27f2, Input System y AI Navigation instaladas. Esto comprueba tipos y firmas; no sustituye Play ni la ejecución del constructor en Unity.
- Los JSON de FBX registran las piezas reimportadas, 21 huesos y cinco clips por civil, deformación de la marcha, pesos y cierre del ciclo, puertas del distrito y dimensiones del mapa. La captura del viewport y los renders se revisan antes de entregar.
- La integración del mapa conserva por huella las geometrías ajenas a los interiores y las dos puertas previstas, incluyendo las máscaras de viento. Se retienen las zonas especiales de banco y comisaría.
- **Pendiente de Alain:** ejecutar el constructor, validar Generic/Avatar, observar NavMesh/evitación real, revisar sombras/materiales, medir rendimiento y probar en Play. **Pendiente de desarrollo:** red, Humanoid final, sistemas de atraco, tráfico y activación por sectores del mapa completo.

## Regenerar

Usa una copia de esta carpeta con Blender 4.5, Python con Pillow, FFmpeg/FFprobe en PATH y las fuentes de `baseline` incluidas. Los chequeos C# independientes usan el SDK .NET 10 instalado localmente; el juego no requiere ese SDK para ejecutarse. Adapta las rutas de DLL en `compile_unity.py` si cambias de equipo.

```powershell
blender -b -P build_props.py
blender -b -P build_characters.py
blender -b -P build_district.py
python preview_simulation.py
blender -b -P build_live_preview.py
blender -b -P fix_preview_viewport.py
blender -b -P update_city.py
blender -b -P export_assets.py
blender -b -P validate_exports.py
blender -b -P render_animation.py
python encode_preview.py
python run_domain_checks.py
python compile_unity.py
blender --factory-startup --python viewport_review.py
```

Los fotogramas intermedios y DLL de comprobación no se incluyen en el paquete. El último comando abre y cierra solo su propia instancia de Blender para capturar el viewport. No abre Unity ni ejecuta el juego.

## Procedencia

Todas las piezas y animaciones son propias, creadas con bpy a partir de nuestro elenco y ciudad. Sin modelos, texturas, clips ni sonidos descargados. Rótulos geométricos con la fuente incluida en Blender; FFmpeg es una herramienta de codificación. No se incorporó Mixamo. Revisión funcional y online pendientes; la aprobación visual anterior corresponde a vegetación R4.
