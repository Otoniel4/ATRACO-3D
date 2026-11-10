using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;

namespace Alarma.City.Editor
{
    // Personal de los locales: coloca a cada empleado en su puesto (de pie o sentado) y lo viste con el uniforme del local.
    // Los cajeros que atienden las cajas («caja» y «cajero») los crea City25Shops; aquí solo reciben su uniforme.
    internal sealed class City25Staff
    {
        public const string CashierRole = "caja";
        // Cajeros de las cajas extra (supermercado, banco): los crea City25Shops con su caja, fila y mostrador.
        public const string LaneCashierRole = "cajero";
        private readonly Dictionary<string, UniformModel> slots;
        private readonly Dictionary<string, Material> uniforms;

        private City25Staff(Dictionary<string, UniformModel> wardrobe, Dictionary<string, Material> materials)
        {
            slots = wardrobe;
            uniforms = materials;
        }

        public static City25Staff Load(IEnumerable<ShopLayout> layouts)
        {
            var data = JsonUtility.FromJson<UniformSlots>(File.ReadAllText(City25Paths.Cast + "/staff_uniform_slots.json"));
            var names = new HashSet<string>(layouts.SelectMany(l => l.staff ?? Array.Empty<StaffPost>())
                .SelectMany(p => new[] { p.top, p.bottom }).Where(n => !string.IsNullOrEmpty(n)), StringComparer.OrdinalIgnoreCase);
            var materials = names.Count == 0 ? new Dictionary<string, Material>(StringComparer.OrdinalIgnoreCase)
                : FlatMaterialLibrary.Create(City25Paths.Kit, City25Paths.ColorManifests, names);
            var missing = names.Where(n => !materials.ContainsKey(n)).ToArray();
            if (missing.Length > 0) throw new InvalidOperationException("Faltan colores de uniforme en shop_materials.json: " + string.Join(", ", missing));
            return new City25Staff(data.models.ToDictionary(m => m.model), materials);
        }

        // Empleados del local salvo el cajero. Devuelve cuántos colocó.
        public int Place(Transform shop, Transform root, ShopLayout layout, PedestrianActor[] civilians, int index)
        {
            int placed = 0;
            for (int k = 0; k < layout.staff.Length; k++)
            {
                var post = layout.staff[k];
                if (post.role == CashierRole || post.role == LaneCashierRole) continue;
                // Paso 3 sobre diez civiles: dentro de un local no se repite la misma persona.
                var prefab = civilians[(index * 3 + 4 + k * 3) % civilians.Length];
                var person = UnityEngine.Object.Instantiate(prefab, root);
                person.name = Capitalized(post.role) + "_" + prefab.name;
                person.enabled = false;
                person.GetComponent<UnityEngine.AI.NavMeshAgent>().enabled = false;
                foreach (var t in person.GetComponentsInChildren<Transform>(true))
                    if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
                Quaternion facing = shop.rotation * Quaternion.Euler(0f, post.yaw, 0f);
                person.transform.SetPositionAndRotation(shop.TransformPoint(new Vector3(post.x, .1f, post.z)), facing);
                if (post.pose == "seat") Sit(person.gameObject, root, shop.TransformPoint(new Vector3(post.x, post.seat, post.z)), facing);
                else if (post.pose != "stand") throw new InvalidOperationException($"{shop.name}: pose de empleado desconocida «{post.pose}».");
                Dress(person.gameObject, prefab.name, post);
                AddWork(person.gameObject, post.role, shop.TransformPoint(new Vector3(post.x, .1f, post.z)), facing, post.pose == "seat");
                placed++;
            }
            return placed;
        }

