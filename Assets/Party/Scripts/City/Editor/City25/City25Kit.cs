using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
using Alarma.City.Playtest;
using Alarma.Traffic;
using Alarma.Vehicles;

namespace Alarma.City.Editor
{
    // Importa el kit y el suelo, les asigna materiales planos y crea un prefab con colisión por pieza del kit.
    // Todo vive en Art/City (arte versionado) y se actualiza sin cambiar GUID, así que repetirlo es rápido.
    internal static class City25Kit
    {
        private const string Prefabs = City25Paths.Kit + "/Prefabs";
        // Autos del proyecto (ruedas y puertas separadas); ya traen sus materiales de paleta.
        public static readonly string[] Cars = { "Car_Sedan", "Car_Hatchback", "Car_SUV", "Car_Pickup", "Car_Van", "Car_Coupe", "Car_Taxi" };
        private const string Palette = "Assets/Party/Data/CarPalette.asset";
        // Taxi y patrulla conservan sus colores: el resto recibe una pintura al azar.
        private static readonly string[] FixedLivery = { "Car_Taxi", "Car_Police" };

        // Kit del mundo R9 (export_kit.py), de calle (build_street_kit.py) y de barrios y lugares (build_district_kit.py) en un solo catálogo.
        public static readonly string[] Manifests = { "/kit.json", "/street_kit.json", "/district_kit.json" };

        public static KitManifest Manifest()
            => new KitManifest { pieces = Manifests.SelectMany(m => City25Paths.Read<KitManifest>(City25Paths.Kit + m).pieces).ToArray() };

        public static Dictionary<string, GameObject> Prepare(KitManifest kit)
        {
            string[] pieces = Directory.GetFiles(City25Paths.Kit, "*.fbx", SearchOption.AllDirectories).Select(p => p.Replace('\\', '/')).ToArray();
            string[] ground = Directory.GetFiles(City25Paths.Ground, "*.fbx").Select(p => p.Replace('\\', '/')).ToArray();
            if (pieces.Length != kit.pieces.Length) throw new InvalidOperationException($"El kit tiene {pieces.Length} FBX y kit.json describe {kit.pieces.Length}.");
            foreach (string path in pieces) Configure(path, false);
            foreach (string path in ground) Configure(path, true);
            string[] cars = Cars.Select(id => City25Paths.Vehicles + "/" + id + ".fbx").ToArray();
            foreach (string path in cars) Configure(path, false);
            string[] shops = Directory.GetFiles(City25Paths.Shops, "*.fbx").Select(p => p.Replace('\\', '/')).ToArray();
            foreach (string path in shops) Configure(path, false);
            var models = pieces.Concat(ground).Concat(cars).Concat(shops).ToArray();
            var names = FlatMaterialLibrary.UsedNames(models);
            var materials = FlatMaterialLibrary.Create(City25Paths.Kit, City25Paths.ColorManifests, names);
            var missing = names.Where(n => !materials.ContainsKey(n)).ToArray();
            if (missing.Length > 0) Debug.LogWarning("Ciudad 2 km: materiales sin color en los manifiestos (se usa el color del FBX): " + string.Join(", ", missing));
            FlatMaterialLibrary.Remap(models, materials, "Ciudad 2 km");
            FlatMaterialLibrary.EnsureFolder(Prefabs);
            var lamps = LampMaterials();
            var prefabs = new Dictionary<string, GameObject>(StringComparer.Ordinal);
            foreach (var piece in kit.pieces)
            {
                string model = pieces.FirstOrDefault(p => Path.GetFileNameWithoutExtension(p) == piece.id) ?? throw new FileNotFoundException("Falta la pieza del kit", piece.id);
                prefabs[piece.id] = MakePrefab(piece, model, lamps);
            }
            var palette = CarColors();
            foreach (string id in Cars) prefabs[id] = MakeParked(id, palette);
            foreach (string path in shops) prefabs[Path.GetFileNameWithoutExtension(path)] = MakeShop(path);
            return prefabs;
        }

