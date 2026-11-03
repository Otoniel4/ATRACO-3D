# Estudio de estructura femenina

Se rehizo una sola base para responder a la corrección de Alain: mejorar anatomía y articulaciones antes del detalle facial. No se considera terminado el personaje de chaqueta denim. La V2 permanece rechazada.

## Lo que contiene esta entrega

- Una superficie continua de cuerpo, pelvis, brazos, piernas, manos y pies. No usa las prendas ni el cuerpo de la V2.
- Jaula de 755 vértices y 759 caras, 728 cuadriláteros; subdivisión editable para evaluar la silueta.
- Esqueleto de diagnóstico con 29 huesos y pesos normalizados. Los dedos tienen articulación básica; no es el rig final de manos.
- Prueba de flexión en los fotogramas 1 (reposo), 30 (codo y rodilla) y 60 (reposo).
- [Vista de estructura](Revision-estructura.png), [frente](Base-front.png), [perfil](Base-side.png), [esqueleto](Esqueleto.png) y [flexión](Prueba-articulaciones.png).
- [Archivo Blender editable](Base-femenina-estudio.blend).

La base mantiene cabeza y rasgos simplificados para centrar la revisión en el cuerpo. Todavía hay que ajustar la silueta a la mujer de la referencia 02, resolver manos y pies con mayor detalle y construir su vestuario real. Los controles de geometría no certifican parecido ni calidad artística.

## Comprobaciones realizadas

La jaula no tiene aristas no manifold ni vértices sueltos. Todos los vértices tienen pesos y la suma es 1 con error máximo inferior a 0.000001. Se revisaron las capturas de reposo y flexión. Los datos se guardaron en `Geometry-and-weights.json` y `Deformation-check.json`.

## Abrir y probar en Blender

1. Abre `Base-femenina-estudio.blend`. La escena es `FemaleBody_AnatomyStudy`.
2. En el fotograma 1, revisa frente, perfil y espalda. La referencia original sigue en `Assets/Party/Art/References~/NPC_V2/02_civil_mujer.png`.
3. Selecciona `FemaleStudy_DiagnosticRig` y activa Pose Mode para ver los huesos.
4. Ve al fotograma 30 para revisar el codo derecho y la rodilla izquierda; vuelve al 60 para comprobar el retorno.
5. Modifica la jaula de `FemaleBody_Study` en Edit Mode. Conserva el orden de modificadores: Armature y después Subdivision.

## Fuentes y estado del proyecto

`Assets/Party/Art/BlenderScripts/female_body_study.py` construye la jaula, el esqueleto y los pesos. `female_body_joint_test.py` guarda la prueba de articulaciones. La biblioteca fuente está en `Assets/Party/Art/BlenderSources~/FemaleBody_AnatomyStudy.blend`.

No se exportó este estudio a Unity ni se crearon prefabs. Se mantiene Unity 6000.3.27f2. El diagnóstico no sustituye el auto-rig de Mixamo acordado para los modelos finales ni cierra las tareas de Humanoid o animación. No contiene los 19 clips del juego.

## Explicación para aprender

La topología es la forma de conectar las caras del cuerpo. Los bucles cerca de codos y rodillas permiten repartir una flexión. Los huesos indican el movimiento y los pesos deciden cuánto sigue cada vértice a cada hueso. Probar una pose permite detectar fallos antes de añadir ropa. La forma anatómica y la deformación se deben revisar por separado; una malla cerrada por sí sola no garantiza un buen personaje.
