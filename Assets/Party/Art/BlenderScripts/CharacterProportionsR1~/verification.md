# Verificación del blockout

Blender ejecutado: 4.5.15 LTS. Altura objetivo: 1.65 m.
Error medio de proporciones: 6.1%. IoU media de silueta: 0.761.
Criterio de coincidencia razonable alcanzado: True.

Las medidas son comparaciones de silueta 2D; no demuestran por sí solas anatomía correcta.

| Vista | Cabeza | Hombros | Cadera | Pantalón/rodilla | Bajo pantalón |
|---|---:|---:|---:|---:|---:|
|front|+0.4%|+3.8%|-2.3%|-6.5%|-8.7%|
|side|-5.3%|-10.0%|+6.9%|-2.6%|-13.6%|
|back|+12.0%|+3.8%|-2.3%|-3.8%|-11.9%|

Un valor positivo indica que el render resulta más ancho que la referencia. Son anchuras de silueta en filas a altura fija; hombros incluye la manga y no mide directamente la distancia entre articulaciones. Las diferencias de pose o perspectiva de la hoja pueden impedir coincidencia simultánea de las tres vistas.

Ángulo de brazos revisado: 61.0 grados por debajo de la horizontal. Las medidas revisadas se conservan por defecto; --auto-fit permite activar el ajuste automático opcional.

| Vista | Entrepierna visible referencia/altura | Entrepierna render/altura |
|---|---:|---:|
|front|45.2%|44.1%|
|side|0.0%|0.0%|
|back|45.8%|43.1%|

La altura de la abertura entre piernas mide el pantalón, no la longitud anatómica del fémur. No puede estimarse de forma fiable de perfil con las dos piernas superpuestas.

## Preparado
Skin y Mirror X; prendas separadas; materiales planos; rig humanoide y pesos automáticos; FBX con las opciones pedidas. El grafo original queda oculto como SOURCE_SkinGraph. Body es una jaula continua en quads. Prendas, pelo y calzado contienen bordes abiertos intencionales y pequeños paneles independientes: no se presentan como volúmenes estancos.

Bone Heat se ejecuta por malla. Los vértices sin peso de accesorios o ropa se reparan automáticamente por interpolación de los pesos del cuerpo; report.json registra los recuentos exactos. Esta comprobación no equivale a una revisión artística completa de las deformaciones.

## Escultura y revisión manual pendientes
Rostro, orejas, dedos, anatomía fina, pliegues, costuras finas y rizos individuales. Revisar deformaciones con el rig antes de producir animaciones. La jerarquía es apta para configurar Humanoid; no se ha validado un Avatar dentro de Unity. Apply Transform usa bake_space_transform del exportador de Blender y debe comprobarse al importar el rig.

No se descargaron modelos ni texturas. Las referencias son recortes frontal, lateral y posterior de la lámina 02_civil_mujer.png suministrada por el usuario.
