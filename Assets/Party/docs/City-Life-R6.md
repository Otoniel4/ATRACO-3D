# Alarma: manos, circulación y compras R6

Revisión solicitada por Alain el 2 de noviembre de 2026. Corrige la demostración R5 que podía bloquear peatones y mostraba manos demasiado cortas. Mantiene Unity **6000.3.27f2**, el estilo low poly y el mapa de **4.000 × 4.000 m**. Las versiones anteriores se conservan.

## Cambios

- **18 personajes, 36 manos:** palmas, cuatro dedos y pulgar en ambas manos. Treinta huesos de dedos añadidos por rig, 51 huesos totales. Se conservan las proporciones corporales y correcciones de piernas R3. Diez civiles se usan en la demo; guardias, policías y jugadores también reciben las manos nuevas en los archivos de arte.
- **Circulación cooperativa:** grafo peatonal sobre NavMesh, destinos reservados, prohibición de intercambiar posiciones de frente y herencia de prioridad para apartarse. El desplazamiento usa pasos de 0,70 m interpolados; su trazado resulta algo angular. La animación de caminar depende del movimiento real. El sistema sustituye la simple regla R5 de detenerse ante otro NPC.
- **Tres locales:** minimarket, joyería y restaurante. Tres puestos de selección por tienda; aforo de tres compradores para evitar saturar los pasillos. Tres dependientes fijos y hasta 24 peatones desde pools.
- **Compra completa:** reservar existencias, entrar, elegir, tomar un producto con la mano, llevarlo, formar fila FIFO, colocarlo sobre la cinta, escanearlo, ofrecer dinero, cobrar, emitir recibo, recoger la bolsa y despejar la caja. El siguiente cliente espera hasta que el anterior se aparta.
- **Caja e inventario:** precios y tiempos configurables, saldo ambiental del cliente, existencias y recaudación por local. Cada cobro genera un recibo único; repetir la orden no vuelve a descontar dinero. Cancelar una compra pendiente libera producto, puesto y turno. Esta economía no modifica el dinero de banda.
- **Contacto de manos:** flexión de dedos y corrección del brazo mediante CCD sin escalar los huesos. El producto recorre estante, mano, cinta, dependiente y bolsa. Los agarres son de prototipo; requieren revisión visual en Play. La distancia máxima medida entre el agarre y su punto ideal es de 10,3 cm en la revisión horneada; los productos transportados sí siguen el agarre. El contacto fino se debe refinar en los clips finales.
- **Interiores:** se libera una vitrina que bloqueaba el acceso a caja de la joyería y se añaden tres expositores de comida para llevar. Se preservan los otros edificios, vegetación y máscaras de viento.

## Archivos principales

Los archivos de entrega se encuentran en `Assets/Party/Art/BlenderScripts/CityLifeR6~` y en la copia de `outputs/Alarma-Ciudad-Compras-R6`.

| Archivo o carpeta | Contenido |
| --- | --- |
| `Elenco_Manos_R6.blend` | 18 personajes con manos nuevas en pose de referencia |
| `Elenco_Animado_R6.blend` | Cinco clips propios por personaje y punto de agarre |
| `Productos_Compra_R6.blend` | Cartón de jugo, caja de joya, comida, billete ambiental y recibo |
| `Distrito_Comercial_R6.blend` | Tres negocios e interiores para la demo |
| `Ciudad_Compras_R6.blend` | Revisión Blender horneada de 90 segundos, 27 personajes |
| `Villa_Alarma_Compras_R6.blend` | Mapa de 4 km con las tres zonas de compra de revisión |
| `export/Characters` | 18 FBX con cinco tomas, manos y rig |
| `export/Props` | 32 piezas R5 conservadas y cinco productos R6 |
| `export/District_CityLife_R6.fbx` | Distrito sin personajes congelados |
| `export/Map` | Mapa estático completo; se omite en el constructor de demo |
| `Unity/Runtime`, `Unity/Editor` | Copia de las fuentes instaladas, incluyendo dominio, movimiento, tareas y constructor |
| `tests` | Pruebas .NET del mismo dominio que usa Unity |
| `renders` | Manos, filas, caja, joyería y capturas de viewport |

Las fuentes activas se actualizan **dentro de las carpetas existentes** `Assets/Party/Scripts/AI/CityLifeR5` y `Assets/Party/Scripts/City/Editor/CityLifeR5`. Sus nombres históricos se conservan para mantener las referencias y evitar clases duplicadas. El menú vigente es R6. Las escenas R5 no se convierten automáticamente: genera una escena R6 nueva.

## Pasos para el editor

1. Sal de Play, activa Unity y espera a que termine la compilación e importación.
2. Ejecuta **Alarma → Ciudad → Crear demo local R6**. Crea una carpeta nueva `Assets/Party/Generated/CityLifeR6_<fecha>`; no sobrescribe escenas existentes. La preparación de modelos puede tardar.
3. Abre **solamente** `Scenes/CityLife_R6.unity` dentro de esa carpeta. El constructor la añade de forma aditiva para preservar tu trabajo; abrirla sola evita cámaras o poblaciones duplicadas.
4. Pulsa **Play**. Cámara: clic derecho para mirar, WASD para desplazarte, Q/E para bajar/subir y Shift para acelerar.
5. Mantén la cámara cerca del mercado, después de la joyería y del restaurante. La población distante se devuelve a los pools. Los techos se ocultan en esta escena de inspección.

