# Blockout femenino para Blender 4.x

Generación original en bpy, probada realmente en Blender 4.5.15 LTS portable oficial.
Es una base para esculpir; no un personaje terminado ni una réplica exacta de la lámina.

## Archivos

- `build_character.py`: script completo comentado por secciones, sin dependencias Python externas a Blender.
- `character.blend`: escena editable `Character_Blockout_4x`, con referencias empacadas.
- `refs/front.png`, `side.png`, `back.png`: recortes de la lámina 02_civil_mujer.png aportada por Alain.
- `renders/`: tres vistas finales y las 2 iteraciones de esta ejecución.
- `comparison.png`: referencias junto a los renders reales, con la misma escala de imagen.
- `export/character.fbx`: siete mallas y un armature, sin luces ni cámaras.
- `verification.md` y `report.json`: diferencias por vista, parámetros y pesos.
- `export/roundtrip.json`: reimportación del FBX y comprobaciones del archivo editable.
- `check_blockout_fbx.py`: comprobación reproducible del FBX y .blend.
- `logs/`: ejecución headless y versión/checksum del runtime utilizado.

## Ejecutar

Abre una terminal en esta carpeta y ejecuta:

```text
blender -b -P build_character.py
```

Para propagar errores al código de salida del proceso, como en la verificación entregada:

```text
blender -b --python-exit-code 1 -P build_character.py
```

Opciones:

```text
blender -b -P build_character.py -- --fit-iterations 4
blender -b -P build_character.py -- --no-fit
blender -b --python-exit-code 1 -P check_blockout_fbx.py -- .
```

El Blender 4.5.15 utilizado está en:
`C:/Users/Alain/Documents/Codex/2026-10-31/pued/work/blender45-portable/blender-4.5.15-windows-x64/blender.exe`.
En PowerShell puedes invocarlo con `& 'ruta/al/blender.exe' -b -P build_character.py`.
No se cambió la instalación de Blender 5 ni la versión de Unity del proyecto.

## Ajustar el modelo

La sección 1 contiene medidas en metros, radios, alturas, colores, perfiles de prendas y posiciones secundarias.
`BODY_GUIDES`, `JACKET_GUIDES`, `PANTS_GUIDES`, `SHOE_PROFILE`, `HAIR_GUIDES` y los contornos de bolsillo/cuello permiten ajustar detalles sin buscar coordenadas en las funciones.
Los multiplicadores usados en las funciones son proporciones de forma o resolución de topología.
`HEIGHT` normaliza el conjunto completo, incluido el moño, a 1,65 m con los pies en Z=0.
`HEAD_HEIGHT = HEIGHT / HEADS_TALL` fija la guía de aproximadamente 6,5 cabezas; la normalización global y el suavizado Skin modifican ligeramente la medida final de la cabeza.

El ajuste automático modifica anchuras, profundidad y descenso de brazos; la salida final usa 58.4 grados desde la horizontal para acercarse a la hoja.
Para mantener exactamente los 45 grados iniciales usa `--no-fit`.
Las referencias funcionan mejor con fondo gris claro y personaje de color. Los umbrales de segmentación se encuentran al inicio.
Se mide el contorno, no landmarks anatómicos ni la calidad de una cara.

## Resultado verificado

- Altura reimportada: 1.650000 m.
- Siete objetos: Body, Jacket, Top, Pants, Shoes, Hair y Earrings.
- 21 huesos humanoides; pesos de todos los vértices comprobados tras exportar y reimportar.
- Body continuo, cerrado, con 3288 caras, todas en quads, y Mirror X activo.
- Total de caras en quads: 9204/9486; algunos remates y bolsillos usan triángulos o n-gons.
- Orígenes en cero, escalas unitarias, rotaciones aplicadas y volumen firmado positivo del cuerpo.
- Grafo oculto SOURCE_SkinGraph con Mirror, Skin y Subdivision para estudiar la construcción.
- Error medio de anchuras: 8.9%; IoU media: 0.743.
- Criterio declarado: media <= 18 %, máximo de anchuras <= 25 %, IoU >= 0,60 y sin recorte horizontal.
- Coincidencia razonable según ese criterio: True.
- Prueba de flexión y recuperación de la pose importada superada; no sustituye una revisión animada completa.

