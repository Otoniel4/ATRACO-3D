using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Alarma.AI.CityLife;
using Alarma.Core.Settings;
using Alarma.City.Playtest;
using Alarma.City.Playtest.Editor;

namespace Alarma.City.Editor
{
    // «Crear y probar juego»: prepara la ciudad de 2 × 2 km (kit, suelo y protagonistas), arma la escena, la comprueba y entra en Play.
    // Si nada cambió desde la última preparación, abre la escena guardada directamente.
    public static class City25Builder
    {
        private const string Version = "ciudad25-15";
        private const float ActiveRadius = 420f, FarClip = 450f;
        private static bool building;

        [MenuItem("Alarma/Crear y probar juego", false, 0)]
        public static void BuildAndPlay()
        {
            if (building || EditorApplication.isPlayingOrWillChangePlaymode) return;
            building = true; Scene stage = default; var previous = SceneManager.GetActiveScene();
            try
            {
                ReviewSceneProtection.Capture();
                string stamp = Stamp();
                if (File.Exists(City25Paths.Report))
                {
                    var ready = JsonUtility.FromJson<City25Record>(File.ReadAllText(City25Paths.Report));
                    if (ready.complete && ready.version == Version + "|" + stamp && File.Exists(ready.scene)) { EditorSceneManager.OpenScene(ready.scene, OpenSceneMode.Single); StartPlay(); return; }
                }
                // La escena anterior de la ciudad vive en la carpeta que se regenera: se reemplaza por la nueva antes de borrarla.
                bool replacing = Enumerable.Range(0, SceneManager.sceneCount).Select(SceneManager.GetSceneAt).Any(s => s.path.StartsWith(City25Paths.Output + "/", StringComparison.Ordinal));
                stage = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, replacing ? NewSceneMode.Single : NewSceneMode.Additive); SceneManager.SetActiveScene(stage);
                if (AssetDatabase.IsValidFolder(City25Paths.Output)) AssetDatabase.DeleteAsset(City25Paths.Output);
                PrepareOutput();
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Kit y suelo", .05f);
                var prefabs = City25Kit.Prepare(City25Kit.Manifest());
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Protagonistas", .45f);
                var (roles, walkers, civilians, shoppers, guard, police) = City25Characters.Prepare(City25Paths.Output);
                var city = City25Paths.Read<CityObjects>(City25Paths.Plan + "/city_objects.json");
                var ground = City25Paths.Read<GroundManifest>(City25Paths.Ground + "/ground.json");
                var world = City25World.Build(prefabs, city, ground);
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Jugador, mapa y luz", .9f);
                var map = City25Map.Create(City25Paths.Output);
                var hideout = map.Places.FirstOrDefault(p => p.Category == "escondite") ?? throw new InvalidOperationException("El plano no tiene escondite.");
                var streamer = world.Root.AddComponent<CitySectorStreamer>();
                var settings = Settings();
                var rig = ReviewPlayerRig.Create(streamer, hideout.Position + Vector3.up * .5f, roles, FarClip, settings);
                streamer.Configure(rig.Player.transform, world.Sectors, ground.half, ActiveRadius);
                var (shops, shopDoors) = City25Shops.Build(City25Paths.Output, world, City25Paths.Read<ShopLayouts>(City25Paths.Shops + "/shop_layouts.json"), shoppers);
                var doors = new GameObject("Puertas").AddComponent<ReviewDoorInteraction>();
                doors.Configure(rig.Input, rig.Player.transform, shopDoors, Array.Empty<ReviewSlidingDoor>());
                Shoppers(shops, shoppers, rig.Player.transform);
                int sentries = City25Security.Place(world, guard, police);
                var life = City25Paths.Read<CityLife>(City25Paths.Plan + "/city_life.json");
                var signals = City25Life.Signals(life, world.Signals);
                City25Life.Pedestrians(City25Paths.Output, life, signals, walkers, rig.Player.transform);
                City25Traffic.Build(City25Paths.Output, signals, rig.Player.transform, civilians);
                ReviewPlayerRig.Lighting(180, 430);
                ReviewPlayerRig.CreateInterface(rig, streamer, doors, map, settings);
                string acceptance = City25Acceptance.Validate(stage, world, city, hideout.Position);
                File.WriteAllText(City25Paths.Output + "/Acceptance.json", acceptance);
                if (!EditorSceneManager.SaveScene(stage, City25Paths.Scene)) throw new IOException("No se pudo guardar la escena de la ciudad.");
                var record = new City25Record { complete = true, version = Version + "|" + stamp, scene = City25Paths.Scene, objects = world.Placed, sectors = world.Sectors.Length, places = map.Places.Length };
                File.WriteAllText(City25Paths.Report, JsonUtility.ToJson(record, true)); AssetDatabase.Refresh();
                for (int i = SceneManager.sceneCount - 1; i >= 0; i--) { var other = SceneManager.GetSceneAt(i); if (other != stage) EditorSceneManager.CloseScene(other, true); }
                Selection.activeGameObject = rig.Player.gameObject;
                Debug.Log($"Alarma: ciudad 2 × 2 km lista con {world.Placed} objetos en {world.Sectors.Length} sectores, {signals.Count} semáforos con ciclo, peatones en las aceras, autos con conductor, {shops.Length} locales con interior, {sentries} guardias y policías y {map.Places.Length} lugares en el mapa. Inicio en el escondite; M: mapa, Esc: menú.");
                StartPlay();
            }
            catch (Exception error)
            {
                if (stage.IsValid() && stage.isLoaded) EditorSceneManager.CloseScene(stage, true);
                if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
                if (AssetDatabase.IsValidFolder(City25Paths.Output)) AssetDatabase.DeleteAsset(City25Paths.Output);
                if (!(error is OperationCanceledException)) { Debug.LogException(error); EditorUtility.DisplayDialog("Ciudad 2 km interrumpida", error.Message + "\n\nTus escenas siguen abiertas. Revisa Console.", "Cerrar"); }
            }
            finally { building = false; EditorUtility.ClearProgressBar(); }
        }

