# Arte de Alarma

### Revisión vigente de ciudad: manos y compras R6

Fuentes: `BlenderScripts/CityLifeR6~`; guía: `../docs/City-Life-R6.md`. Corrección de manos, tráfico y tareas de compra con filas/dependientes. Se conserva el mapa 4 × 4 km y el arte previo. Demo local Unity y revisión Blender horneada, pendientes de Play y aprobación de Alain.

### Revisión anterior de ciudad: vida e interiores R5

Fuentes en `BlenderScripts/CityLifeR5~`; guía `../docs/City-Life-R5.md`. 32 piezas detalladas, nueve interiores, diez civiles con cinco clips propios y mapa de 4 × 4 km con 26 personajes de revisión. Incluye demo animada en Blender y constructor de demo local Unity con rutinas y pools. Runtime/editor compilados contra DLL instaladas y FBX reimportados; Play, Generic/Avatar, navegación real y red pendientes de prueba/integración. Alain aprobó la dirección visual R4; la revisión R5 sigue pendiente. Mantener Unity 6000.3.27f2 y las versiones anteriores.

### Vegetación conservada: jardineras y pasto R4

Fuentes y ciudad con arbustos de hojas individuales y pasto detallado en `BlenderScripts/PlantersGrassR4~`; guía `../docs/Planters-Grass-R4.md`. Conserva el arbolado R3 y las bases de macetas, añade bordes y viento suave. Captura y vídeo revisados en Blender; compilación/prueba en Unity y aprobación visual de Alain pendientes. Mantener 4 × 4 km, Unity 6000.3.27f2 y elenco R3.

### Arbolado conservado: árboles y viento R3

La revisión de árboles y hojas en movimiento está en `BlenderScripts/TreesWindR3~`. Consultar `../docs/Trees-Wind-R3.md`. Incluye seis especies, viento Geometry Nodes, copia del mapa, FBX y archivos URP preparados. El movimiento está comprobado en Blender; faltan compilación y prueba en Unity. Mantener 4 × 4 km, Unity 6000.3.27f2 y el elenco R3. Arquitectura R2 conservada; aprobación visual de Alain pendiente.

### Base de arquitectura: ciudad moderna R2

La revisión actual del diseño de ciudad está en `BlenderScripts/Map4KmModernR2~`. Consultar `../docs/Map4Km-Modern-R2.md`. Alain pidió mejorar la sencillez de V1 y confirmó terminar primero el diseño. Mantener 4 × 4 km, personajes R3 y Unity 6000.3.27f2. La revisión R2 sigue pendiente de su aprobación visual e integración funcional.


## Guía actual — mapa y elenco low poly

Alain aprobó la dirección de personajes geométricos divertidos; la versión actual del elenco está en `BlenderScripts/CastLegsR3~`. El mapa de 4 × 4 km se entrega en `BlenderScripts/Map4Km~`, con fuentes, FBX completo, 64 sectores, 55 piezas de kit y capturas. Consultar `../docs/Map4Km.md`. Todo usa metros y colores planos cálidos. Mantener Unity 6000.3.27f2. La ciudad sigue pendiente de aprobación visual e integración funcional. Las secciones ReferenceV2 que siguen documentan una versión anterior rechazada; no son la guía vigente de personajes.


Unity 6000.3.27f2 URP; Blender 5.2.3 LTS. Todos los modelos se construyen con scripts bpy mediante MCP. No se usan bibliotecas de modelos ni texturas descargadas.

## Estilo y revisión vigente

Ciudad colorida de tonos cálidos, materiales planos compartidos, sin texturas pintadas. Alain rechazó la simplicidad del primer lote de personajes y entregó 14 referencias de mayor detalle. La revisión `ReferenceV2` usa anatomía suave, rasgos faciales y prendas con detalles geométricos. Sus comparaciones y aprobación visual siguen pendientes; no se considera terminado el acabado ni el rig.

## Escala y exportación

1 unidad Blender = 1 metro. Blender Z arriba y frente -Y; FBX exporta Y arriba, eje de exportación -Z. No cambiar la escala del proyecto Unity. El cubo `Validation/ConnectionCube_1m.fbx` se verificó a 1 m en los tres ejes en Unity.

`BlenderScripts/alarmart.py:export_asset` exporta los modelos del primer lote. `BlenderScripts/npc_v2.py:export` exporta los nuevos personajes al origen y conserva las asignaciones de materiales por objeto. Conserva nombres en inglés, raíces identificables y piezas móviles separadas. Los FBX actuales son estáticos; el exportador de esqueletos y clips se añadirá tras recibir el rig real.

## Carpetas

- `BlenderSources~`: archivos .blend editables. El sufijo ~ evita la conversión automática de Unity; Unity importa los FBX explícitos.
- `BlenderScripts`: recetas propias y catálogos. Antes de regenerar, trabajar en una copia de la biblioteca; las funciones rechazan nombres existentes.
- `References~`: láminas entregadas por Alain, solo como referencia de modelado.
- `Characters/ReferenceV2`: 14 personajes y cuatro cuerpos de preparación A/T. El primer lote se conserva en `Characters`.
- `City`, `Vehicles`, `Props`, `Weapons`: primer lote de diseño estático, pendiente de revisión visual.
- `Materials`: paletas JSON y materiales URP. `Previews~`: capturas del primer lote.
- `../Prefabs/Art`: prefabs visuales generados por el constructor de editor, sin lógica de juego.

## Uso en Blender

Abrir `BlenderSources~/Alarma_Characters_ReferenceV2.blend` para la galería nueva o `Alarma_ArtLibrary.blend` para el primer lote completo. La escena nueva se llama `Alarma_Characters_ReferenceV2`. Las raíces `NPC2_01_...` a `NPC2_14_...` contienen sus piezas. Las bases de preparación están ocultas en la galería.

Para modificar por script, añadir `BlenderScripts` a sys.path, importar `npc_v2`, activar la escena y editar una copia. `npc_v2.frame(root, 'front')` aísla un personaje; `npc_v2.gallery()` restablece la galería. `npc_v2.export(root)` conserva el origen del FBX; `npc_v2.save()` escribe la biblioteca propia. Las rutas de proyecto están declaradas al inicio del módulo para trasladarlo a otro equipo.

## Pendiente antes de animación

Aprobar el acabado y corregir los diseños. Alain realiza la subida/descarga de los dos cuerpos en T con Mixamo; después se revisarán el rig, la transferencia de pesos, Humanoid y los clips. Consultar `../docs/GUIA-MIXAMO-V2.md`. No se sustituyen rigs reales por marcadores ni se declara animado un prefab estático.
