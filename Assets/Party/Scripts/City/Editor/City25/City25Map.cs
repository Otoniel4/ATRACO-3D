using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.UI.Map;

namespace Alarma.City.Editor
{
    // Datos del mapa (tecla M) y del minimapa de la ciudad de 2 × 2 km: fondo, categorías, iconos y lugares del plano.
    internal static class City25Map
    {
        public static CityMapDefinition Create(string folder)
        {
            var catalog = City25Paths.Read<MapCatalog>(City25Paths.Map + "/map_places.json");
            var map = ScriptableObject.CreateInstance<CityMapDefinition>();
            map.Title = "Villa Alarma · ciudad 2 × 2 km";
            map.Background = Background(City25Paths.Map + "/mapa_base.png");
            map.PlayerIcon = Icon("jugador");
            map.WorldMin = new Vector2(catalog.world_min[0], catalog.world_min[1]);
            map.WorldMax = new Vector2(catalog.world_max[0], catalog.world_max[1]);
            map.Categories = catalog.categories.Select(c => new MapCategory
            {
                Id = c.id, Label = c.label, Group = c.group, Icon = Icon(c.id),
                Color = ColorUtility.TryParseHtmlString(c.color, out Color color) ? color : Color.white
            }).ToArray();
            map.Places = catalog.places.Select(p => new MapPlace { Category = p.category, Name = p.name, Position = City25Paths.World(p.x, p.y) }).ToArray();
            AssetDatabase.CreateAsset(map, folder + "/Data/CityMap.asset");
            return map;
        }

        private static Texture2D Icon(string id)
        {
            string path = City25Paths.Map + "/Icons/" + id + ".png";
            // Iconos nítidos: sin compresión ni mipmaps y con transparencia limpia en los bordes.
            var importer = (TextureImporter)AssetImporter.GetAtPath(path) ?? throw new System.IO.FileNotFoundException("Falta el icono del mapa", path);
            if (importer.mipmapEnabled || importer.textureCompression != TextureImporterCompression.Uncompressed || !importer.alphaIsTransparency)
            {
                importer.mipmapEnabled = false; importer.textureCompression = TextureImporterCompression.Uncompressed; importer.alphaIsTransparency = true; importer.wrapMode = TextureWrapMode.Clamp;
                importer.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        private static Texture2D Background(string path)
        {
            // Mipmaps para que el mapa alejado no parpadee; compresión de alta calidad para no ocupar 16 MB.
            var importer = (TextureImporter)AssetImporter.GetAtPath(path) ?? throw new System.IO.FileNotFoundException("Falta el fondo del mapa", path);
            if (!importer.mipmapEnabled || importer.textureCompression != TextureImporterCompression.CompressedHQ || importer.wrapMode != TextureWrapMode.Clamp || importer.maxTextureSize != 2048)
            {
                importer.mipmapEnabled = true; importer.textureCompression = TextureImporterCompression.CompressedHQ; importer.wrapMode = TextureWrapMode.Clamp; importer.maxTextureSize = 2048;
                importer.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
    }
}