        // Cómo trabaja cada rol entre clientes: puntos de la mano respecto de sus pies (lado, altura, frente),
        // duración del gesto, pausa mínima y máxima y si usa el gesto de manipular del Animator.
        private sealed class WorkProfile
        {
            public Vector3[] Points; public float Reach, RestMin, RestMax; public bool Gesture;
        }
        private static readonly WorkProfile Typing = new WorkProfile { Points = new[] { new Vector3(-.12f, 1.02f, .45f), new Vector3(.12f, 1.02f, .45f) }, Reach = 1.4f, RestMin = .5f, RestMax = 2.5f };
        private static readonly WorkProfile Cooking = new WorkProfile { Points = new[] { new Vector3(-.35f, .97f, .55f), new Vector3(.05f, .97f, .6f), new Vector3(.35f, 1.1f, .5f) }, Reach = 1.6f, RestMin = .8f, RestMax = 2.5f, Gesture = true };
        private static readonly WorkProfile Restocking = new WorkProfile { Points = new[] { new Vector3(-.2f, 1.35f, .55f), new Vector3(.2f, .8f, .55f), new Vector3(0f, 1.6f, .5f) }, Reach = 1.4f, RestMin = .5f, RestMax = 1.8f, Gesture = true };
        private static readonly WorkProfile Attending = new WorkProfile { Points = new[] { new Vector3(.05f, 1.05f, .45f) }, Reach = 1.2f, RestMin = 4f, RestMax = 9f, Gesture = true };
        private static readonly Dictionary<string, WorkProfile> Profiles = new Dictionary<string, WorkProfile>
        {
            ["caja"] = Typing, ["cajero"] = Typing, ["recepcion"] = Typing, ["asesor"] = Typing, ["gerente"] = Typing,
            ["cocinero"] = Cooking, ["cocinera"] = Cooking, ["carnicero"] = Cooking, ["panadera"] = Cooking,
            ["reponedor"] = Restocking,
            ["vendedor"] = Attending, ["vendedora"] = Attending, ["asesora"] = Attending, ["probadores"] = Attending, ["mesero"] = Attending,
        };

        // Agrega el brazo con alcance y la rutina de trabajo del rol. Sentado, las manos quedan a la altura del escritorio.
        public static StaffWork AddWork(GameObject person, string role, Vector3 feet, Quaternion facing, bool seated)
        {
            if (!Profiles.TryGetValue(role, out var profile)) throw new InvalidOperationException("Rol de empleado sin rutina de trabajo: " + role);
            var grip = person.GetComponentsInChildren<Transform>(true).First(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal));
            var reach = person.GetComponent<PedestrianReach>() ?? person.AddComponent<PedestrianReach>();
            reach.Configure(grip);
            var points = new Transform[profile.Points.Length];
            for (int i = 0; i < points.Length; i++)
            {
                Vector3 local = profile.Points[i];
                if (seated) local.y -= .24f;
                points[i] = new GameObject("Trabajo_" + i).transform;
                points[i].SetParent(person.transform, false);
                points[i].position = feet + facing * local;
            }
            var work = person.AddComponent<StaffWork>();
            work.Configure(points, reach, person.GetComponentInChildren<Animator>(), profile.Gesture && !seated, profile.Reach, profile.RestMin, profile.RestMax);
            return work;
        }

        // Uniforme del cajero si el local lo define.
        public void DressCashier(GameObject cashier, string model, ShopLayout layout)
        {
            var post = layout.staff.FirstOrDefault(p => p.role == CashierRole);
            if (post != null) Dress(cashier, model, post);
        }

        // Uniforme de un puesto concreto (cajeros de las cajas extra).
        public void DressPost(GameObject person, string model, StaffPost post) => Dress(person, model, post);

        private void Dress(GameObject person, string model, StaffPost post)
        {
            if (!slots.TryGetValue(model, out var garments)) throw new InvalidOperationException("Sin prendas clasificadas para " + model);
            foreach (var renderer in person.GetComponentsInChildren<Renderer>(true))
            {
                var shared = renderer.sharedMaterials;
                bool changed = false;
                for (int i = 0; i < shared.Length; i++)
                {
                    if (shared[i] == null) continue;
                    string name = shared[i].name;
                    if (garments.top.Contains(name)) { shared[i] = uniforms[post.top]; changed = true; }
                    else if (garments.bottom.Contains(name)) { shared[i] = uniforms[post.bottom]; changed = true; }
                }
                if (changed) renderer.sharedMaterials = shared;
            }
        }

        // Pose fija sentada en la silla del puesto: sin Animator, con la misma regla de huesos que los conductores.
        private static void Sit(GameObject person, Transform root, Vector3 seatPoint, Quaternion facing)
        {
            person.GetComponentInChildren<Animator>().enabled = false;
            var seat = new GameObject("Asiento").transform;
            seat.SetParent(root, false);
            seat.SetPositionAndRotation(seatPoint, facing);
            try { SeatedPose.Apply(person.transform, seat, seat, true); }
            finally { UnityEngine.Object.DestroyImmediate(seat.gameObject); }
            foreach (var skin in person.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                skin.localBounds = new Bounds(skin.localBounds.center, skin.localBounds.size + Vector3.one);
        }

        private static string Capitalized(string role) => string.IsNullOrEmpty(role) ? "Empleado" : char.ToUpperInvariant(role[0]) + role.Substring(1);
    }
}
