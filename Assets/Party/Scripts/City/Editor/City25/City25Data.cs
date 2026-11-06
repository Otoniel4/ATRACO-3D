using System;
using System.IO;
using UnityEngine;

// Los campos de estos datos los llena JsonUtility al leer los JSON del plano.
#pragma warning disable CS0649
namespace Alarma.City.Editor
{
    // Rutas de entrada (plano, kit, suelo, mapa) y de salida regenerable de la ciudad de 2 × 2 km.
    internal static class City25Paths
    {
        public const string Plan = "Assets/Party/Art/BlenderScripts/City25~";
        public const string Kit = "Assets/Party/Art/City/Kit25";
        public const string Ground = "Assets/Party/Art/City/Ground25";
        public const string Map = "Assets/Party/Art/UI/Map";
        public const string Cast = "Assets/Party/Art/Characters/Cast";
        public const string Vehicles = "Assets/Party/Art/Vehicles";
        public const string Shops = "Assets/Party/Art/City/Shops";
        public const string Weapons = "Assets/Party/Art/Weapons";
        public const string Output = "Assets/Party/Generated/Ciudad2km";
        public const string SceneSuffix = "/Scenes/Ciudad_2km.unity";
        public const string Scene = Output + SceneSuffix;
        public const string Revisions = Output + "/Revisiones";
        public const string Report = Output + "/BuildReport.json";

        public static bool IsCityScene(string path)
        {
            if (path == Scene) return true;
            const string prefix = Revisions + "/R_";
            return path != null && path.Length == prefix.Length + 32 + SceneSuffix.Length
                && path.StartsWith(prefix, StringComparison.Ordinal) && path.EndsWith(SceneSuffix, StringComparison.Ordinal)
                && Guid.TryParseExact(path.Substring(prefix.Length, 32), "N", out _);
        }
        // Colores planos del kit y del elenco, y los del suelo nuevo.
        public static readonly string[] ColorManifests = { "Assets/Party/Art/Materials/FlatColors.json", Ground + "/ground_materials.json", Vehicles + "/vehicle_materials.json", Shops + "/shop_materials.json", Kit + "/street_materials.json", Kit + "/district_materials.json", Shops + "/hideout_materials.json", Weapons + "/weapon_materials.json" };

        public static T Read<T>(string path) => JsonUtility.FromJson<T>(File.ReadAllText(path)) ?? throw new InvalidDataException("No se pudo leer " + path);
        // Plano: X este, Y norte. Unity: X este, Z norte.
        public static Vector3 World(float x, float y) => new Vector3(x, 0f, y);
    }

    [Serializable] internal sealed class KitManifest { public KitPiece[] pieces = Array.Empty<KitPiece>(); }
    [Serializable] internal sealed class KitPiece { public string id, group, kind; public float width, depth, height; }

    [Serializable] internal sealed class CityObjects { public CityObject[] objects = Array.Empty<CityObject>(); }
    [Serializable] internal sealed class CityObject
    {
        public string kit, kind, name;
        public float x, y, yaw;
        public float z; // alto del apoyo: vereda o asfalto (0 si va sobre el terreno)
        public int signal = -1, axis = -1; // solo en semáforos: cruce y eje al que miran
        public int[] sector = Array.Empty<int>();
        public float[] size = Array.Empty<float>();
        public PlaceTag place;
        public bool HasPlace => place != null && !string.IsNullOrEmpty(place.kind);
    }
    [Serializable] internal sealed class PlaceTag { public string kind, name; }

    // Datos de la ciudad viva (city_life.py): ejes de cada semáforo y red peatonal en listas planas.
    [Serializable] internal sealed class CityLife
    {
        public LifeSignal[] signals = Array.Empty<LifeSignal>();
        public float[] nodes = Array.Empty<float>();
        public int[] edges = Array.Empty<int>();
    }
    [Serializable] internal sealed class LifeSignal { public float x, y; public float[] axes = Array.Empty<float>(); }

    // Carriles de autos (city_traffic.py): puntos en lista plana, enlaces siguientes y control del final.
    [Serializable] internal sealed class CityTraffic { public TrafficLink[] links = Array.Empty<TrafficLink>(); }
    [Serializable] internal sealed class TrafficLink { public float[] points = Array.Empty<float>(); public int[] next = Array.Empty<int>(); public int control, signal, axis; public float speed; }

    // Locales con interior (build_shops.py): puntos en coordenadas locales del modelo (frente +Z), en listas planas.
    [Serializable] internal sealed class ShopLayouts { public ShopLayout[] shops = Array.Empty<ShopLayout>(); }
    [Serializable] internal sealed class ShopLayout
    {
        public string kind, model, product, product_name;
        public int price_cents;
        public float width, depth, door_width;
        public float[] walkable, obstacles, sidewalk, entry, exit, stations, products, queue, counter, scan, cashier, receipt, till;
        public StaffPost[] staff = Array.Empty<StaffPost>();
    }
    // Puesto de un empleado en coordenadas locales del local; pose «stand» o «seat» y materiales de su uniforme.
    [Serializable] internal sealed class StaffPost { public string role, pose, top, bottom; public float x, z, yaw, seat; }
    // Prendas de cada civil que se cambian por el uniforme (analyze_staff_uniforms.py).
    [Serializable] internal sealed class UniformSlots { public UniformModel[] models = Array.Empty<UniformModel>(); }
    [Serializable] internal sealed class UniformModel { public string model; public string[] top = Array.Empty<string>(), bottom = Array.Empty<string>(); }

    [Serializable] internal sealed class GroundManifest { public float sector_m, half; public int count; public GroundSector[] sectors = Array.Empty<GroundSector>(); }
    [Serializable] internal sealed class GroundSector { public string id; public int[] sector; public float[] center; public int faces; }

    [Serializable] internal sealed class MapCatalog
    {
        public float[] world_min, world_max;
        public MapCategoryEntry[] categories = Array.Empty<MapCategoryEntry>();
        public MapPlaceEntry[] places = Array.Empty<MapPlaceEntry>();
    }
    [Serializable] internal sealed class MapCategoryEntry { public string id, group, label, color; }
    [Serializable] internal sealed class MapPlaceEntry { public string category, name; public float x, y; }

    [Serializable] internal sealed class City25Record { public bool complete; public string version, scene; public int objects, sectors, places; }
}
