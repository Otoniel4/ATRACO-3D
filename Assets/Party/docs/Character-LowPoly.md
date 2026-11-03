# Cabeza low poly de Alarma - 2026-11-01

Alain rechazó la cabeza anterior y pidió una versión low poly sencilla, sin buscar anatomía realista.
Se construyó directamente en el Blender conectado y se guardó una versión reproducible con Blender 4.5.15.

## Resultado

- Cabeza de cubo biselado, ligeramente estrechada abajo, con sombreado plano.
- Orejas geométricas, ojos negros con un punto claro, cejas, nariz de pocos polígonos y sonrisa gráfica.
- Pelo en masas facetadas con moño alto. Aros recolocados junto a las orejas.
- Cuerpo y prendas de la revisión anterior conservados; altura total de 1,65 m.
- Cabeza, facciones y pelo: 590 triángulos. El personaje completo conserva 16620 triángulos porque se mantuvieron las mallas anteriores del cuerpo, ropa y accesorios. No se presenta como una optimización completa a 4.000 triángulos.
- Nueve mallas y un rig de 21 huesos. Las piezas de la cabeza siguen rígidamente el hueso Head.

## Archivos

- `character_lowpoly.blend`: archivo editable independiente, escena Female_LowPoly.
- `build_lowpoly_head.py`: construcción reproducible. Usa baseline/character.blend, que es el modelo propio anterior.
- `export/character_lowpoly.fbx`: exportación con FBX All, -Z Forward, Y Up, Apply Transform, sin cámaras, luces, leaf bones ni clips.
- `renders/`: cabeza frontal, lateral y tres cuartos; personaje completo de frente y espalda.
- `viewport_head.png`: captura del viewport revisada en Blender 5.2.3.
- `validation.json`: pruebas reales de la malla y del FBX reimportado.

## Verificación

Se comprobó que cabeza y cuerpo están cerrados, que ojos y boca miran hacia fuera y que las cuatro prendas principales conservan sus posiciones.
El FBX reimportado mantiene 1,65 m, nueve mallas, 21 huesos y pesos en todos los vértices.
Se giró Head 25 grados: cabeza, ojos, boca, pelo y aros siguen su transformación rígida, sin separarse. La pose inicial se recupera al restaurar las matrices.
El Avatar de Unity aún requiere revisión dentro del editor; no se crearon animaciones finales ni se cambiaron prefabs.

## Cómo revisar

1. En el Blender abierto está la escena Female_LowPoly, encuadrada sobre la cara. También puedes abrir character_lowpoly.blend.
2. Revisa frente, perfil y tres cuartos en renders. Esta dirección de estilo queda pendiente de la aprobación visual de Alain.
3. Después de aprobarla, importa el FBX dentro de Assets/Party, configura Rig = Humanoid y revisa Configure con un clip de prueba.

## Regenerar

Desde esta carpeta:

```text
blender -b --python-exit-code 1 -P build_lowpoly_head.py
blender -b --python-exit-code 1 -P validate_lowpoly.py
```

Las medidas de cabeza y rasgos están al inicio del script. Se usa geometría y materiales propios; no se descargaron modelos ni texturas.

## Explicación para aprender

El bisel de pocos segmentos redondea las esquinas sin crear una mandíbula anatómica compleja. El sombreado plano hace visibles las facetas.
Los ojos y la sonrisa son formas gráficas; el pelo usa masas simples. Estas piezas se vinculan rígidamente a Head para evitar deformar sus formas al girar la cabeza.
La cabeza se mantiene separada del cuerpo para facilitar ajustes del estilo. El cuerpo conserva su rig previo y la ropa actual.
