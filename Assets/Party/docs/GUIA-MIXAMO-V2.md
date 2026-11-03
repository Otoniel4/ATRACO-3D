# Preparar el rig y las animaciones de los personajes V2

Estado: los modelos son propios, están en Blender y exportados a FBX. Todavía no tienen esqueleto, pesos ni animaciones. Los dos cuerpos cerrados en T sirven para solicitar el auto-rig; los cuerpos en A conservan la pose de las prendas de referencia.

## Auto-rig que realiza Alain

1. Aprueba primero la forma y el vestuario usando las comparaciones de esta entrega.
2. Abre https://www.mixamo.com/ e inicia sesión con tu cuenta de Adobe.
3. En **Upload Character**, sube `C:\Users\Alain\Atraco3D\Assets\Party\Art\Characters\ReferenceV2\NPC2_BaseMale_TPose.fbx`.
4. Coloca los marcadores siguiendo la pantalla y revisa la deformación del cuerpo. Nuestros cuerpos son geométricos y usan colores planos; no requieren texturas externas.
5. Descarga el personaje rigeado en FBX **con piel**. Conserva el archivo original descargado.
6. Repite con `NPC2_BaseFemale_TPose.fbx` de la misma carpeta.
7. Guarda los resultados como `RiggedMale_V2.fbx` y `RiggedFemale_V2.fbx` en `Assets/Party/Art/Characters/ReferenceV2/Rigged/`. Avísame cuando estén allí.

Adobe documenta la subida de personajes propios, los marcadores y la descarga del rig en su [guía oficial de Mixamo](https://helpx.adobe.com/creative-cloud/help/mixamo-rigging-animation.html). La subida y descarga las hace Alain, según AGENTS.md; no existe una API de Mixamo en este flujo.

## Trabajo que sigue al recibir esos FBX

Revisar huesos y escala; colocar el esqueleto en la pose A de las prendas; transferir pesos desde el cuerpo continuo; vincular cabello, ojos y accesorios; corregir hombros, manos, codos, rodillas y ropa. Después configurar y validar el Avatar Humanoid en Unity 6000.3.27f2. Los uniformes conservan el equipamiento de las referencias; la porra del guardia y el arma policial se adjuntarán como accesorios del juego.

## Clips acordados

La tabla contiene búsquedas sugeridas, no una garantía de nombres disponibles en el catálogo. Si no existe un movimiento adecuado, se realizará con keyframes sobre el esqueleto de Mixamo.

| Clip del juego | Búsqueda o producción | Bucle |
| --- | --- | --- |
| Idle | Idle | Sí |
| Walk | Walking; In Place | Sí |
| Run | Running; In Place | Sí |
| CrouchIdle | Crouch Idle | Sí |
| CrouchWalk | Crouch Walking; In Place | Sí |
| AimPistol | Pistol Idle / Pistol Aim | Sí |
| ShootPistol | Pistol Shoot | No |
| ScaredCrouch | Terrified / Cowering | Sí |
| HandsUp | Hands Up | Sí |
| Flee | Running; In Place | Sí |
| KnockedDown | Knocked Down | No |
| RevivePartner | Help Up; si no corresponde, keyframes propios | No |
| BatonStrike | Melee Attack; ajustar para porra | No |
| Handcuff | Arrest; si no corresponde, keyframes propios | No |
| ComicFall | Caída y ajuste cómico con keyframes | No |
| PullDriverOut | Keyframes propios; acción de quien tira | No |
| DraggedFromCar | Keyframes propios; acción de quien es sacado | No |
| DriveSeated | Driving | Sí |
| ExitCarRunning | Keyframes propios y salida hacia carrera | No |

Para los clips: FBX sin piel, 30 fps y el mismo esqueleto de origen. Usar In Place en locomoción cuando esté disponible. Después comprobar retargeting entre cuerpos, bucles, apoyos y root motion. Animator y NetworkAnimator corresponden a las tareas de integración posteriores; no se han creado en esta entrega.