        // Local con interior: colisión de malla en la estructura y los muebles, y la puerta de dos hojas lista para abrirse.
        private static GameObject MakeShop(string path)
        {
            string id = Path.GetFileNameWithoutExtension(path);
            var root = new GameObject(id);
            try
            {
                var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));
                model.transform.SetParent(root.transform, false);
                Transform left = Part(root, "DoorLeaf_L"), right = Part(root, "DoorLeaf_R");
                // Puertas extra de un lugar (portón peatonal y portón corredizo del escondite): opcionales.
                Transform gate = Optional(root, "GateLeaf_L"), slide = Optional(root, "SlideGate");
                var moving = new[] { left, right, gate, slide }.Where(t => t != null).ToArray();
                foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
                {
                    string name = filter.name;
                    bool decoration = name.StartsWith("FloorTiles", StringComparison.Ordinal) || name.StartsWith("CeilingLight", StringComparison.Ordinal)
                        || name.StartsWith("Aisle", StringComparison.Ordinal) || name.StartsWith("Sign", StringComparison.Ordinal) || name.StartsWith("Awning", StringComparison.Ordinal);
                    if (!decoration && !moving.Any(leaf => filter.transform.IsChildOf(leaf))) filter.gameObject.AddComponent<MeshCollider>();
                }
                foreach (var leaf in moving) LeafCollider(leaf);
                var gateway = new GameObject("Umbral").transform; gateway.SetParent(root.transform, false);
                gateway.position = (left.position + right.position) / 2f;
                root.AddComponent<ShopDoor>().Configure(left, right, gateway);
                if (gate != null) root.AddComponent<ShopDoor>().Configure(gate, null, Part(root, "Umbral_Porton"));
                if (slide != null)
                    root.AddComponent<ReviewSlidingDoor>().Configure(slide, Part(root, "Umbral_Auto"), Part(root, "SlideGate_Abierto").localPosition - slide.localPosition);
                FlatMaterialLibrary.EnsureFolder(City25Paths.Shops + "/Prefabs");
                return PrefabUtility.SaveAsPrefabAsset(root, City25Paths.Shops + "/Prefabs/" + id + ".prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Caja de colisión de una hoja de puerta, en el espacio de su bisagra para que gire con ella.
        private static void LeafCollider(Transform leaf)
        {
            var renderers = leaf.GetComponentsInChildren<Renderer>(true);
            var bounds = renderers[0].bounds; foreach (var r in renderers) bounds.Encapsulate(r.bounds);
            var box = leaf.gameObject.AddComponent<BoxCollider>();
            box.center = leaf.InverseTransformPoint(bounds.center);
            Vector3 size = leaf.InverseTransformVector(bounds.size);
            box.size = new Vector3(Mathf.Abs(size.x), Mathf.Abs(size.y), Mathf.Abs(size.z));
        }

        public static GameObject CarModel(string id) => AssetDatabase.LoadAssetAtPath<GameObject>(City25Paths.Vehicles + "/" + id + ".fbx") ?? throw new FileNotFoundException("Falta el auto", id);

        // Auto estacionado: no se abre ni se mueve, así que sus ~120 piezas se juntan en una malla por material
        // (unas 20). Las luces y el tablero van apagados. Pintura fija según su posición. Se regenera con la ciudad.
        private static GameObject MakeParked(string id, CarPalette palette)
        {
            var root = new GameObject(id);
            try
            {
                var model = (GameObject)PrefabUtility.InstantiatePrefab(CarModel(id));
                model.transform.SetParent(root.transform, false);
                var bounds = Bounds(root);
                var groups = new Dictionary<Material, List<CombineInstance>>();
                foreach (var renderer in model.GetComponentsInChildren<MeshRenderer>(true))
                {
                    var filter = renderer.GetComponent<MeshFilter>();
                    if (filter == null || filter.sharedMesh == null) continue;
                    var mesh = filter.sharedMesh;
                    var materials = renderer.sharedMaterials;
                    for (int i = 0; i < Mathf.Min(mesh.subMeshCount, materials.Length); i++)
                    {
                        if (materials[i] == null) continue;
                        if (!groups.TryGetValue(materials[i], out var parts)) groups[materials[i]] = parts = new List<CombineInstance>();
                        parts.Add(new CombineInstance { mesh = mesh, subMeshIndex = i, transform = root.transform.worldToLocalMatrix * renderer.transform.localToWorldMatrix });
                    }
                }
                UnityEngine.Object.DestroyImmediate(model);
                foreach (var group in groups)
                {
                    var combined = new Mesh { name = id + "_" + group.Key.name, indexFormat = IndexFormat.UInt32 };
                    combined.CombineMeshes(group.Value.ToArray(), true, true);
                    AssetDatabase.CreateAsset(combined, City25Paths.Output + "/Art/" + combined.name + ".asset");
                    var part = new GameObject(group.Key.name);
                    part.transform.SetParent(root.transform, false);
                    part.AddComponent<MeshFilter>().sharedMesh = combined;
                    part.AddComponent<MeshRenderer>().sharedMaterial = LightsOff(group.Key);
                }
                var box = root.AddComponent<BoxCollider>(); box.center = bounds.center; box.size = bounds.size;
                root.AddComponent<CarAppearance>().Configure(palette, false, PaintRenderers(root, id), null);
                return PrefabUtility.SaveAsPrefabAsset(root, City25Paths.Output + "/Prefabs/" + id + "_Estacionado.prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Copia sin emisión de los materiales que brillan (faros, pilotos, intermitentes, pantallas): un auto estacionado está apagado.
        private static Material LightsOff(Material material)
        {
            if (!material.IsKeywordEnabled("_EMISSION")) return material;
            string path = City25Paths.Output + "/Materials/" + material.name + "_Apagado.mat";
            var off = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (off != null) return off;
            off = new Material(material) { name = material.name + "_Apagado" };
            off.DisableKeyword("_EMISSION");
            off.SetColor("_EmissionColor", Color.black);
            off.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            AssetDatabase.CreateAsset(off, path);
            return off;
        }

        // Blender exige nombres únicos en todo el archivo: desde el segundo auto las piezas llegan como «Seat_Driver.001».
        public static Transform Part(GameObject root, string name)
            => root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name || t.name.StartsWith(name + ".", StringComparison.Ordinal))
               ?? throw new InvalidOperationException($"{root.name}: falta la pieza {name} en el modelo del auto.");

        private static Transform Optional(GameObject root, string name)
            => root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name || t.name.StartsWith(name + ".", StringComparison.Ordinal));

        public static Renderer[] PaintRenderers(GameObject root, string id)
            => FixedLivery.Contains(id) ? Array.Empty<Renderer>() : WithMaterial(root.transform, "Alarma_Paint_");

        public static Renderer[] WithMaterial(Transform root, string prefix)
            => root.GetComponentsInChildren<Renderer>(true).Where(r => r.sharedMaterial != null && r.sharedMaterial.name.StartsWith(prefix, StringComparison.Ordinal)).ToArray();

        // Paleta editable en Party/Data: colores de pintura y de las personas dentro de los autos.
        private static CarPalette CarColors()
        {
            var palette = AssetDatabase.LoadAssetAtPath<CarPalette>(Palette);
            if (palette != null) return palette;
            palette = ScriptableObject.CreateInstance<CarPalette>();
            Color[] Hex(params string[] values) => values.Select(v => ColorUtility.TryParseHtmlString("#" + v, out Color c) ? c : Color.white).ToArray();
            palette.Configure(Hex("D9534A", "2F9C8F", "4F5D6B", "A33B32", "ECECE6", "2D5FD0", "1E252C", "C9D2D6", "E6BB55", "579267", "8E5BB0", "F08A3C", "3E6FB0", "6B4F3A"));
            AssetDatabase.CreateAsset(palette, Palette);
            return palette;
        }

        public static Bounds Bounds(GameObject root)
        {
            var renderers = root.GetComponentsInChildren<Renderer>(true);
            var bounds = renderers[0].bounds; foreach (var r in renderers) bounds.Encapsulate(r.bounds);
            return bounds;
        }

        private static void Configure(string path, bool collider)
        {
            var importer = (ModelImporter)AssetImporter.GetAtPath(path) ?? throw new InvalidOperationException("No se importó " + path);
            // Colores planos sin mapas de normales ni animaciones; el suelo genera su propia colisión de malla.
            bool ready = !importer.importAnimation && importer.importTangents == ModelImporterTangents.None && importer.addCollider == collider
                && !importer.importCameras && !importer.importLights && Mathf.Approximately(importer.globalScale, 1f);
            if (ready) return;
            importer.importAnimation = false; importer.importTangents = ModelImporterTangents.None; importer.addCollider = collider;
            importer.importCameras = false; importer.importLights = false; importer.globalScale = 1f;
            importer.SaveAndReimport();
        }

        private static GameObject MakePrefab(KitPiece piece, string modelPath, Material[] lamps)
        {
            var root = new GameObject(piece.id);
            try
            {
                var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(modelPath));
                model.transform.SetParent(root.transform, false);
                var renderers = model.GetComponentsInChildren<Renderer>(true);
                var bounds = renderers[0].bounds; foreach (var r in renderers) bounds.Encapsulate(r.bounds);
                // El kit sale de Blender con el ancho en X y el fondo en Z: si no coincide, los ejes cambiaron y la ciudad quedaría girada.
                if (piece.group == "building" && (Mathf.Abs(bounds.size.x - piece.width) > .3f || Mathf.Abs(bounds.size.z - piece.depth) > .3f))
                    throw new InvalidOperationException($"{piece.id}: medidas {bounds.size} distintas de kit.json ({piece.width} × {piece.depth}).");
                AddCollider(root, piece, bounds);
                if (piece.kind == "signal") AddLamps(root, lamps);
                return PrefabUtility.SaveAsPrefabAsset(root, Prefabs + "/" + piece.id + ".prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Luces encendibles sobre las lentes del modelo (rojo arriba, verde abajo), mirando a los autos que llegan (+Z).
        private static void AddLamps(GameObject root, Material[] lamps)
        {
            var renderers = new Renderer[3];
            float[] heights = { 5.02f, 4.72f, 4.42f };
            for (int i = 0; i < 3; i++)
            {
                var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
                UnityEngine.Object.DestroyImmediate(quad.GetComponent<Collider>());
                quad.name = new[] { "Luz roja", "Luz amarilla", "Luz verde" }[i];
                quad.transform.SetParent(root.transform, false);
                quad.transform.SetLocalPositionAndRotation(new Vector3(0f, heights[i], 1.17f), Quaternion.Euler(0f, 180f, 0f));
                quad.transform.localScale = Vector3.one * .24f;
                renderers[i] = quad.GetComponent<Renderer>(); renderers[i].sharedMaterial = lamps[0];
                renderers[i].shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            }
            root.AddComponent<TrafficLightHead>().ConfigureLamps(renderers[0], renderers[1], renderers[2], lamps[0], lamps[1], lamps[2], lamps[3]);
        }

        // Apagada, roja, amarilla y verde; sin iluminación para que brillen de día.
        private static Material[] LampMaterials()
        {
            var shader = Shader.Find("Universal Render Pipeline/Unlit") ?? throw new InvalidOperationException("No se encontró URP/Unlit.");
            var colors = new[] { ("Off", new Color(.1f, .1f, .11f)), ("Red", new Color(1f, .12f, .08f)), ("Yellow", new Color(1f, .72f, .08f)), ("Green", new Color(.15f, 1f, .4f)) };
            return colors.Select(c =>
            {
                string path = City25Paths.Kit + "/Materials/Signal_Lamp_" + c.Item1 + ".mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null) { m = new Material(shader) { name = "Signal_Lamp_" + c.Item1 }; AssetDatabase.CreateAsset(m, path); }
                m.shader = shader; m.enableInstancing = true; m.SetColor("_BaseColor", c.Item2); EditorUtility.SetDirty(m);
                return m;
            }).ToArray();
        }

        private static void AddCollider(GameObject root, KitPiece piece, Bounds bounds)
        {
            switch (piece.kind)
            {
                case "tree":
                    var trunk = root.AddComponent<CapsuleCollider>(); trunk.center = new Vector3(0f, 2f, 0f); trunk.radius = .35f; trunk.height = 4f;
                    break;
                case "lamp":
                case "signal":
                    // El poste está detrás del centro; el brazo cuelga hacia +Z sobre la calzada.
                    var pole = root.AddComponent<BoxCollider>(); pole.center = new Vector3(0f, bounds.size.y / 2f, bounds.min.z + .15f); pole.size = new Vector3(.3f, bounds.size.y, .3f);
                    break;
                case "playground":
                case "basketballcourt":
                    break; // se puede caminar por encima
                case "busstop":
                case "kiosk":
                case "billboard":
                case "yard":
                case "yardsign":
                case "gasstation":
                case "parking":
                case "forklift":
                case "junk":
                    // Colisión con la forma real: se entra bajo el techo de la parada y de la gasolinera, por el portón
                    // del antejardín, entre los pilares de un cartel o entre las islas de surtidores.
                    foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true)) filter.gameObject.AddComponent<MeshCollider>();
                    break;
                case "stopsign":
                case "yieldsign":
                case "speedsign":
                    var post = root.AddComponent<BoxCollider>(); post.center = new Vector3(bounds.center.x, bounds.size.y / 2f, bounds.center.z); post.size = new Vector3(.15f, bounds.size.y, .15f);
                    break;
                case "bollards":
                    foreach (float x in new[] { -1.2f, 0f, 1.2f })
                    {
                        var bollard = root.AddComponent<BoxCollider>(); bollard.center = new Vector3(bounds.center.x + x, bounds.size.y / 2f, bounds.center.z); bollard.size = new Vector3(.2f, bounds.size.y, .2f);
                    }
                    break;
                default:
                    var box = root.AddComponent<BoxCollider>(); box.center = bounds.center; box.size = bounds.size;
                    break;
            }
        }
    }
}
