using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.Street;

namespace Alarma.City.Editor
{
    // Locales con interior: a cada local con modelo propio le arma la rutina de compra con el sistema de CityLifeR5
    // (puntos, cuadrícula interior, ajustes de tienda y cajero). El resto del personal lo pone City25Staff; los clientes, SidewalkPopulation.
    internal static class City25Shops
    {
        private const float Step = .5f, Clearance = .3f, BodyRadius = .23f;

        public static (ShopActivity[] shops, ShopDoor[] doors) Build(string folder, City25World.Result world, ShopLayouts layouts, PedestrianActor[] civilians)
        {
            var shops = new List<ShopActivity>(); var doors = new List<ShopDoor>();
            Physics.SyncTransforms();
            var staff = City25Staff.Load(layouts.shops);
            int index = 0, employees = 0;
            foreach (var (data, instance) in world.Places)
            {
                var layout = layouts.shops.FirstOrDefault(l => l.kind == data.place.kind);
                var door = instance.GetComponent<ShopDoor>();
                if (layout == null || door == null) continue;
                if (layout.kind == "banco") OpenServiceGap(instance.transform);
                var activity = Activity(folder, data, instance.transform, layout, door, civilians, index, staff);
                employees += staff.Place(instance.transform, activity.transform, layout, civilians, index++);
                shops.Add(activity);
                doors.Add(door);
            }
            Debug.Log($"Personal de locales: {shops.Sum(s => s.CheckoutCount)} cajas atendidas y {employees} empleados más en sus puestos.");
            return (shops.ToArray(), doors.ToArray());
        }

        private static ShopActivity Activity(string folder, CityObject data, Transform shop, ShopLayout layout, ShopDoor door, PedestrianActor[] civilians, int index, City25Staff team)
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
            if (layout.kind == "joyeria")
                foreach (var product in products)
                {
                    Vector3 point = shop.InverseTransformPoint(product.position);
                    point.y = 1.344f; // La pieza manipulable está sobre el cristal, no dentro de la vitrina cerrada.
                    product.position = shop.TransformPoint(point);
                }
            var tasks = ScriptableObject.CreateInstance<ShopTaskSettings>();
            tasks.ShopId = id; tasks.ProductName = layout.product_name; tasks.PriceCents = layout.price_cents; tasks.CustomerWalletCents = Math.Max(200000, layout.price_cents * 3); tasks.InitialStock = 500;
            tasks.IsWithdrawal = layout.kind == "banco";
            tasks.Animation = AssetDatabase.LoadAssetAtPath<ShopAnimationProfile>("Assets/Party/Data/ShopAnimations/" + layout.kind + ".asset")
                ?? throw new InvalidOperationException("Falta el perfil de atención de " + layout.kind);
            if (tasks.IsWithdrawal) tasks.ProductName = "Retiro de efectivo";
            tasks.ProductPrefab = Prop(layout.product); tasks.MoneyPrefab = Prop("CashStack"); tasks.ReceiptPrefab = Receipt(folder);
            AssetDatabase.CreateAsset(tasks, folder + "/Data/Shop_" + index + ".asset");
            activity.Configure(walk, entry, browse, queue, exit, products, Marker(root, shop, "Counter", Stand(tasks.Animation, true), graph), Free("Scan", layout.scan, 3), Free("Receipt", layout.receipt, 3), Free("Till", layout.till, 3), tasks);
            if (!tasks.IsWithdrawal) root.gameObject.AddComponent<ShopStockDisplay>();
            // Cajero de la caja principal: un civil del elenco detrás del mostrador mirando hacia el escáner.
            int variant = (index * 3 + 4) % civilians.Length;
            var cashier = Cashier(root, shop, civilians[variant], shop.TransformPoint(Stand(tasks.Animation, false)), shop.TransformPoint(tasks.Animation.CounterCenter));
            activity.ConfigureStaff(variant, door, Grip(cashier));
            team.DressCashier(cashier.gameObject, civilians[variant].name, layout);
            // Cajas extra (supermercado, banco): una por cada puesto «cajero», con la caja principal trasladada hasta ese
            // puesto. Cada una tiene su fila, su mostrador y su cajero, y los clientes van a la que tiene menos gente.
            var extra = new List<CheckoutStation>();
            var extraCashiers = new List<PedestrianActor>();
            foreach (var (k, shift) in LaneOffsets(layout))
            {
                var post = layout.staff[k];
                var person = civilians[(index * 3 + 4 + k * 3) % civilians.Length];
                Vector3 offset = new Vector3(shift.x, 0f, shift.y);
                int lane = extra.Count + 1;
                CheckoutStation station;
                int before = root.childCount;
                try
                {
                    station = new CheckoutStation
                    {
                        queue = Points(layout.queue, 2).Select((v, i) => Marker(root, shop, $"Queue{lane}_{i}", v + offset, graph)).ToArray(),
                        counter = Marker(root, shop, $"Counter{lane}", Stand(tasks.Animation, true) + offset, graph),
                        scan = Marker(root, shop, $"Scan{lane}", Points(layout.scan, 3)[0] + offset, null),
                        receipt = Marker(root, shop, $"Receipt{lane}", Points(layout.receipt, 3)[0] + offset, null),
                        till = Marker(root, shop, $"Till{lane}", Points(layout.till, 3)[0] + offset, null),
                    };
                }
                catch (InvalidOperationException problem)
                {
                    // Sin lugar para su fila: el cajero queda en su puesto, quieto, y el local atiende con las demás cajas.
                    Debug.LogWarning($"{shop.name}: la caja del puesto {k} no se habilitó ({problem.Message}).");
                    for (int c = root.childCount - 1; c >= before; c--) UnityEngine.Object.DestroyImmediate(root.GetChild(c).gameObject);
                    var idle = Cashier(root, shop, person, shop.TransformPoint(new Vector3(post.x, .1f, post.z)), shop.TransformPoint(Points(layout.scan, 3)[0] + offset));
                    team.DressPost(idle.gameObject, person.name, post);
                    continue;
                }
                var lanePerson = Cashier(root, shop, person, shop.TransformPoint(Stand(tasks.Animation, false) + offset), shop.TransformPoint(tasks.Animation.CounterCenter + offset));
                station.cashierGrip = Grip(lanePerson);
                team.DressPost(lanePerson.gameObject, person.name, post);
                extra.Add(station);
                extraCashiers.Add(lanePerson);
            }
            activity.ConfigureCheckouts(extra.ToArray());
            for (int lane = 0; lane < activity.CheckoutCount; lane++)
            {
                var station = activity.Checkout(lane);
                Vector3 offset = shop.InverseTransformPoint(station.scan.position) - Points(layout.scan, 3)[0];
                var workspace = Marker(root, shop, "Contacto_Caja_" + lane, tasks.Animation.CounterCenter + offset, null);
                workspace.rotation = Quaternion.LookRotation(shop.TransformDirection(tasks.Animation.CounterNormal));
                activity.ConfigureWorkspace(lane, workspace);
                station.scan.position = workspace.position;
                station.Till.position = workspace.position - workspace.forward * .25f + workspace.right * .055f + Vector3.up * .10f;
            }

