using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace Alarma.City.Editor
{
    // Coloca el suelo por sectores y un prefab por cada objeto del plano, agrupados por sector para activarlos según la distancia.
    internal static class City25World
    {
        public sealed class Result
        {
            public GameObject Root;
            public CitySectorStreamer.Sector[] Sectors;
            public List<GameObject> Ground = new List<GameObject>();
            public List<(CityObject data, GameObject instance)> Places = new List<(CityObject, GameObject)>();
            public List<(CityObject data, GameObject instance)> Signals = new List<(CityObject, GameObject)>();
            public int Placed;
        }

        // Lotes y alcantarillas ya forman parte del suelo exportado desde Blender.
        private static readonly HashSet<string> GroundOnly = new HashSet<string>(StringComparer.Ordinal) { "Lot", "Sewer" };

        public static Result Build(IReadOnlyDictionary<string, GameObject> prefabs, CityObjects city, GroundManifest ground)
        {
            var result = new Result { Root = new GameObject("Ciudad 2 km") };
            var soil = new GameObject("Suelo"); soil.transform.SetParent(result.Root.transform, false);
            foreach (var sector in ground.sectors)
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(City25Paths.Ground + "/" + sector.id + ".fbx") ?? throw new InvalidOperationException("Falta el suelo " + sector.id);
                // Blender exporta con -Y al frente: la malla del suelo queda media vuelta girada respecto del plano y el contenedor la endereza.
                var holder = new GameObject(sector.id); holder.transform.SetParent(soil.transform, false);
                holder.transform.SetPositionAndRotation(City25Paths.World(sector.center[0], sector.center[1]), Quaternion.Euler(0f, 180f, 0f));
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, holder.transform);
                result.Ground.Add(instance);
            }
            var content = new GameObject("Edificios y mobiliario"); content.transform.SetParent(result.Root.transform, false);
            int count = ground.count; float size = ground.sector_m, half = ground.half;
            var roots = new GameObject[count, count]; var sectors = new List<CitySectorStreamer.Sector>();
            for (int i = 0; i < count; i++)
                for (int j = 0; j < count; j++)
                {
                    roots[i, j] = new GameObject($"Sector {i}_{j}"); roots[i, j].transform.SetParent(content.transform, false);
                    sectors.Add(new CitySectorStreamer.Sector { Root = roots[i, j], Min = new Vector2(-half + i * size, -half + j * size), Max = new Vector2(-half + (i + 1) * size, -half + (j + 1) * size) });
                }
            result.Sectors = sectors.ToArray();
            var objects = city.objects;
            for (int n = 0; n < objects.Length; n++)
            {
                var o = objects[n];
                if (n % 250 == 0 && EditorUtility.DisplayCancelableProgressBar("Ciudad 2 km", $"Colocando objetos {n}/{objects.Length}", .55f + .3f * n / objects.Length)) throw new OperationCanceledException();
                if (GroundOnly.Contains(o.kit)) continue;
                if (!prefabs.TryGetValue(o.kit, out var prefab)) throw new InvalidOperationException("El plano usa una pieza que no está en el kit: " + o.kit);
                // Los locales con interior propio reemplazan al edificio del kit en el mismo lugar.
                if (o.HasPlace && prefabs.TryGetValue("Local_" + char.ToUpperInvariant(o.place.kind[0]) + o.place.kind.Substring(1), out var local)) prefab = local;
                var parent = roots[Mathf.Clamp(o.sector[0], 0, count - 1), Mathf.Clamp(o.sector[1], 0, count - 1)];
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent.transform);
                instance.transform.SetPositionAndRotation(City25Paths.World(o.x, o.y), Quaternion.Euler(0f, o.yaw, 0f));
                if (o.HasPlace) { instance.name = o.place.name + " (" + o.kit + ")"; result.Places.Add((o, instance)); }
                if (o.signal >= 0) result.Signals.Add((o, instance));
                result.Placed++;
            }
            return result;
        }
    }
}