        [MenuItem("Alarma/Crear y probar juego", true)]
        private static bool CanBuild() => !building && !EditorApplication.isCompiling && !EditorApplication.isUpdating && !EditorApplication.isPlayingOrWillChangePlaymode;

        // Los ajustes iniciales viven en Party/Data para que se puedan editar sin regenerar la ciudad.
        private static GameSettings Settings()
        {
            const string path = "Assets/Party/Data/GameSettings.asset";
            var settings = AssetDatabase.LoadAssetAtPath<GameSettings>(path);
            if (settings == null) { settings = ScriptableObject.CreateInstance<GameSettings>(); AssetDatabase.CreateAsset(settings, path); }
            return settings;
        }

        // Compradores cerca del jugador: llegan por la acera, empujan la puerta, eligen productos, hacen fila, pagan y salen.
        private static void Shoppers(ShopActivity[] shops, PedestrianActor[] civilians, Transform player)
        {
            const string path = "Assets/Party/Data/ShopperSettings.asset";
            var settings = AssetDatabase.LoadAssetAtPath<PedestrianSettings>(path);
            if (settings == null)
            {
                settings = ScriptableObject.CreateInstance<PedestrianSettings>();
                settings.PerDistrict = 4; settings.ShopperFraction = 1; settings.PopulationBudget = 16; settings.BrowseSeconds = 2.5f; settings.PaySeconds = 1.2f;
                settings.ActivationRadius = 90; settings.DeactivationRadius = 140;
                AssetDatabase.CreateAsset(settings, path);
            }
            var population = new GameObject("Compradores");
            population.AddComponent<CityPopulationDirector>().Configure(settings, civilians, shops, player, population.AddComponent<LocalCityLifeAuthority>(), null);
            foreach (var shop in shops) shop.Traffic.ConfigureBlocker(player);
        }

        private static void PrepareOutput()
        {
            foreach (string child in new[] { "Art", "Data", "Materials", "Controllers", "Prefabs", "Scenes" }) Directory.CreateDirectory(City25Paths.Output + "/" + child);
            AssetDatabase.Refresh();
        }

        private static void StartPlay()
        {
            EditorApplication.delayCall += () =>
            {
                if (EditorApplication.isCompiling || EditorApplication.isUpdating) { StartPlay(); return; }
                EditorApplication.ExecuteMenuItem("Window/General/Game"); EditorApplication.EnterPlaymode();
            };
        }

        // Cambia cuando se regenera el plano, el kit, el suelo o el mapa: entonces hay que preparar de nuevo.
        private static string Stamp() => string.Join(",", new[]
        {
            City25Paths.Plan + "/city_objects.json", City25Paths.Plan + "/city_life.json", City25Paths.Plan + "/city_traffic.json", City25Paths.Kit + "/kit.json", City25Paths.Kit + "/street_kit.json", City25Paths.Vehicles + "/vehicle_materials.json", City25Paths.Shops + "/shop_layouts.json", City25Paths.Ground + "/ground.json", City25Paths.Map + "/map_places.json"
        }.Select(p => File.GetLastWriteTimeUtc(p).Ticks));
    }
}
