# Origen de recursos de Alarma

## Personajes V2 — 2026-10-31

Referencias: 14 láminas aportadas por Alain desde su carpeta `NPC_referencias`; el LEEME original indica que se generaron con la herramienta integrada de imágenes. Se conservan como referencias, no como texturas del juego.

Geometría y materiales: creados en Blender con scripts bpy propios (`npc_v2.py`); sin descargar modelos ni texturas. No se han incorporado rigs ni clips de Mixamo. Cuando Alain los descargue, registrar aquí los archivos, la fecha, el origen y las condiciones aplicables.

Herramienta de conexión: [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender), MIT; herramienta de producción, no asset del juego. Integraciones de bibliotecas y generadores externos desactivadas.


## Blockout Blender 4.x — 2026-10-31

Geometría y materiales generados con bpy propio; sin modelos ni texturas descargados. Referencias: recortes de la lámina 02_civil_mujer.png aportada por Alain. Rig propio con Bone Heat y reparación automática de pesos mediante Data Transfer; sin clips ni archivos de Mixamo. Blender 4.5.15 portable se obtuvo del repositorio oficial y se comprobó el SHA-256; es una herramienta de producción y no un recurso del juego.

## Elenco low poly — 2026-11-01

18 personajes (17 nuevos y una mujer aprobada) construidos con bpy propio a partir de nuestra base. Materiales planos y accesorios geométricos propios. Vestuario guiado por las láminas aportadas por Alain. Sin modelos ni texturas descargados; sin recursos, rigs ni clips de Mixamo incorporados. Scripts y procedencia en Art/BlenderScripts/LowPolyCast~/README.md. Blender 4.5.15 portable ya verificado se utilizó para generar y comprobar FBX; Blender conectado para revisar el viewport. Las integraciones de bibliotecas y generadores externos siguen sin usarse. Las tipografías del README no se exportan como assets del juego; los rótulos de la galería 3D usan la fuente incluida en Blender y las hojas de revisión usan Arial instalada localmente.

## Toñito Gym R1 — 2026-11-01

Corrección geométrica y de pesos con bpy propio sobre nuestras bases. Fuentes y procedencia en Art/BlenderScripts/TonitoGymR1~/README.md. Sin modelos, texturas ni clips externos. No se incorporó Mixamo. Capturas y hojas de comparación son renders del modelo propio; Arial instalada localmente solo se usa en los rótulos de revisión.

## Revisión de piernas R2 — 2026-11-01

Correcciones de geometría y pesos con bpy propio sobre el elenco anterior. Sin modelos, texturas ni animaciones externos; no se incorporó Mixamo. Fuentes y procedencia en Art/BlenderScripts/RigLegsR2~/README.md. Diagramas de articulaciones derivados de sus posiciones reales. Arial instalada localmente se usa solo en hojas de revisión.

## Piernas del elenco R3 — 2026-11-01

Corrección de geometría y pesos mediante bpy propio sobre el elenco R2. Sin modelos, texturas ni clips externos; no se incorporó Mixamo. Fuentes y procedencia en Art/BlenderScripts/CastLegsR3~/README.md. Renders, capturas y comparaciones del modelo propio; Arial instalada localmente se usa solo en hojas de revisión.


## Mapa low poly de 4 × 4 km — 2026-11-01

Ciudad, piezas modulares y paleta creadas con bpy propio. Interiores, coches y figuras de escala reutilizan nuestra biblioteca y elenco R3. Sin modelos, texturas ni clips externos. Imagen generated-image-1793470363247-canvus-ai.png aportada por Alain, conservada solo como referencia de composición; no se usa como textura. Rótulos 3D con la fuente incluida en Blender y láminas con Arial instalada localmente. Fuentes y procedencia: Art/BlenderScripts/Map4Km~/README.md.


## Ciudad moderna R2 — 2026-11-01

Arquitectura, vegetación y equipamiento de la revisión creados con bpy propio. Terreno, trazado, coches y figuras reutilizan nuestras entregas anteriores. Sin modelos ni texturas descargados. Cielo procedural nativo de Blender; fuente incluida para los rótulos 3D. Arial instalada localmente solo para hojas de revisión. La referencia aportada por Alain guía la composición y no se usa como textura. Sin Mixamo en esta entrega. Fuentes: Art/BlenderScripts/Map4KmModernR2~/README.md.

## Árboles y viento R3 — 2026-11-01

Seis especies, ramas, hojas, paleta y movimiento procedural creados con bpy y shader HLSL propios. El mapa base es nuestra ciudad moderna R2. Sin modelos, texturas ni clips descargados; sin Mixamo. Blender 4.5.15 portable ya verificado se usa para generar, reimportar y revisar; FFmpeg/FFprobe instalados localmente codifican y comprueban el vídeo. Arial local solo se usa en la hoja de revisión. Fuentes, captura y procedencia en Art/BlenderScripts/TreesWindR3~/README.md. La entrega no incorpora ejecutables de herramientas.

## Jardineras y pasto R4 — 2026-11-01