            // Cada cajero se mueve solo mientras atiende a un cliente de su caja; sin cliente espera quieto.
            cashier.gameObject.AddComponent<CashierPresentation>().Configure(activity, cashier.GetComponentInChildren<Animator>(), 0);
            for (int lane = 0; lane < extraCashiers.Count; lane++)
                extraCashiers[lane].gameObject.AddComponent<CashierPresentation>().Configure(activity, extraCashiers[lane].GetComponentInChildren<Animator>(), lane + 1);
            return activity;
        }

        // Un civil del elenco como cajero, de pie en su puesto y mirando hacia el escáner.
        private static PedestrianActor Cashier(Transform root, Transform shop, PedestrianActor prefab, Vector3 spot, Vector3 scanner)
        {
            var person = UnityEngine.Object.Instantiate(prefab, root);
            person.name = "Cajero_" + prefab.name; person.enabled = false;
            person.GetComponent<UnityEngine.AI.NavMeshAgent>().enabled = false;
            foreach (var t in person.GetComponentsInChildren<Transform>(true))
                if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
            person.transform.SetPositionAndRotation(spot, Quaternion.LookRotation(Vector3.ProjectOnPlane(scanner - spot, Vector3.up)));
            return person;
        }

        private static Vector3 Stand(ShopAnimationProfile profile, bool customer)
        {
            Vector3 normal = profile.CounterNormal.normalized;
            Vector3 side = Vector3.Cross(Vector3.up, normal);
            Vector3 stand = profile.CounterCenter + (normal * (profile.CounterWidth * .5f + .255f) + side * .15f) * (customer ? 1f : -1f);
            stand.y = .1f;
            return stand;
        }