Si el constructor avisa de un puesto inaccesible, conserva el mensaje y no uses una escena parcialmente generada. El constructor comprueba NavMesh y que los seis puestos de cada tienda ocupen celdas distintas.

## Cómo probarlo

1. Observa durante **tres minutos**: peatones en ambos sentidos, entradas y salidas y compradores que se apartan al terminar. Deben llegar a sus objetivos sin intercambiar posiciones de frente ni caminar inmóviles de forma continua.
2. Sigue a un comprador: manos visibles, producto en su agarre, fila con espacio entre personas, producto sobre la cinta, gesto del dependiente, dinero, recibo y salida con bolsa. El cliente posterior no debe ocupar la caja antes de despejarse.
3. Selecciona `Routine_Minimarket`, `Routine_MallJewelry` y `Routine_Restaurant`. En `ShopActivity`, vigila **Purchase Count**, **Stock**, **Till Cents** y **Last Receipt**. Por una venta: stock baja uno y caja aumenta exactamente el precio del producto.
4. Selecciona un peatón comprador: `Visible State` recorre tareas y `Wallet Cents` baja al cobrar. Si desactivas un comprador que está en fila, el siguiente debe avanzar y el producto pendiente debe liberarse.
5. Repite una sesión con `PopulationBudget=24`, `PerDistrict=8` y `ShopperFraction=1` en el asset `PedestrianSettings`. El aforo interior limita a tres por tienda; el resto espera en la acera. Esta condición adicional debe revisarse en Play.
6. Detén Play. En `Data/Shop_<local>.asset` puedes cambiar producto, precio, existencias y saldo ambiental. Un precio superior al saldo hace que el NPC no inicie la compra. Un stock inicial de cero impide reservas y ventas.

## Verificación realizada

- Dominio C# ejecutado fuera del editor: tráfico enfrentado de 20 NPC; puerta de dos carriles con 24 NPC en sentidos opuestos; rutas desconectadas; FIFO; cancelación; sobreventa; saldo insuficiente; cobro único y liberación al volver al pool.
- Simulación de **180 segundos**, 24 peatones y tres tiendas: los 12 compradores pagan; 34 compras totales, ninguna rutina fallida. Separación mínima entre centros: **0,49497 m**. Estas medidas corresponden al simulador y sus obstáculos de revisión, no a una ejecución de física de Unity.
- Fuentes runtime y editor compiladas contra las DLL de Unity 6000.3.27f2 instaladas. Esto comprueba las APIs y sintaxis; no ejecuta NavMesh, Animator ni Play.
- Reimportación independiente de los 18 FBX: ambos conjuntos de dedos, pesos, manos cerradas topológicamente, cinco tomas por rig y flexión distinta entre reposo y agarre. Los productos y puertas se comprueban también.
- Capturas y animación de Blender inspeccionadas. La revisión Blender reproduce trazas C# horneadas; no es una captura del juego.

Consulta los JSON de validación para cifras y resultados exactos. **Play y la comprobación visual de Alain permanecen pendientes.** La escena Unity es un prototipo local; todavía no sincroniza NPC, inventario, caja ni filas por Netcode. La integración del runtime en los 16 km² completos necesita sectores y medición de rendimiento. El mapa completo de Blender ofrece la revisión visual de las tres zonas; la demo Unity usa el distrito ligero. Los rig siguen siendo Generic de estudio; no se declara validado un Avatar Humanoid final. No se cierran tareas ni se hace commit de cierre antes de tu prueba.

## Regeneración

Scripts comentados en esta carpeta. Orden: `build_hands.py`, `build_characters.py`, `prepare_district.py`, `build_district.py`, `prepare_navigation.py`, `add_food_displays.py`, `build_products.py`, pruebas `tests`, `build_preview.py`, `fix_preview_review.py`, `bake_reach.py`, `export_assets.py`, `validate_exports.py`, `update_map.py` y revisión/render. La preparación toma como base nuestra entrega propia R5, conservada como carpeta hermana; no descarga assets. Cada script bpy se ejecuta con Blender 4.5.15 mediante `blender -b -P <script>`.

## Explicación para aprender

Una máquina de estados divide la compra en tareas que empiezan cuando el personaje llega a su destino. La fila conserva el turno hasta despejar la caja. El servicio de tienda controla reservas, dinero y recibos; la presentación escucha sus eventos y mueve los objetos visibles. El planificador de tráfico reserva el siguiente espacio y permite que otro peatón ceda paso. Separar estas responsabilidades aplica el principio de responsabilidad única; las interfaces de movimiento y navegación permiten probar la lógica sin abrir Unity. El pool reutiliza personajes al salir de la zona activa.