Arbustos de hojas individuales, flores, macetas, bordes, briznas y colores creados con bpy propio. El mapa y arbolado base son nuestras revisiones R2/R3. Viento Geometry Nodes y shader reutilizan nuestra fórmula R3; sin modelos, texturas ni clips descargados y sin Mixamo. FFmpeg/FFprobe locales codifican y comprueban el vídeo. Fuentes y procedencia: Art/BlenderScripts/PlantersGrassR4~/README.md. No se incluyen ejecutables de herramientas.

## Ciudad viva R5 — 2026-11-02

32 piezas y 50 clips propios generados con bpy. Los diez civiles reutilizan nuestras mallas/pesos R3; el mapa reutiliza R4 y conserva vegetación y máscaras. Sin modelos, texturas, animaciones ni sonidos descargados; sin Mixamo. Rótulos geométricos con fuente incluida en Blender. FFmpeg/FFprobe codifican y verifican medios; .NET compila comprobaciones contra DLL de Unity instaladas, sin redistribuir esas DLL ni ejecutables. Shader de viento propio reutilizado de R3. Fuentes: Art/BlenderScripts/CityLifeR5~/README.md.

## Ciudad: manos y compras R6 — 2026-11-02

Palmas, dedos, rig ampliado, 90 clips propios, cinco productos y tres expositores creados mediante bpy sobre nuestros modelos R3/R5. Se reutilizan 32 piezas propias e interiores/vegetación R4/R5. Sin modelos, texturas, animaciones o sonidos descargados. Rótulos geométricos con fuente incluida en Blender. Pillow compone el resumen y las etiquetas con Arial instalada localmente; no se redistribuye la fuente. FFmpeg/FFprobe codifican/verifican medios. .NET compila contra DLL de Unity instaladas, que no se redistribuyen. Fuentes y comprobaciones: Art/BlenderScripts/CityLifeR6~.

## Prueba integrada R7 — 2026-11-02

Ciudad R6 propia repartida en 263 partes y nueve exportaciones de puerta, conservando mallas, materiales y máscaras. Controles, cámara, carga por distancia, catálogo e interfaz C# propios. Sin modelos, texturas, animaciones ni sonidos descargados. Blender 4.5.15 exporta y reimporta; .NET compila contra DLL de Unity instaladas, que no se redistribuyen. Fuentes y guía: Art/BlenderScripts/PlaytestR7~ y docs/Prueba-Completa-R7.md.

## Correcciones de prueba R8 — 2026-11-02

Clips de carrera, puertas, correas de bolsa, plano de ciudad y código propios; se conservan los modelos y materiales propios de R6/R7. Sin modelos, texturas ni animaciones descargados. Blender 4.5.15 portable exporta y reimporta; las capturas de revisión son renders Blender. Fuentes en Art/BlenderScripts/PlaytestR8~. Las DLL de Unity se utilizan localmente para comprobar compilación, sin redistribuirlas.

## Ciudad y correcciones R9 — 2026-11-02

Geometría de barrio comercial/escondite, productos, puertas, plano, clips de carrera y código generados para Alarma con bpy y C# propios. Conserva y recorta ciudad, personajes y vegetación propios de revisiones anteriores. Sin modelos, texturas ni animaciones descargados. Blender 4.5.15 portable para construir, exportar, reimportar y renderizar; renders no proceden de Unity. Recetas y evidencia en Art/BlenderScripts/PlaytestR9~. Las DLL instaladas de Unity se utilizan para compilación local y no se redistribuyen.

## Seguridad y policía sobre Quaternius UBC — 2026-11-03

