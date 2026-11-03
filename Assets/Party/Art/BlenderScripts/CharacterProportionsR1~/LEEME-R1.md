# Corrección de proporciones R1

Alain autorizó corregir el perfil de la cabeza, cuello, hombros y tiro del pantalón. Se conserva la altura de 1,65 m y la dirección estilizada; no se cambió al estilo chunky de la guía PDF.

## Cambios realizados
- Cabeza y mandíbula reconstruidas mediante anillos de quads unidos al cuello. Se conserva una única malla Body, cerrada y simétrica mediante Mirror X.
- Cuello separado de la masa facial; mentón y profundidad craneal ajustados para evitar la transición cónica de Skin.
- Hombros y mangas estrechados. Los puños continúan la manga sin separarse al cambiar la altura de la pelvis.
- Pelvis anatómica elevada, tiro del pantalón elevado y cintura alta recolocada. Se adaptaron el largo del top, el bajo de la chaqueta y los bolsillos traseros.
- Masas de pelo y posición de mechones adaptadas a la nueva cabeza. Rostro, orejas y manos siguen pendientes de modelado.

## Comparación reproducible
Se usan los mismos recortes de la lámina 02_civil_mujer.png, cámaras ortográficas y altura total para ambas versiones.
La anchura del cuello se mide al 82 % de altura, sobre cuello desnudo; al 80 % la referencia cruza el cuello de la chaqueta. La anchura de pelvis usa el intervalo central para excluir los brazos.
Las medidas de imagen describen contornos, no distancias exactas entre articulaciones.

| Medida de silueta | Diferencia antes | Diferencia R1 |
|---|---:|---:|
| Cabeza de perfil | -19.7% | -5.3% |
| Cuello frontal | +100.8% | +0.4% |
| Cuello de perfil | +54.5% | +8.1% |
| Hombros frontales | +10.4% | +3.8% |
| Hombros posteriores | +14.0% | +3.8% |
| Pelvis frontal | +2.5% | +6.8% |

Un signo positivo indica mayor anchura que la referencia; negativo, menor anchura. La pelvis frontal queda algo más ancha que antes; no todas las medidas mejoraron a la vez.

| Altura visible de entrepierna | Referencia | Antes | R1 |
|---|---:|---:|---:|
|Frente|0.745 m|0.641 m|0.728 m|
|Espalda|0.755 m|0.632 m|0.712 m|

La abertura entre piernas corresponde al pantalón y al cuerpo que queda detrás; no es una medición del fémur.

## Archivos y comprobaciones
- `character.blend`: archivo editable generado en Blender 4.5.15, escena Character_Blockout_4x.
- `build_character.py`: fuente bpy completa, con medidas y perfiles al inicio.
- `export/character.fbx`: siete objetos y 21 huesos, exportado con FBX All, -Z Forward, Y Up y Apply Transform.
- `export/roundtrip.json`: reimportación, altura, pesos, flexión y recuperación de la pose, cuerpo cerrado en quads, orígenes y referencias empacadas.
- `comparacion_frente.png`, `comparacion_perfil.png`, `comparacion_espalda.png`: referencia, antes y R1.
- `diagnostic_body/`: vistas del cuerpo sin prendas para inspeccionar anatomía de blockout.
- `viewport_front.png`: captura del viewport del Blender 5.2.3 abierto, usado solo para revisar la fuente producida en 4.5.15.
- `before_after.json`: comparación numérica con un único protocolo para ambas versiones. El promedio R1 incluye cuello y pelvis central; no debe compararse directamente con el promedio del informe antiguo que no incluía esas medidas.

## Cómo regenerar
Desde esta carpeta, con Blender 4.x:

```text
blender -b --python-exit-code 1 -P build_character.py
blender -b --python-exit-code 1 -P check_blockout_fbx.py -- .
```

La corrección manual se conserva por defecto. `--auto-fit --fit-iterations 4` habilita el ajuste automático opcional; no es necesario para reproducir esta revisión.
Body parte de Skin y subdivisión para torso/extremidades; refine_head_cage sustituye su extremo superior por la jaula de cabeza/cuello. El grafo oculto SOURCE_SkinGraph conserva la etapa Skin, no toda la cabeza refinada.
HEADS_TALL sigue siendo una guía de construcción; la forma final se ajusta por los perfiles y por las referencias, no mediante una certificación automática de la proporción de cabezas.

## Revisar en Blender y Unity
1. En el Blender abierto está cargada la escena Female_Proportions_R1, sin reemplazar escenas anteriores. Para abrir el entregable independiente, usa character.blend.
2. Compara frente, perfil y espalda con los PNG. Revisa mandíbula/cuello, ancho de hombros y altura del tiro antes de seguir con rostro y manos.
3. El rig existe para comprobar articulaciones. Al pasar a animación deben revisarse los pesos de hombros, pelo y la ropa ancha en poses extremas.
4. Después de aprobar la silueta, importa el FBX dentro de Assets/Party. En Rig selecciona Humanoid, Create From This Model, Configure y comprueba el Avatar con un clip de caminar.

El Avatar de Unity y las animaciones finales siguen pendientes. No se sustituyeron prefabs ni se marcaron tareas como aprobadas.

## Explicación para aprender
Skin sirve para obtener rápidamente un cuerpo conectado, pero puede fusionar demasiado cabeza y cuello. Los anillos permiten controlar por separado la nuca, el mentón y el cráneo sin perder quads.
El tiro alto cambia la longitud visual de las piernas sin alargar todo el personaje. Por eso se reajustaron también cintura, pelvis y prendas.
Las medidas del rig se generan con los mismos parámetros del cuerpo. Después de cambiar la geometría se recalcularon pesos y se comprobó el FBX real, conservando la responsabilidad separada de construir, medir, riggear y exportar.

## Pendiente artístico
Es una corrección del blockout. Aún faltan facciones, orejas, manos con pulgar/dedos, pelo detallado, pliegues y transiciones finas de ropa. El perfil posterior de la cabeza y los bajos del pantalón conservan diferencias medibles.
No se descargaron modelos ni texturas. Las referencias proceden de las imágenes aportadas por Alain. Unity permanece en 6000.3.27f2.
