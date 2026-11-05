# Arte vigente y respaldo — 2026-11-04

La copia vigente es la ciudad de 2 × 2 km, Ciudad 3.0 B1, con elenco modular Cast y escondite enterable. Los once `.blend` fuente se respaldan: diez directamente y Villa_Alarma_R9_Ligera desde un ZIP íntegro fragmentado por el límite de GitHub. Esa fuente sigue alimentando el exportador del kit actual; no es un mapa activo alternativo.

Ver [respaldo y limpieza](../docs/RESPALDO-Y-LIMPIEZA.md) y el README de la raíz para restaurar el proyecto. La escena vigente y sus dependencias también están en Git. Se retiraron el primer kit sustituido, el mapa de 6 × 6 km, Atraco.unity y capturas rechazadas. Se conservan los props, armas, vehículos y tres interiores únicos útiles para continuar. Las afirmaciones históricas sobre otro equipo, pérdida de binarios y ciudades anteriores no describen el estado actual; quedan como contexto en Git y en los documentos de cada revisión.

## Fuentes y recetas actuales

- `BlenderScripts/City25~`: plano, redes, suelo y kits de calle/barrios.
- `BlenderSources~/Villa_Alarma_R9_Ligera.blend.zip.part*`: fuente exacta de edificios, mobiliario y vegetación usados por `City25~/export_kit.py`; restaurar antes de regenerar ese kit.
- `BlenderSources~/Alarma_ArtLibrary.blend`: biblioteca propia que aún contiene props y diseños útiles; no abrir sus escenas históricas como mapa vigente.
- `BlenderSources~/Alarma_StreetKit.blend`, `Alarma_DistrictKit.blend`, `Alarma_Shops.blend`, `Alarma_Escondite.blend`, `Alarma_Vehicles.blend`: modelos actuales editables.
- `BlenderScripts/ModularCast~/ModularCast.blend`: elenco actual. Los dos maestros originales CC0 están en `ThirdParty~/Quaternius_Modular`; ver `../docs/LICENSES.md`.
- `BlenderSources~/ConnectionTest.blend`: fuente de la comprobación de escala.

1 unidad = 1 metro; low poly con colores planos; Unity 6000.3.27f2. Las fuentes se conservan sin modificar geometría, pesos, huesos ni animaciones. Blender/MCP y las fuentes tipográficas que usa el generador del plano deben instalarse en el otro equipo si se desea regenerar el arte. Los FBX y la escena guardada permiten revisar el juego sin regenerarlo.
