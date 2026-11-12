# Objetos de negocios R44 — preparación, no integrado

Solicitud de Alain, 2026-11-10: sustituir los productos genéricos por objetos específicos, añadir materiales/texturas y preparar bienes robables. Autoriza recursos gratuitos externos para este lote; sustituye la prohibición previa de descargarlos en este alcance. Primero aprobar objetos, después ajustar animaciones.

## Lote propuesto

| Negocio | Objetos para comprar/manipular | Bienes robables propuestos |
|---|---|---|
| Minimarket | Botella con tapa y etiqueta, lata con anilla, paquete de café, cartón de leche, bolsa de pan | Botellas de licor, café y mercancía de estante |
| Supermercado | Caja de cereal con gráfica, botella de aceite, caja de huevos, detergente con asa, fruta | Mercancía, pequeños electrodomésticos y caja registradora |
| Joyería | Anillo con piedra y estuche articulado, reloj con correa, collar con cierre, pendientes | Joyas individuales, relojes, bandejas de joyas |
| Banco | Tarjeta, comprobante, sobre de documentos, fajo con banda | Lingotes, documentos y maletín de valores; además de efectivo |
| Comida | Hamburguesa por piezas, vaso con tapa, bandeja, caja de pizza, bolsa de pedido | Mercancía y equipos pequeños; decoración pesada queda fija |
| Ropa | Camiseta doblada con costuras, pantalón, zapatillas, bolso con asas, gorra | Prendas, accesorios y bolsos |

Los bienes robables son propuesta de diseño: contrastar valores, peso y capacidad con el GDD antes de implementar economía. No se declara implementado el robo ni se altera el inventario actual.

## Criterios de aceptación por objeto

- Silueta reconocible y detalles propios: cierres, asas, tapas, costuras, etiquetas y partes separadas cuando corresponda.
- Escala en metros, origen coherente, base de apoyo plana y colisión simple.
- Puntos separados de agarre izquierdo/derecho, apoyo y entrega; indicar una o dos manos. No usar el centro de límites como agarre universal.
- Materiales compatibles con URP. Texturas pequeñas para etiquetas y tejidos, metal/vidrio mediante materiales; coherencia con el estilo del mundo.
- Modelo del estante y modelo transportable comparten identidad; sin incluir expositor, bandeja o embalaje fijo accidentalmente.
- Registrar fuente, licencia, dimensiones y captura frontal/lateral/en mano. Aprobar visualmente antes de sustituir prefabs de compras.
- Mantener la escena actual hasta tener sustitutos comprobados. No borrar productos antiguos aún referenciados.

## Fuentes comprobadas

- Kenney Food Kit: https://kenney.nl/assets/food-kit — página oficial declara 200 modelos y CC0. Candidato para alimentos y envases.
- Quaternius Ultimate Food Pack: https://quaternius.com/packs/ultimatefood.html — página oficial declara 103 modelos, FBX/OBJ/Blend y CC0. Alternativa de estilo.

No se ha importado ninguno de estos packs. El primer intento de descarga de Kenney devolvió contenido que no era ZIP. `Tools~/prepare_food_kit.py` valida el formato antes de extraer y conserva procedencia/hash si descarga correctamente. No registrar como recurso incorporado en LICENSES hasta disponer del archivo y su licencia.

## Estado y prueba

La revisión del código confirma que ShopTaskSettings usa un único ProductPrefab por negocio y varios locales comparten ProductBox. Hará falta un catálogo por producto y una elección guardada en cada sesión para variar productos sin cambiarlos durante la compra.

Blender MCP no respondió. Pendientes descarga válida, diseño/adaptación, capturas y catálogo de runtime. Este documento no representa modelos terminados.

1. Conectar Blender MCP con el proyecto abierto para preparar la revisión visual.
2. Revisar el lote completo antes de sustituir modelos en Unity.
3. Tras integrar el catálogo, usar Alarma/Crear y probar juego y comprobar que cada NPC conserva el mismo producto desde el estante hasta la salida.

## Explicación para aprender

Una textura mejora la superficie, pero no cambia la silueta de un cubo.
Cada producto necesita geometría, material y puntos de contacto propios.
Separar la definición del producto de la rutina de compra permite añadir mercancías sin reescribir la animación.
Esa separación aplica responsabilidad única y prepara una ampliación mediante datos configurables.
