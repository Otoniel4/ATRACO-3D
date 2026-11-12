# Corrección de «LataCola: falta Support»

2026-11-10. Corrección dentro de la integración de objetos; pendiente de prueba de Alain en Unity.

## Causa

Blender exportó marcadores únicos con sufijos: la lata contiene `Support.003`, `Grip_R.003` y `Grip_L.003`. El constructor exigía el nombre exacto sin sufijo. La construcción se interrumpía y se intentaba recuperar la escena anterior. «No cameras rendering» en la captura no demuestra que se haya borrado la ciudad: la construcción no llegó a preparar su escena jugable.

Los materiales del escondite también contienen sufijos numéricos, por ejemplo `Alarma_Hideout_Facade.002`, mientras los manifiestos contienen el nombre original.

## Archivos

- `Scripts/City/Editor/CityLifeR5/BlenderAssetNames.cs`: reconoce únicamente sufijos numéricos de Blender de tres o más cifras.
- `Scripts/City/Editor/City25/City25Products.cs`: admite esos nombres y exige exactamente un marcador de cada tipo. Ante ambigüedad informa los nombres encontrados.
- `Scripts/City/Editor/CityLifeR5/FlatMaterialLibrary.cs`: las copias sin definición propia usan el material original; una entrada explícita conserva su color.
- `Art/BlenderScripts/ShopObjectsR44~/AnchorNameTests.cs`, `test_anchor_names.py` y `validate_integration.py`: pruebas reproducibles y compilación.

## Verificación

Se leyeron los nombres de nodos de los 18 archivos FBX activos: 54 marcadores únicos encontrados. Pasan 62 comprobaciones con el resolutor C# real, incluyendo sufijos inválidos y ambigüedad. Pasan 360 comprobaciones de alcance. Compilan CityLife, CityLife.Editor, Playtest y City.Editor contra las DLL instaladas. No se abrió Unity, no se modificaron los modelos ni se guardaron escenas.

## Pasos en el editor y prueba

1. Cierra el cuadro de error y sal de Play si está activo. Espera a que Unity termine de compilar.
2. Limpia Console para separar los mensajes anteriores de los nuevos.
3. Pulsa **Alarma > Crear y probar juego**.
4. Comprueba que termina la construcción, aparece la cámara del jugador y no vuelve el error del marcador. Revisa los colores del escondite y después las compras de los NPC.

No guardes una escena vacía encima de la escena de ciudad. No hace falta borrar Library ni regenerar los modelos. La construcción completa y la prueba en Play quedan pendientes de Alain.

## Explicación para aprender

Un nombre visible puede cambiar durante la exportación aunque el objeto siga existiendo. Ahora una función dedicada interpreta los sufijos de Blender y el constructor sigue exigiendo un único marcador válido. Así se separa la regla de nombres de la creación de productos, aplicando responsabilidad única, sin ocultar modelos realmente incompletos.
