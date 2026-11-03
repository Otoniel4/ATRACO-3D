# Ajuste de las dos bases corporales

Alain aprobó la dirección de la estructura femenina y pidió ajustar cintura y demás proporciones, y después crear una base masculina más ajustada. Se conservaron el estudio aprobado y la V2 rechazada como archivos separados. Esta entrega contiene las dos nuevas bases de trabajo, sin vestuario ni detalles faciales.

## Resultado

- Mujer: cintura más definida, pelvis algo más amplia, transición más suave hacia muslos, ajuste moderado del pecho y perfil posterior.
- Varón: silueta esbelta, hombros y pecho más anchos, pelvis más estrecha y volumen moderado en brazos y piernas. Sin musculatura exagerada.
- Ambas conservan una única superficie continua, 755 vértices de control y un rig diagnóstico independiente de 29 huesos. El masculino tiene una altura mayor, aproximadamente 1,80 m frente a 1,72 m de la base femenina.
- [Comparación frontal](Comparacion-cuerpos.png), [tres vistas](Revision-tres-vistas.png) y [flexión de ambas bases](Prueba-ambos-cuerpos.png).
- [Biblioteca editable de Blender](Bases-mujer-varon.blend).

## Comprobaciones

Se revisaron frente, perfil, espalda y una pose de flexión de cada cuerpo. Ambas jaulas mantienen cero aristas no manifold y cero vértices sin pesos. Los pesos suman 1 con error inferior a 0,000001. La pose mueve los vértices y vuelve exactamente a la posición inicial en el fotograma 60. Consultar `Validacion.json`. Estas comprobaciones técnicas no sustituyen la revisión visual de anatomía.

## Abrir y probar

1. Abre `Bases-mujer-varon.blend` y selecciona la escena `BodyBases_Refined`.
2. En el fotograma 1 se ven ambos cuerpos en reposo. Mujer a la izquierda y varón a la derecha.
3. Selecciona `FemaleBase_DiagnosticRig` o `MaleBase_DiagnosticRig` y activa Pose Mode para revisar sus articulaciones.
4. Ve al fotograma 30 para observar la flexión de codo y rodilla; vuelve al 60 para comprobar el retorno.
5. Para ajustar la superficie, edita `FemaleBase_Refined` o `MaleBase_Refined`. Mantén Armature antes de Subdivision.

## Fuentes y límites

Fuente Blender: `Assets/Party/Art/BlenderSources~/BodyBases_Refined.blend`.
Receta bpy: `Assets/Party/Art/BlenderScripts/refine_body_bases.py`.
Estudio previo conservado: `Assets/Party/Art/BlenderSources~/FemaleBody_AnatomyStudy.blend`.

No se exportaron estos ajustes a Unity. Se mantiene Unity 6000.3.27f2. El rig es de diagnóstico y todavía no es el rig final de Mixamo/Humanoid. Los clips del juego, el vestuario, las manos y los pies de mayor detalle y el acabado del rostro siguen pendientes. Las tareas 03.2–03.4 no se cierran por esta revisión de proporciones.

## Explicación para aprender

Ambos cuerpos usan la misma conectividad de caras para facilitar la reutilización futura de prendas y animaciones. La forma cambia mediante ajustes suaves de la superficie, y los huesos se reposicionan con los mismos ajustes para mantener las articulaciones alineadas. Los rigs son independientes para ensayar cada cuerpo sin deformar el otro.

## Ajuste posterior solicitado: pecho femenino

Se aumentó ligeramente el volumen frontal del pecho femenino mediante `ChestVolume_Slight` (valor 1). El masculino, cintura, pelvis y esqueleto no se modificaron. Script adicional: `Assets/Party/Art/BlenderScripts/adjust_female_chest.py`. Archivo Blender actualizado.
