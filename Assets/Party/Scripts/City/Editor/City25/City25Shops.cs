using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;

namespace Alarma.City.Editor
{
    // Locales con interior: a cada local con modelo propio le arma la rutina de compra con el sistema de CityLifeR5
    // (puntos, cuadrícula interior, ajustes de tienda y cajero). Los compradores los pone CityPopulationDirector.
    internal static class City25Shops
    {
        private const float Step = .5f, Clearance = .3f;

        public static (ShopActivity[] shops, ShopDoor[] doors) Build(string folder, City25World.Result world, ShopLayouts layouts, PedestrianActor[] civilians)
        {
            var shops = new List<ShopActivity>(); var doors = new List<ShopDoor>();
            int index = 0;
            foreach (var (data, instance) in world.Places)
            {
                var layout = layouts.shops.FirstOrDefault(l => l.kind == data.place.kind);
                var door = instance.GetComponent<ShopDoor>();
                if (layout == null || door == null) continue;
                shops.Add(Activity(folder, data, instance.transform, layout, door, civilians, index++));
                doors.Add(door);
            }
            return (shops.ToArray(), doors.ToArray());
        }

        private static ShopActivity Activity(string folder, CityObject data, Transform shop, ShopLayout layout, ShopDoor door, PedestrianActor[] civilians, int index)
        {
            string id = data.place.name;
            var root = new GameObject("Rutina de compra").transform; root.SetParent(shop, false);
            var graph = ScriptableObject.CreateInstance<TrafficGraph>();
            graph.Cells = Cells(shop, layout);
            AssetDatabase.CreateAsset(graph, folder + "/Data/Traffic_" + index + ".asset");
            var traffic = root.gameObject.AddComponent<CityTrafficController>(); traffic.Configure(graph, .42f); // un paso de 0,5 m cada 0,42 s: unos 1,2 m/s, paso normal
            var activity = root.gameObject.AddComponent<ShopActivity>(); activity.ConfigureTraffic(traffic);
            Transform[] Snap(string name, float[] p) => Points(p, 2).Select((v, i) => Marker(root, shop, $"{name}_{i}", v, graph)).ToArray();
            Transform Free(string name, float[] p, int stride) => Marker(root, shop, name, Points(p, stride)[0], null);
            var walk = Snap("Walk", layout.sidewalk); var entry = Snap("Entry", layout.entry); var exit = Snap("Exit", layout.exit);
            var queue = Snap("Queue", layout.queue); var browse = Snap("Browse", layout.stations);
            var products = Points(layout.products, 3).Select((v, i) => Marker(root, shop, "Product_" + i, v, null)).ToArray();
            var tasks = ScriptableObject.CreateInstance<ShopTaskSettings>();
            tasks.ShopId = id; tasks.ProductName = layout.product_name; tasks.PriceCents = layout.price_cents; tasks.CustomerWalletCents = Math.Max(200000, layout.price_cents * 3); tasks.InitialStock = 500;
            tasks.ProductPrefab = Prop(layout.product); tasks.MoneyPrefab = Prop("CashStack"); tasks.ReceiptPrefab = Receipt(folder);
            AssetDatabase.CreateAsset(tasks, folder + "/Data/Shop_" + index + ".asset");
            activity.Configure(walk, entry, browse, queue, exit, products, Snap("Counter", layout.counter)[0], Free("Scan", layout.scan, 3), Free("Receipt", layout.receipt, 3), Free("Till", layout.till, 3), tasks);
            root.gameObject.AddComponent<ShopStockDisplay>();
            // Cajero: un civil del elenco detrás del mostrador mirando hacia la caja; no sale a comprar.
            int variant = (index * 3 + 4) % civilians.Length;
            var staff = UnityEngine.Object.Instantiate(civilians[variant], root);
            staff.name = "Cajero_" + civilians[variant].name; staff.enabled = false;
            staff.GetComponent<UnityEngine.AI.NavMeshAgent>().enabled = false;
            Vector3 till = activity.Scan.position, spot = shop.TransformPoint(Local(layout.cashier, .1f));
            staff.transform.SetPositionAndRotation(spot, Quaternion.LookRotation(Vector3.ProjectOnPlane(till - spot, Vector3.up)));
            var grip = staff.GetComponentsInChildren<Transform>(true).First(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal));
            activity.ConfigureStaff(variant, door, grip);
            staff.gameObject.AddComponent<CashierPresentation>().Configure(activity, staff.GetComponentInChildren<Animator>());
            return activity;
        }

