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