Bone Heat no resolvió todos los paneles desconectados. Reparación automática por interpolación de pesos del cuerpo: Jacket: 20.
El informe distingue pesos originales y reparados. No se presentan como pesos pintados y revisados a mano.
La ropa, el pelo y el calzado tienen algunos bordes abiertos intencionales; son superficies de blockout, no todas piezas estancas.

## Fidelidad y escultura pendiente

La paleta, las piezas de ropa separadas, la cintura alta, el ancho general del pantalón y el moño siguen la referencia.
Quedan diferencias medibles en la tabla de verification.md: cabeza de perfil más estrecha, mangas/hombros más anchos y bajos algo estrechos.
La abertura entre piernas está más baja; el pantalón hace que las piernas se lean más cortas. Corregir el tiro y la transición a la cadera será parte del refinamiento de silueta.
El rostro es un volumen liso. Faltan facciones, orejas y manos/dedos definidos; el pelo representa masas y dos mechones, no rizos esculpidos.
Faltan pliegues, costuras finas, grosor final de cuello/bordes y detalles de zapatillas.
Revisar intersecciones de ropa, hombros, caderas y puños en poses extremas antes de animar para producción.

## Abrir en Blender y probar en Unity

1. Abre character.blend. La escena del personaje queda activa y el viewport frontal encuadrado. El rig aparece delante para inspeccionarlo.
2. En Outliner puedes ocultar References_Only para ver el blockout sin imágenes y mostrar SOURCE_SkinGraph para editar el grafo.
3. Para comprobar el rig, selecciona Armature, entra en Pose Mode y prueba codos y rodillas. Revisa especialmente la ropa de pierna ancha.
4. Después de la revisión visual, copia export/character.fbx a una carpeta de modelos dentro de Assets/Party del proyecto Unity.
5. En Rig elige Humanoid, Create From This Model y Apply; abre Configure, revisa el mapa y usa Enforce T-Pose si es necesario.
6. Comprueba la altura de 1,65 m junto a un cubo de 1 m, asigna materiales URP/Lit con los hex del script y prueba un clip de caminar.

El Avatar de Unity todavía no está verificado. No se crearon animaciones ni se sustituyeron los prefabs existentes.
El FBX usa FBX All, -Z Forward, Y Up, Apply Transform, sin leaf bones ni clips.

## Explicación para aprender

Skin convierte un grafo de puntos y radios en una superficie conectada. Subdivision suaviza la base; Mirror conserva simetría.
La chaqueta y el top parten de esa superficie, mientras el pantalón y las zapatillas usan anillos de quads para controlar el volumen.
El armature se alinea con las mismas medidas del cuerpo; Bone Heat calcula pesos y Data Transfer repara únicamente vértices sin peso de otras piezas.
Separar construcción, comparación, rig y exportación permite corregir una etapa sin mezclar sus responsabilidades.

## Referencias técnicas y procedencia

- Geometría y materiales propios; no se descargaron modelos ni texturas.
- Blender 4.5: https://docs.blender.org/api/4.5/bpy.types.SkinModifier.html
- Exportador FBX: https://docs.blender.org/api/4.5/bpy.ops.export_scene.html
- Transferencia: https://docs.blender.org/api/4.5/bpy.types.DataTransferModifier.html
- Portable oficial: https://download.blender.org/release/Blender4.5/blender-4.5.15-windows-x64.zip
- SHA-256 verificado: 52dd02fd74877fa08e74b67d7854cf32468a232c02aaa19b6844c91285574f8d

## Guía PDF recibida al final del trabajo

La guía adicional propone otro estilo: 1,40 m, 3,5 cabezas, Shade Flat, 1.500-4.000 triángulos y Mixamo.
No se aplicó ese cambio al modelo de esta entrega: la petición explícita sigue siendo una mujer de 1,65 m, 6,5 cabezas, quads y rig generado con bpy.
El flujo de trabajo de referencias, variables, revisión y exportación es compatible con ambas direcciones.
Alain confirmó mantener la mujer de 1,65 m y 6,5 cabezas; la guía se usa como apoyo de flujo de trabajo, no para cambiar proporciones. No se crearon Don Sigilo ni variantes.