        // La ventanilla necesita espacio para el antebrazo; la bandeja atraviesa ese hueco.
        private static void OpenServiceGap(Transform shop)
        {
            foreach (var renderer in shop.GetComponentsInChildren<MeshRenderer>())
            {
                bool glass = renderer.name.StartsWith("TellerGlass", StringComparison.Ordinal);
                bool tray = renderer.name.StartsWith("TellerSlot", StringComparison.Ordinal);
                if (!glass && !tray) continue;
                var bounds = renderer.bounds;
                var pivot = new GameObject("Paso_Ventanilla_" + renderer.name).transform;
                pivot.SetParent(shop, false);
                pivot.position = glass ? new Vector3(bounds.center.x, bounds.max.y, bounds.center.z) : bounds.center;
                renderer.transform.SetParent(pivot, true);
                if (glass)
                    pivot.localScale = new Vector3(1f, (bounds.max.y - shop.TransformPoint(Vector3.up * 1.38f).y) / bounds.size.y, 1f);
                else
                {
                    pivot.localScale = new Vector3(1f, 1f, .65f / .3f);
                    pivot.position -= shop.forward * .27f;
                }
            }
            Physics.SyncTransforms();
        }

        private static Transform Grip(PedestrianActor person)
            => person.GetComponentsInChildren<Transform>(true).First(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal));

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
            // Pasillos de las cajas extra: entre cajas de cobro quedan pasillos de 0,9 m que la muestra cada 0,5 m no
            // alcanza. Se abren los casilleros de su fila y su mostrador si todos quedan a un radio de persona de los muebles.
            foreach (var (_, offset) in LaneOffsets(layout))
            {
                var path = Points(layout.queue, 2).Reverse().Append(Points(layout.counter, 2)[0]).Select(v => new Vector2(v.x + offset.x, v.z + offset.y)).ToArray();
                var carved = new List<Vector2Int>();
                bool clear = true;
                for (int i = 0; i + 1 < path.Length && clear; i++)
                {
                    int samples = Mathf.Max(1, Mathf.CeilToInt(Vector2.Distance(path[i], path[i + 1]) / (Step * .5f)));
                    for (int k = 0; k <= samples && clear; k++)
                    {
                        Vector2 p = Vector2.Lerp(path[i], path[i + 1], (float)k / samples);
                        var cell = new Vector2Int(Mathf.RoundToInt(p.x / Step), Mathf.RoundToInt(p.y / Step));
                        clear = Gap(cell.x * Step, cell.y * Step, blocks) >= BodyRadius;
                        carved.Add(cell);
                    }
                }
                if (clear) points.UnionWith(carved);
            }
            var list = points.ToList(); var lookup = list.Select((p, i) => (p, i)).ToDictionary(t => t.p, t => t.i);
            return list.Select(p => new TrafficCell
            {
                Position = FloorPoint(shop, p, layout.depth * .5f),
                Links = Neighbours(p).Where(lookup.ContainsKey).Select(n => lookup[n]).ToArray()
            }).ToArray();
        }

        // Puesto de cada cajero de caja extra («cajero») y cuánto se traslada la caja principal hasta él.
        private static IEnumerable<(int post, Vector2 offset)> LaneOffsets(ShopLayout layout)
        {
            for (int k = 0; k < layout.staff.Length; k++)
                if (layout.staff[k].role == City25Staff.LaneCashierRole)
                    yield return (k, new Vector2(layout.staff[k].x - layout.cashier[0], layout.staff[k].z - layout.cashier[1]));
        }

        // Distancia de un punto al mueble más cercano (cajas x0, z0, x1, z1).
        private static float Gap(float x, float z, float[][] blocks)
        {
            float best = float.PositiveInfinity;
            foreach (var b in blocks)
            {
                float dx = Mathf.Max(b[0] - x, 0f, x - b[2]), dz = Mathf.Max(b[1] - z, 0f, z - b[3]);
                best = Mathf.Min(best, Mathf.Sqrt(dx * dx + dz * dz));
            }
            return best;
        }

        private static Vector3 FloorPoint(Transform shop, Vector2Int cell, float frontage)
        {
            Vector3 point = shop.TransformPoint(new Vector3(cell.x * Step, .1f, cell.y * Step));
            return cell.y * Step > frontage && SidewalkClearance.TryGround(point, out Vector3 floor) ? floor : point;
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
