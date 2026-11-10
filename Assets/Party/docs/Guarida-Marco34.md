# B1 — marco de la guarida, revisión 34

Estado: modelo instalado, pendiente de aprobación visual y Play por Alain. No cierra B1. Unity 6000.3.27f2.

La abertura de 2 m tenía hojas de 1,78 m de ancho exterior y molduras superficiales. Se añadieron jambas de 24 cm de profundidad y un dintel continuo. Las hojas se ajustaron sin mover las bisagras ni los puntos de contacto. Quedan juntas de 25 mm a los lados y 15 mm arriba para permitir el giro en ambos sentidos. Las jambas llevan colisión mediante la preparación existente de City25Kit.

## Archivos creados o modificados

- `Assets/Party/Art/BlenderScripts/build_hideout.py`: función `entrance_door`, dimensiones y marco.
- `Assets/Party/Art/City/Shops/Local_Escondite.fbx`: modelo activo. Su `.meta` se conserva intacto.
- `Assets/Party/Art/BlenderSources~/Alarma_Escondite.blend`: fuente editable de la guarida.
- `Assets/Party/Art/BlenderScripts/HideoutB1Fix~/DoorFrame34~/`: receta de ajuste aislado, comprobador de reimportación, instalador, tres capturas y resultados JSON.
- Este documento y notas de seguimiento en `TASKS.md` y `AGENTS.md`.

## Comprobaciones realizadas

- 342 posiciones de las cajas de las hojas, de −85° a +85° cada una, sin intersección con jambas, dintel y paredes frontales en Blender.
- Reimportación de ambos FBX: 412 mallas ajenas al acceso coinciden en posiciones de vértices redondeadas a 1 mm, número de caras y nombres de materiales.
- Capturas del viewport revisadas, con puerta cerrada y abierta. Son vistas de Blender.
- SHA-256 de los archivos instalados igual al de los preparados. Copias anteriores en `Library/Alarma/DoorFrame34/Anterior`.
- No se abrió Unity ni se ejecutó PhysX o Play. No cambió código C#.

## Pasos para el editor y prueba

1. Abre Unity y espera a que termine de importar.
2. Pulsa **Alarma > Crear y probar juego**. La huella del FBX cambia y provoca la preparación de la escena actualizada.
3. En la guarida, mira la puerta cerrada desde dentro y desde el patio. Comprueba laterales y borde superior.
4. Abre con **E**, cruza, deja cerrar y repite desde el otro lado. Comprueba que no se atasque.
5. Confirma el resultado antes de cerrar B1 o hacer un commit de esta corrección.

## Explicación para aprender

El marco es fijo y cada hoja sigue siendo hija de su bisagra. Así la animación mueve solo la puerta. La función `entrance_door` concentra la construcción del acceso, aplicando responsabilidad única. El constructor existente detecta el nuevo contenido del FBX y prepara sus colisiones. La prueba geométrica reduce el riesgo de roces, pero la prueba final de movimiento corresponde a Unity.
