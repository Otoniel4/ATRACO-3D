> RECHAZADA POR ALAIN. No usar esta versión para rig, animación ni como arte final.

# Alarma: revisión de personajes V2

Se modelaron los 14 personajes de las nuevas láminas: diez civiles, dos guardias y dos policías. Esta es una **revisión para comparar y corregir**, no una aprobación del acabado ni una entrega animada. Los modelos conservan formas y colores simplificados; todavía no igualan todos los detalles de rostro, cabello, tela y calzado de las imágenes de referencia.

La biblioteca anterior se conserva. Los nuevos personajes están en `C:\Users\Alain\Atraco3D\Assets\Party\Art\Characters\ReferenceV2`. No se descargaron modelos ni texturas ajenos. Las referencias proporcionadas por Alain se conservaron en `Assets/Party/Art/References~/NPC_V2`.

## Entregables

- [Biblioteca editable de Blender](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/Alarma-Personajes-V2.blend).
- [FBX de los 14 personajes y cuatro cuerpos de preparación](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/FBX-Personajes-V2.zip).
- [Vista conjunta](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/Resumen-14-personajes.png).
- [Inventario de mallas y triángulos](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/Inventario.csv).
- [Guía de rig y los 19 clips acordados](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/Guia-Rig-y-Animaciones.md).

Los cuatro cuerpos son hombre/mujer en A para ajustar prendas y hombre/mujer en T para el auto-rig. No representan cuatro personajes adicionales del juego.

## Comparaciones con tus referencias

Cada imagen muestra la lámina original encima y tres capturas reales de Blender debajo. Las capturas se montaron en una página; no se retocó el modelo ni se sustituyó por una imagen generada.

- [01_Civil_Male_Bomber](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/01-Comparacion.png): 152,311 triángulos.
- [02_Civil_Female_Denim](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/02-Comparacion.png): 127,987 triángulos.
- [03_Civil_Male_Turquoise](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/03-Comparacion.png): 116,973 triángulos.
- [04_Civil_Female_Lavender](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/04-Comparacion.png): 125,233 triángulos.
- [05_Civil_Male_Burgundy](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/05-Comparacion.png): 114,799 triángulos.
- [06_Civil_Female_Overalls](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/06-Comparacion.png): 121,524 triángulos.
- [07_Civil_Male_PaddedVest](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/07-Comparacion.png): 123,827 triángulos.
- [08_Civil_Female_Tracksuit](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/08-Comparacion.png): 122,741 triángulos.
- [09_Civil_Male_Plaid](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/09-Comparacion.png): 121,439 triángulos.
- [10_Civil_Female_Cardigan](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/10-Comparacion.png): 120,089 triángulos.
- [11_Security_Male](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/11-Comparacion.png): 157,823 triángulos.
- [12_Security_Female](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/12-Comparacion.png): 123,749 triángulos.
- [13_Police_Male](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/13-Comparacion.png): 123,227 triángulos.
- [14_Police_Female](C:/Users/Alain/Documents/Codex/2026-10-31/pued/outputs/Personajes-V2/14-Comparacion.png): 124,993 triángulos.

## Archivos fuente y cambios

- `Assets/Party/Art/BlenderSources~/Alarma_Characters_ReferenceV2.blend`: escena editable con los modelos, prendas y materiales.
- `Assets/Party/Art/BlenderScripts/npc_v2.py`: anatomía, prendas, detalles, ajuste de superficies, exportación y galería.
- `Assets/Party/Art/BlenderScripts/capture_npc_v2.py`: captura de tres vistas.
- `Assets/Party/Art/BlenderScripts/npc_v2_catalog.json`: inventario.
- `Assets/Party/Art/Materials/NPC2_Palette.json`: paleta propia de esta revisión.
- `Assets/Party/Scripts/Core/Editor/ArtAssetBuilder.cs`: admite varias paletas, conserva materiales existentes y genera prefabs.
- `Assets/Party/docs/GUIA-MIXAMO-V2.md`: pasos de rig y plan de clips.

## Pasos en Unity y prueba

1. Activa Unity y espera a que termine de importar. Mantén Unity **6000.3.27f2**.
2. Ejecuta **Alarma > Art > Apply Palette and Build Art Prefabs** si la importación pendiente no ejecutó el constructor.
3. En una escena temporal, arrastra un prefab de `Assets/Party/Prefabs/Art/Characters/ReferenceV2`.
4. Revisa frontal, lateral y espalda; amplía rostro, cuello, manos, ropa y calzado. Comprueba que los materiales usan URP y no aparecen rosas.
5. Ejecuta **Alarma > Validation > Validate Blender Imports**. El resultado está en `Library/Alarma/BlenderImportResults.json`; los datos del constructor están en `Library/Alarma/ArtBuildResults.json`.
6. Indica qué personajes o partes deben corregirse. La aprobación visual sigue pendiente; no se han marcado las tareas de personajes ni animación como terminadas.

Esta entrega contiene geometría estática de trabajo. No valida deformación, Humanoid, Animator, red ni rendimiento en juego. El inventario registra la densidad actual; la retopología para deformación y los LOD siguen pendientes antes de una entrega final para juego. Las mallas de piel de los outfits omiten zonas tapadas por ropa; los cuerpos base continuos se conservan aparte para transferir pesos. Las pruebas de deformación deben hacerse después de recibir los rigs.

## Explicación para aprender

El cuerpo define las proporciones; las prendas y accesorios son piezas separadas. El esqueleto y sus pesos permitirán que esas piezas se deformen juntas. Humanoid compartirá las animaciones entre hombres y mujeres. El generador separa construcción, ajuste y exportación; el constructor de prefabs se ocupa solo del trabajo de editor. Así cada pieza tiene una responsabilidad y las nuevas variantes se agregan con datos y materiales.