        // Cuadrícula caminable: interior sin obstáculos, el paso de la puerta y una franja de acera enfrente.
        private static TrafficCell[] Cells(Transform shop, ShopLayout layout)
        {
            var points = new HashSet<Vector2Int>();
            float[] w = layout.walkable;
            var blocks = Enumerable.Range(0, layout.obstacles.Length / 4).Select(i => layout.obstacles.Skip(i * 4).Take(4).ToArray()).ToArray();
            void Area(float x0, float z0, float x1, float z1, bool interior)
            {
                for (float x = x0; x <= x1 + .01f; x += Step)
                    for (float z = z0; z <= z1 + .01f; z += Step)
                        if (!interior || !blocks.Any(b => x > b[0] - Clearance && x < b[2] + Clearance && z > b[1] - Clearance && z < b[3] + Clearance))
                            points.Add(new Vector2Int(Mathf.RoundToInt(x / Step), Mathf.RoundToInt(z / Step)));
            }
            Area(w[0], w[1], w[2], w[3], true);
            float side = layout.sidewalk[1];
            Area(-layout.door_width / 2 + .5f, w[3], layout.door_width / 2 - .5f, side, false);
            Area(Mathf.Min(layout.sidewalk[0], layout.sidewalk[2]), side - .5f, Mathf.Max(layout.sidewalk[0], layout.sidewalk[2]), side + .5f, false);
            var list = points.ToList(); var lookup = list.Select((p, i) => (p, i)).ToDictionary(t => t.p, t => t.i);
            return list.Select(p => new TrafficCell
            {
                Position = shop.TransformPoint(new Vector3(p.x * Step, .1f, p.y * Step)),
                Links = Neighbours(p).Where(lookup.ContainsKey).Select(n => lookup[n]).ToArray()
            }).ToArray();
        }

        private static IEnumerable<Vector2Int> Neighbours(Vector2Int p)
        {
            for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) if (dx != 0 || dz != 0) yield return new Vector2Int(p.x + dx, p.y + dz);
        }

        private static Vector3[] Points(float[] p, int stride)
            => Enumerable.Range(0, p.Length / stride).Select(i => stride == 3 ? new Vector3(p[i * 3], p[i * 3 + 2], p[i * 3 + 1]) : new Vector3(p[i * 2], .1f, p[i * 2 + 1])).ToArray();

        private static Vector3 Local(float[] p, float height) => new Vector3(p[0], height, p[1]);

        private static Transform Marker(Transform parent, Transform shop, string name, Vector3 local, TrafficGraph graph)
        {
            var marker = new GameObject(name).transform; marker.SetParent(parent, false);
            marker.position = shop.TransformPoint(local);
            if (graph == null) return marker;
            int cell = graph.Nearest(marker.position, .65f);
            if (cell < 0) throw new InvalidOperationException($"{shop.name}: el punto {name} quedó fuera del suelo caminable.");
            marker.position = graph.Cells[cell].Position;
            return marker;
        }

        private static GameObject Prop(string name)
            => AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Party/Art/Props/Prop_" + name + ".fbx") ?? throw new InvalidOperationException("Falta el prop " + name);

        // Boleta: un papel blanco pequeño que el cajero entrega.
        private static GameObject Receipt(string folder)
        {
            string path = folder + "/Prefabs/Boleta.prefab";
            var existing = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (existing != null) return existing;
            var paper = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                UnityEngine.Object.DestroyImmediate(paper.GetComponent<Collider>());
                paper.transform.localScale = new Vector3(.08f, .003f, .15f);
                return PrefabUtility.SaveAsPrefabAsset(paper, path);
            }
            finally { UnityEngine.Object.DestroyImmediate(paper); }
        }
    }
}
