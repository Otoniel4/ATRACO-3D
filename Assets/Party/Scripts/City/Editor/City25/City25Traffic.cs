using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.Traffic;
using Alarma.Vehicles;

namespace Alarma.City.Editor
{
    // Tráfico: red de carriles desde city_traffic.json y autos con conductor que comparten el reloj de los semáforos.
    internal static class City25Traffic
    {
        private const int VehicleLayer = 28;

        private const int DriversPerModel = 3; // cada modelo sale con varios conductores distintos

        public static TrafficPopulation Build(string folder, TrafficSignalNetwork signals, Transform observer, GameObject[] civilians)
        {
            var data = City25Paths.Read<CityTraffic>(City25Paths.Plan + "/city_traffic.json");
            var links = new List<(Vector2[], int[], int, int, int, float)>(data.links.Length);
            foreach (var l in data.links)
            {
                var path = new Vector2[l.points.Length / 2];
                for (int i = 0; i < path.Length; i++) path[i] = new Vector2(l.points[2 * i], l.points[2 * i + 1]);
                if (path.Length < 2 || l.next.Length == 0) throw new InvalidOperationException("Hay un carril sin recorrido o sin salida en city_traffic.json.");
                if (l.signal >= signals.Count) throw new InvalidOperationException("Un carril apunta a un semáforo que no existe.");
                links.Add((path, l.next, l.control, l.signal, l.axis, l.speed));
            }
            var network = ScriptableObject.CreateInstance<RoadNetwork>();
            network.Build(links);
            AssetDatabase.CreateAsset(network, folder + "/Data/RoadNetwork.asset");
            var cars = City25Kit.Cars.SelectMany((id, m) => Enumerable.Range(0, DriversPerModel).Select(v =>
                Car(folder, id, v, civilians[(m * DriversPerModel + v) % civilians.Length], civilians[(m * DriversPerModel + v + 5) % civilians.Length]))).ToArray();
            var population = new GameObject("Tráfico").AddComponent<TrafficPopulation>();
            population.Configure(network, signals, cars, observer);
            return population;
        }

        // Auto de tráfico: modelo, cuerpo cinemático en la capa de vehículos (28), conductor de tráfico y un civil al volante.
        private static TrafficCar Car(string folder, string id, int variant, GameObject driverModel, GameObject riderModel)
        {
            var root = new GameObject("Trafico_" + id + "_" + variant);
            try
            {
                var model = (GameObject)PrefabUtility.InstantiatePrefab(City25Kit.CarModel(id));
                model.transform.SetParent(root.transform, false);
                var bounds = City25Kit.Bounds(root);
                var box = root.AddComponent<BoxCollider>(); box.center = bounds.center; box.size = bounds.size;
                var rigidbody = root.AddComponent<Rigidbody>(); rigidbody.isKinematic = true; rigidbody.interpolation = RigidbodyInterpolation.None;
                foreach (var t in root.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = VehicleLayer;
                // Ejes Wheel_ si el FBX los trae; si no, las llantas Tire_, que tienen su centro en el eje.
                var parts = root.GetComponentsInChildren<Transform>(true);
                var wheels = parts.Where(t => t.name.StartsWith("Wheel_", StringComparison.Ordinal)).ToArray();
                if (wheels.Length != 4) wheels = parts.Where(t => t.name.StartsWith("Tire_", StringComparison.Ordinal)).ToArray();
                if (wheels.Length != 4) throw new InvalidOperationException($"{id} tiene {wheels.Length} ruedas; se esperaban 4 (Wheel_ o Tire_).");
                // Radio real de la rueda para que gire a la velocidad justa.
                float radius = wheels[0].GetComponentsInChildren<Renderer>(true).Where(t => t.name.StartsWith("Tire_", StringComparison.Ordinal)).Select(t => t.bounds.extents.y).DefaultIfEmpty(.34f).Max();
                var driver = root.AddComponent<TrafficCar>(); driver.Configure(wheels, bounds.extents, radius);
                Seat(root, driverModel, "Seat_Driver", true);
                var rider = Seat(root, riderModel, "Seat_Passenger", false);
                root.AddComponent<CarAppearance>().Configure(AssetDatabase.LoadAssetAtPath<CarPalette>("Assets/Party/Data/CarPalette.asset"), true, City25Kit.PaintRenderers(root, id), rider);
                var amber = City25Kit.WithMaterial(root.transform, "Alarma_Indicator");
                // El auto mira a +Z: la izquierda es -X en su espacio local.
                root.AddComponent<CarLights>().Configure(driver, City25Kit.WithMaterial(root.transform, "Alarma_TailLight"),
                    amber.Where(r => root.transform.InverseTransformPoint(r.bounds.center).x < 0f).ToArray(),
                    amber.Where(r => root.transform.InverseTransformPoint(r.bounds.center).x > 0f).ToArray());
                return PrefabUtility.SaveAsPrefabAsset(root, folder + "/Prefabs/Trafico_" + id + "_" + variant + ".prefab").GetComponent<TrafficCar>();
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Civil del elenco sentado en el auto con pose fija: sin Animator, sin sombra y sin la bolsa de compras.
        private static GameObject Seat(GameObject car, GameObject model, string seatName, bool driving)
        {
            var person = (GameObject)PrefabUtility.InstantiatePrefab(model);
            person.name = (driving ? "Conductor_" : "Acompanante_") + model.name;
            person.transform.SetParent(car.transform, false);
            person.GetComponentInChildren<Animator>().enabled = false; // pose fija: nada la sobrescribe
            foreach (var t in person.GetComponentsInChildren<Transform>(true))
            {
                t.gameObject.layer = VehicleLayer;
                if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal) || t.name.StartsWith("Grip_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
            }
            SeatedPose.Apply(person.transform, car.transform, City25Kit.Part(car, seatName), driving);
            foreach (var skin in person.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            {
                // La pose cambia la forma: se amplían los límites para que no desaparezca al mirarlo de cerca.
                skin.localBounds = new Bounds(skin.localBounds.center, skin.localBounds.size + Vector3.one);
                skin.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            }
            return person;
        }
    }
}
