# Toñito Músculo — torso de gimnasio R1

Corrección solicitada por Alain el 2026-11-01: más anchura desde la cintura hacia el pecho y mejor encaje de los brazos, manteniendo el estilo low poly divertido.

## Cambios

- Torso en V, caja torácica más ancha y profunda; pecho y espalda con mayor volumen.
- Mayor separación de hombros; clavículas, brazos y manos recalculados junto con los huesos.
- Bíceps y antebrazos menos exagerados, con transición progresiva hacia codos y muñecas.
- Prenda superior continua, sin los bloques de tirantes anteriores; dibujo MAMA colocado delante del nuevo pecho.
- Cuello algo más robusto y mazo desplazado con la mano.
- Altura de 1,88 m y estilo geométrico conservados.

El ancho máximo canónico del torso vestido pasa de 0,368 a 0,464 m antes de aplicar la anchura global: aproximadamente un 26 % más. El radio máximo del bíceps pasa de 0,097 a 0,068 m: aproximadamente un 30 % menos. Estas son medidas del generador, no perímetros anatómicos.

## Archivos creados

- `Alarma_Tonito_Gym_R1.blend`: elenco integrado con Toñito corregido. Escena actual `Cast_Player04_Muscle_Gym_R1`; `Cast_Gallery` muestra los 18 personajes. `BeforeGym_Player04_Muscle` conserva la versión anterior.
- `fbx/Player04_Muscle.fbx`: únicamente Toñito corregido, rig propio de 21 huesos y siete mallas; 3.878 triángulos en total.
- `renders/Player04_Muscle/`: frente, perfil, espalda, rostro y tres cuartos. `renders/comparacion.png`: antes/después. `renders/gallery.png`: galería actualizada.
- `viewport_gym_r1.png`: captura revisada del viewport conectado.
- `pose_checks/Player04_Muscle.png`: flexión del FBX reimportado.
- `build_gym_revision.py`: parámetros y construcción de esta corrección. Importa los módulos propios `build_cast.py` y `character_primitives.py`.
- `baseline/`: nuestro elenco anterior y la base femenina aprobada, necesarios para regenerar sin descargas.
- `gym_measures.json`, `manifest.json`, `validation.json`, `preservation.json`, logs y scripts de comprobación.
- `SHA256.json`: integridad de la entrega.

## Pruebas realizadas

Generación y reimportación con Blender 4.5.15 LTS, en modo headless. Un rig de 21 huesos, sin luces/cámaras en el FBX; altura y apoyo correctos con tolerancia de 3 mm; cero vértices sin pesos; pesos normalizados. Giro de cabeza, flexión de brazo/pierna y recuperación de pose inicial comprobados. Captura del viewport y renders frontal, lateral, posterior y de pose revisados.

Se compararon las coordenadas, topología, matrices y colores de las mallas de los otros 17 actores del archivo integrado: permanecen iguales al elenco anterior. La galería referencia la nueva colección de Toñito.

## Revisar y probar

1. Abrir el `.blend` o elegir `Cast_Player04_Muscle_Gym_R1` en Blender ya abierto. Para ver todo el elenco, cambiar a `Cast_Gallery`.
2. Comparar pecho, espalda, hombros y brazos con `renders/comparacion.png`; girar el viewport para revisar las axilas.
3. Mostrar el Armature, entrar en Pose Mode y flexionar hombro/codo. Volver a la pose inicial antes de guardar cambios propios.

## Pasos para Unity después de la revisión visual

1. Mantener Unity **6000.3.27f2**. Copiar este FBX a la carpeta de modelos elegida dentro de `Assets/Party`; sustituir únicamente el Toñito que se decida usar.
2. Configurar Rig = Humanoid, Create From This Model, Apply y Configure. Validar huesos y pose; revisar escala y orientación.
3. Probar posteriormente los clips con el Avatar validado, comprobando hombros, codos y cintura. No se generaron animaciones ni Animator Controllers en esta corrección.

La carpeta `TonitoGymR1~` está excluida de la importación automática de Unity. No se modificaron prefabs ni se abrió el editor. Avatar Humanoid, clips y ausencia de penetraciones en todas las poses siguen pendientes; la prueba básica de flexión no sustituye esa revisión.

## Regenerar

Desde la carpeta de esta entrega, usando Blender 4.5.x:

```powershell
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P build_gym_revision.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P validate_cast.py
& 'C:/ruta/a/blender.exe' -b --python-exit-code 1 -P verify_cast_preserved.py
```

Las medidas están al principio de `build_gym_revision.py`. El generador base es una dependencia importada; no ejecutar `build_cast.py` para regenerar esta revisión, porque reconstruiría el elenco anterior.

## Explicación para aprender

Un brazo grande necesita una caja torácica y hombros que sostengan su volumen. Por eso se ensancha progresivamente el torso desde la cintura y se desplazan los huesos del hombro junto con la geometría. Los pesos de los brazos se asignan por anillos para repartir el movimiento en hombro, bíceps, codo y antebrazo. La camiseta usa pesos de columna y pecho para evitar que un bíceps cercano arrastre todo el torso. Construcción, exportación y validación conservan responsabilidades separadas; no se añadió código C# ni lógica de juego.

## Procedencia

Geometría, materiales planos y rig propios de bpy; reutilización de nuestras bases aprobadas. Sin modelos ni texturas descargados ni recursos de Mixamo. La tipografía Arial de la comparación solo aparece en la hoja de revisión, no se exporta al FBX.
