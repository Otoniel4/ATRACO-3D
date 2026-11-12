# Objetos propios de negocios R44 — revisión visual

2026-11-10. Generados mediante Blender MCP; no se descargaron recursos externos. Estilo estilizado con geometría de detalle, materiales y etiquetas en malla. No incluye todavía texturas bitmap para tejidos ni suciedad.

## Lote

| Local | Objetos |
|---|---|
| Minimarket | Botella de reserva, leche, café |
| Supermercado | Lata de cola, aceite, cereal |
| Joyería | Anillo con piedra y garras, reloj con correa/índices, collar de eslabones |
| Banco | Lingote marcado, maletín con cierres/asa, sobre sellado |
| Comida | Hamburguesa por ingredientes, vaso con tapa/pajita, caja de pizza ventilada |
| Ropa | Bolso con asas/costuras/cremallera, zapatilla con cordones/suela, camiseta doblada |

## Archivos

- `Assets/Party/Art/BlenderScripts/build_shop_objects_r44.py`: receta reutilizable; crea una escena nueva y conserva la escena previa.
- `Assets/Party/Art/BlenderScripts/ShopObjectsR44~/Objetos_Negocios_R44.blend`: fuente y galería.
- La misma carpeta contiene 18 FBX, `catalog.json`, `validation.json` y `Catalogo.png`.

Reimportados los 18 FBX: dimensiones contrastadas con tolerancia de 2 mm y tres anclas presentes por pieza (54). Vista de cámara inspeccionada mediante MCP y render revisado. La galería amplía cada objeto para mostrar detalles: no representa sus proporciones relativas. Los FBX conservan escala real en metros.

## Agarres y límites

`Support` indica apoyo; `Grip_R` y `Grip_L` son referencias iniciales de agarre. Maletín, pizza y camiseta están marcados para dos manos. Los JSON incluyen coordenadas Blender y Unity. Son referencias geométricas, no prueba de contacto con los rigs: faltan orientación fina, cierre de dedos, colisiones de mano y trayectorias por objeto. El código actual de compras no consume todavía este catálogo.

Los objetos son candidatos a mercancía robable. No se implementó recogida, precio de reventa ni consumo de inventario. No se sustituyeron modelos activos ni se abrió Unity. La carpeta con `~` evita importaciones parciales del lote de revisión.

## Pasos y prueba

1. En Blender, revisar la escena `R44_Objetos` o abrir el `.blend` de esta entrega. Usar la cámara para ver la galería.
2. Revisar especialmente asas, etiquetas, joyas y prendas; aprobar o indicar ajustes del diseño.
3. Después de aprobar el lote: crear catálogo Unity por producto, validar las manos de los NPC y preparar materiales URP. Solo entonces sustituir los productos genéricos y probar cada negocio con Alarma/Crear y probar juego.

## Explicación para aprender

Una etiqueta y una tapa no sustituyen la forma: cada modelo tiene su silueta y piezas propias.
Las anclas separan la geometría de las decisiones de animación.
El catálogo guarda dimensiones y tipo de agarre; la animación futura debe leer esos datos.
Esta separación sigue responsabilidad única y permite agregar productos sin duplicar toda la rutina de compra.