Cuerpos base, ojos, cejas y peinados: [Universal Base Characters (Standard)](https://quaternius.com/packs/universalbasecharacters.html) de Quaternius, CC0 1.0 (dominio público), según `License_Standard.txt` del paquete. Descargado por Alain el 2026-11-03 en `Art/ThirdParty~/Quaternius_UBC/`; el crédito no es obligatorio. Se usan el cuerpo Superhero hombre y el peinado Buzzed (seguridad y policía son solo hombres); no se usan sus texturas.

Uniformes, botas, cinturón, gorra, radio, porra, funda y rótulos: bpy propio (`Art/BlenderScripts/SecurityUBC~/build_security.py`), guiados por las láminas 11 a 14 aportadas por Alain. Colores planos. Sin Mixamo. Los rótulos usan la fuente incluida en Blender.

## Elenco low-poly modular — 2026-11-03

Cuerpos, ropa base, peinados y animaciones: [Ultimate Modular Men](https://quaternius.com/packs/ultimatemodularcharacters.html) y [Ultimate Modular Women](https://quaternius.com/packs/ultimatemodularwomen.html) de Quaternius, CC0 1.0 según el `License.txt` de cada paquete. Descargados por Alain el 2026-11-03 en `Art/ThirdParty~/Quaternius_Modular/`; el crédito no es obligatorio. Se combinan piezas (cabeza, torso, piernas y pies) y se recolorean con colores planos.

Accesorios propios con bpy (`Art/BlenderScripts/ModularCast~/build_cast.py`): cinturón, radio, porra, funda con empuñadura, gorra, charreteras y rótulos (fuente incluida en Blender). Sin Mixamo. Sustituye a la versión sobre Universal Base Characters para que todo el elenco comparta un estilo.

## Retirada de Universal Base Characters — 2026-11-03

El pack Universal Base Characters y los personajes construidos sobre él ya no se usan: todo el elenco sale de los packs modulares. Se movieron fuera del proyecto, a `C:\Users\Alain\Atraco3D_Retirado\2026-11-03\`. Del pack modular solo se conservan los `.blend` maestros, el `License.txt` y la vista previa; el resto de formatos se puede volver a descargar.

## Mapa de la ciudad e iconos — 2026-11-03

`Art/UI/Map/mapa_base.png`, los iconos de `Art/UI/Map/Icons/` y `plano_ciudad.png` se dibujan con `City25~/city_plan.py`. Los glifos de los iconos salen de Noto Emoji y los textos de Inter, ambas fuentes con licencia SIL Open Font License 1.1, tomadas de la instalación de Blender. No se usan fuentes de Windows en recursos del juego. Dentro del juego, los textos del mapa usan la fuente integrada de Unity.

## Clips de uso de objetos — 2026-11-05

`Art/Characters/Animations/Alarma_ItemActions_Men.fbx` y `_Women.fbx` contienen solo el esqueleto de los packs Ultimate Modular Men y Women de Quaternius (CC0 1.0, ver arriba) y 12 clips propios: once acciones y el clip de referencia «Reposo». Los clips se animan con bpy en `Art/BlenderScripts/build_action_clips.py` a partir de `Data/Items/item_actions.json` y parten del primer cuadro del clip `Idle_Neutral` del mismo pack. No se usan clips de Mixamo ni de otras bibliotecas. La Universal Animation Library de Quaternius (CC0) queda como fuente posible: si Alain la descarga, se registra aquí antes de usarla.

## Clips de reacción de los civiles — 2026-11-06

`Art/Characters/Animations/Alarma_NpcReactions_Men.fbx` y `_Women.fbx` contienen solo el esqueleto de los packs Ultimate Modular de Quaternius (CC0 1.0) y cinco clips propios animados con bpy en `Art/BlenderScripts/build_npc_reaction_clips.py`: suplicar, rendirse, amarrado y levantarse boca arriba y boca abajo. La caída se calcula con la física de Unity (ragdoll) y no usa clips. Sin Mixamo ni bibliotecas externas.

## Universal Animation Library de Quaternius — 2026-11-09

[Universal Animation Library (Standard, v3.0)](https://quaternius.itch.io/universal-animation-library) de Quaternius, CC0 1.0 (dominio público) según el `License.txt` del paquete; el crédito no es obligatorio. Descargado el 2026-11-09 con autorización de Alain desde itch.io («Universal Animation Library[Standard].zip», 15 MB, versión gratuita) en `Art/ThirdParty~/Quaternius_UAL/`. Trae 43 clips sobre un esqueleto humanoide universal (`UAL1_Standard.fbx`), distinto del esqueleto de los packs Ultimate Modular del elenco: para usarlos hay que pasarlos a ese esqueleto en Blender. `Art/BlenderScripts/retarget_ual_clips.py` pasa 12 de sus clips (reposo, conversar, caminar, caminar formal, trotar, correr, agachado quieto y caminando, sentarse, sentado, sentado conversando y pararse) al esqueleto del elenco y los exporta en `Art/Characters/Animations/Alarma_Locomotion_Men.fbx` y `_Women.fbx` (solo esqueleto y clips; obra derivada de material CC0). Alain aprobó las capturas el 2026-11-09; reposo, caminar, trotar y correr se usan en la locomoción de peatones, clientes, jugador, guardias de puesto y dobles de reacción.

## Celular de los NPC y clips de celular y arresto — 2026-11-10

`Art/Props/Prop_NpcPhone.fbx` es un modelo propio hecho con bpy (`Art/BlenderScripts/build_npc_phone.py`, 800 triángulos, colores planos, sin texturas ni bibliotecas externas). Los clips nuevos `Grabar` (rehecho), `Llamar` y `Esposar` son propios, animados con bpy en `build_npc_reaction_clips.py` sobre el esqueleto de los packs Ultimate Modular de Quaternius (CC0 1.0). El agente usa además `Idle_Gun_Pointing` del mismo pack. Sin Mixamo.

## Poses de dedos para sujetar objetos — 2026-11-11

`Art/Characters/Animations/hand_poses.json` (cinco poses: Cilindro, Caja, Pinza, Plano, Asa) es propio. Lo genera `Art/BlenderScripts/build_hand_poses.py` con bpy sobre la mano de los modelos del elenco, cerrando cada articulación contra un objeto de prueba; no usa clips, modelos ni bibliotecas externas. Capturas: `docs/Capturas/Manos/`.
