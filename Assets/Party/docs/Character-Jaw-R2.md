# Mandíbula R2 - 2026-11-01

Corrección localizada del blockout femenino R1, autorizada por Alain para revisar y arreglar la mandíbula.

## Cambios

- Mentón con menor proyección y contorno inferior más redondeado.
- Parte baja de la cara afinada y transición hacia la nuca suavizada, evitando la cuña del perfil anterior.
- Curvas de sección interpoladas sin sobrepasar sus guías, con más anillos verticales para suavizar el contorno y el sombreado. Se conserva la resolución angular de 18 vértices de R1.
- Se conserva el óvalo general de la cara y se reduce suavemente la proyección del mentón. El cuello inferior conserva su forma para no desplazar las prendas.

La cara sigue siendo un volumen de blockout sin facciones. La aprobación visual de la mandíbula y la validación del Avatar en Unity siguen pendientes.

## Comprobado

- Generación headless en Blender 4.5.15: `headless.log`.
- Body: 3911 caras, todas en quads, cerrado, normales recalculadas y volumen positivo.
- Sin caras de área nula ni aristas de longitud nula; ver `jaw_validation.json`.
- Se compararon las coordenadas con R1: cuerpo por debajo de la unión de cabeza/cuello y todas las prendas, pelo, zapatos y aros sin desplazamientos mayores de 0,000001 m.
- FBX reimportado: siete mallas, 21 huesos, 1,65 m, sin vértices sin peso. Prueba básica de flexión y retorno a la pose importada superada.
- Revisión y captura de viewport en el Blender 5.2.3 conectado: escena `Female_Jaw_R2`. La escena R1 se conserva.

## Archivos

- `character.blend`: modelo editable, escena `Character_Blockout_4x`.
- `build_character.py`: generador completo; los ajustes están en HEAD_RING_PROFILE y las variables JAW_* al inicio.
- `export/character.fbx`: modelo exportado para revisar en Unity; `export/roundtrip.json` contiene las comprobaciones.
- `mandibula_antes_despues.png`: primeros planos frontal y lateral de R1/R2.
- `jaw_closeups/`: frente, perfil y tres cuartos actuales.
- `baseline/`: archivo R1 y primeros planos para repetir la comparación.
- `renders/`: vistas completas, manteniendo el encuadre de las referencias.
- `viewport_jaw_front.png`: captura de revisión en Blender abierto.

## Regenerar y verificar

Desde esta carpeta, con Blender 4.x:

```text
blender -b --python-exit-code 1 -P build_character.py
blender -b --python-exit-code 1 -P check_blockout_fbx.py -- .
blender -b --python-exit-code 1 -P validate_jaw_r2.py -- .
blender -b --python-exit-code 1 -P render_jaw_closeups.py -- .
```

## Revisión en el editor

1. En el Blender abierto selecciona `Female_Jaw_R2`, o abre `character.blend` para trabajar en el archivo independiente.
2. Compara frente, perfil y tres cuartos; revisa el mentón y el borde que conecta con el cuello. El archivo R1 se conserva en baseline.
3. Después de aprobar la silueta, el FBX puede importarse dentro de Assets/Party y comprobarse con Rig = Humanoid, Configure y una animación de prueba. Esa validación dentro de Unity no se realizó en esta revisión.

## Explicación para aprender

La forma de una mandíbula depende tanto de su ancho como de cuánto sobresale el mentón y cómo asciende el borde hacia la nuca. Se controlaron esas medidas por secciones.
Los anillos adicionales redondean la transición sin suavizar todo el cuerpo. La comparación de coordenadas comprueba que el ajuste se mantuvo localizado.
Construcción, exportación y validación conservan responsabilidades separadas. No se añadieron texturas, modelos externos ni animaciones.
