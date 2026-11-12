using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
using Alarma.Core.Settings;
using Alarma.City.Playtest;
using Alarma.City.Playtest.Editor;
using Alarma.AI.Editor;
using Alarma.Police.Editor;

namespace Alarma.City.Editor
{
    // «Crear y probar juego»: prepara la ciudad de 2 × 2 km (kit, suelo y protagonistas), arma la escena, la comprueba y entra en Play.
    // Si nada cambió desde la última preparación, abre la escena guardada directamente.
    public static class City25Builder
    {
        private const string Version = "ciudad25-48"; // Palma hacia el objeto y poses de dedos por tipo de objeto.
        private const float ActiveRadius = 420f, FarClip = 450f;
        private static bool building;

        [MenuItem("Alarma/Crear y probar juego", false, 0)]
        public static void BuildAndPlay()
        {
            if (building || EditorApplication.isPlayingOrWillChangePlaymode) return;
            building = true;
            City25BuildRecovery recovery = null;
            try
            {
                ReviewSceneProtection.Capture();
                string stamp = Stamp();
                var ready = ReadReport();
                if (ready != null && ready.version == Version + "|" + stamp)
                {
                    EditorSceneManager.OpenScene(ready.scene, OpenSceneMode.Single);
                    SelectBuildScene(ready.scene);
                    StartPlay();
                    return;
                }
                recovery = new City25BuildRecovery(ready?.scene);
                string output = recovery.Output;
                PrepareOutput(output);
                var stage = recovery.OpenStage();
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Kit y suelo", .05f);
                var prefabs = City25Kit.Prepare(City25Kit.Manifest(), output);
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Protagonistas", .45f);
                var (roles, walkers, civilians, shoppers, guard, police) = City25Characters.Prepare(output);
                // Reacciones de los civiles (Task 13): doble de reacción y disparador en cada prefab de civil.
                NpcReactionAssets.Prepare(output, shoppers.Select(s => s.gameObject));
                var city = City25Paths.Read<CityObjects>(City25Paths.Plan + "/city_objects.json");
                var ground = City25Paths.Read<GroundManifest>(City25Paths.Ground + "/ground.json");
                var world = City25World.Build(prefabs, city, ground);
                EditorUtility.DisplayProgressBar("Ciudad 2 km", "Jugador, mapa y luz", .9f);
                var map = City25Map.Create(output);
                var hideout = map.Places.FirstOrDefault(p => p.Category == "escondite") ?? throw new InvalidOperationException("El plano no tiene escondite.");
                var streamer = world.Root.AddComponent<CitySectorStreamer>();
                var settings = Settings();
                var hideoutModel = world.Places.Single(p => p.data.place.kind == "escondite").instance;
                var entrance = hideoutModel.GetComponentsInChildren<Transform>(true).SingleOrDefault(t => t.name == "PlayerSpawn")
                    ?? throw new InvalidOperationException("El modelo de la guarida no tiene el marcador PlayerSpawn dentro del recibidor.");
                var rig = ReviewPlayerRig.Create(streamer, entrance.position, roles, FarClip, settings);
                rig.Player.transform.rotation = Quaternion.Euler(0f, entrance.eulerAngles.y, 0f);
                rig.Camera.ResetView(entrance.eulerAngles.y);
                streamer.Configure(rig.Player.transform, world.Sectors, ground.half, ActiveRadius);
                var (shops, shopDoors) = City25Shops.Build(output, world, City25Paths.Read<ShopLayouts>(City25Paths.Shops + "/shop_layouts.json"), shoppers);
                var doors = new GameObject("Puertas").AddComponent<ReviewDoorInteraction>();
                // E interactúa con el acceso más cercano. Las hojas abatibles también admiten empuje al acercarse.
                var hinged = world.Places.SelectMany(p => p.instance.GetComponentsInChildren<ShopDoor>()).Union(shopDoors).ToArray();
                var sliding = world.Places.SelectMany(p => p.instance.GetComponentsInChildren<ReviewSlidingDoor>()).ToArray();
                doors.Configure(rig.Input, rig.Player.transform, hinged, sliding);
                foreach (var shop in shops) shop.Traffic.ConfigureBlocker(rig.Player.transform);
                int sentries = City25Security.Place(world, guard, police);
                // Policía a pie (Task 19): prefab del agente y central que responde a las denuncias.
                PoliceAssets.Install(output);
                // Cámaras de seguridad en los locales (Task 15): ven a quien lleva un arma en la mano y avisan.
                int cameras = City25Cameras.Place(world);
                // Alerta de cada local con cámaras: sigilo, sospecha, alarma, policía en camino y asalto.
                City25Alerts.Place(world);
                var life = City25Paths.Read<CityLife>(City25Paths.Plan + "/city_life.json");
                var signals = City25Life.Signals(life, world.Signals);
                City25Life.Pedestrians(output, life, signals, walkers, rig.Player.transform, shops, ShopperSettings());
                City25Traffic.Build(output, signals, rig.Player.transform, civilians);
                ReviewPlayerRig.Lighting(180, 430);
                ReviewPlayerRig.CreateInterface(rig, streamer, doors, map, settings);
                // Ajustes de dibujo que no cambian la imagen (sondas de luz sin hornear): medidos con PerformanceProbe.
                City25RenderBudget.Apply(stage, output);
                string acceptance = City25Acceptance.Validate(stage, world, city, rig.Player);
                File.WriteAllText(output + "/Acceptance.json", acceptance);
                recovery.SaveAndOpenStage(stage);
                var record = new City25Record { complete = true, version = Version + "|" + stamp, scene = recovery.ScenePath, objects = world.Placed, sectors = world.Sectors.Length, places = map.Places.Length };
                recovery.Publish(JsonUtility.ToJson(record, true));
                SelectBuildScene(recovery.ScenePath);
                Debug.Log($"Alarma: ciudad 2 × 2 km lista con {world.Placed} objetos en {world.Sectors.Length} sectores, {signals.Count} semáforos con ciclo, peatones en las aceras, autos con conductor, {shops.Length} locales con interior, {sentries} guardias y policías, {cameras} cámaras y {map.Places.Length} lugares en el mapa. Inicio en el escondite; M: mapa, Esc: menú.");
                StartPlay();
            }
            catch (Exception error)
            {
                string recovered = "No se reemplazó la ciudad guardada.";
                if (recovery != null)
                {
                    try { recovered = recovery.Restore(); }
                    catch (Exception restoreError)
                    {
                        Debug.LogException(restoreError);
                        recovered = "La ciudad anterior sigue guardada. Puedes abrir su escena desde Project.";
                    }
                }
                if (!(error is OperationCanceledException)) { Debug.LogException(error); EditorUtility.DisplayDialog("Ciudad 2 km interrumpida", error.Message + "\n\n" + recovered + "\nRevisa Console.", "Cerrar"); }
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

        private static PedestrianSettings ShopperSettings()
        {
            const string path = "Assets/Party/Data/ShopperSettings.asset";
            var settings = AssetDatabase.LoadAssetAtPath<PedestrianSettings>(path);
            if (settings == null)
            {
                settings = ScriptableObject.CreateInstance<PedestrianSettings>();
                settings.PerDistrict = 4; settings.ShopperFraction = 1; settings.PopulationBudget = 16; settings.BrowseSeconds = 2.5f;
                settings.ActivationRadius = 90; settings.DeactivationRadius = 140;
                AssetDatabase.CreateAsset(settings, path);
            }
            return settings;
        }

        private static City25Record ReadReport()
        {
            if (!File.Exists(City25Paths.Report)) return null;
            City25Record ready;
            try { ready = JsonUtility.FromJson<City25Record>(File.ReadAllText(City25Paths.Report)); }
            catch (ArgumentException) { return null; }
            return ready != null && ready.complete && City25Paths.IsCityScene(ready.scene) && File.Exists(ready.scene) ? ready : null;
        }

        private static void SelectBuildScene(string scene)
        {
            var scenes = EditorBuildSettings.scenes;
            if (scenes.Any(entry => entry.path == scene)) return;
            for (int i = 0; i < scenes.Length; i++)
            {
                if (!City25Paths.IsCityScene(scenes[i].path)) continue;
                scenes[i] = new EditorBuildSettingsScene(scene, scenes[i].enabled);
                EditorBuildSettings.scenes = scenes;
                return;
            }
        }

        private static void PrepareOutput(string output)
        {
            foreach (string child in new[] { "Art", "Data", "Materials", "Controllers", "Prefabs", "Scenes" }) FlatMaterialLibrary.EnsureFolder(output + "/" + child);
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
            City25Paths.Plan + "/city_objects.json", City25Paths.Plan + "/city_life.json", City25Paths.Plan + "/city_traffic.json", City25Paths.Kit + "/kit.json", City25Paths.Kit + "/street_kit.json", City25Paths.Kit + "/district_kit.json", City25Paths.Vehicles + "/vehicle_materials.json", City25Paths.Shops + "/shop_layouts.json", City25Paths.Shops + "/hideout_materials.json", City25Paths.Ground + "/ground.json", City25Paths.Map + "/map_places.json",
            "Assets/Party/Data/Items/item_actions.json", // animaciones y datos de uso de los objetos (ItemActionAssets)
            "Assets/Party/Art/Props/ShopObjects/catalog.json",
            "Assets/Party/Scripts/City/Editor/City25/City25Products.cs",
            ActionClips + "/item_action_clips.json",      // clips de cuerpo para usar objetos (ItemActionAnimatorAssets)
            ActionClips + "/npc_reaction_clips.json"      // clips de reacción de los civiles (NpcReactionAssets)
        }.Select(ContentHash).Concat(Directory.GetFiles(City25Paths.Shops, "Local_*.fbx").Concat(Directory.GetFiles(ActionClips, "*.fbx"))
            .Concat(Directory.GetFiles("Assets/Party/Art/Props/ShopObjects", "*.fbx"))
            .OrderBy(path => path, StringComparer.Ordinal).Select(ModelHash)).Concat(RigScripts.SelectMany(folder => Directory.GetFiles(folder, "*.cs", SearchOption.AllDirectories))
            .OrderBy(path => path, StringComparer.Ordinal).Select(ContentHash))
            .Concat(Directory.GetFiles("Assets/Party/Data/ShopAnimations", "*.asset").OrderBy(path => path, StringComparer.Ordinal).Select(ContentHash)));

        // El código de los componentes que el constructor arma y guarda en la escena (jugador, inventario e interfaz):
        // si cambia, la escena guardada queda vieja y hay que prepararla otra vez.
        private static readonly string[] RigScripts = { "Assets/Party/Scripts/Player", "Assets/Party/Scripts/UI", "Assets/Party/Scripts/City/PlaytestR7", "Assets/Party/Scripts/City/Editor/PlaytestR7", "Assets/Party/Scripts/Animation",
                                                            "Assets/Party/Scripts/AI/Reactions", "Assets/Party/Scripts/AI/Editor", "Assets/Party/Scripts/AI/CityLifeR5", "Assets/Party/Scripts/AI/Security", "Assets/Party/Scripts/AI/Pathing", "Assets/Party/Scripts/Police" };
        private const string ActionClips = "Assets/Party/Art/Characters/Animations";

        private static string ModelHash(string path)
        {
            using (var model = File.OpenRead(path))
            using (var algorithm = SHA256.Create())
                return BitConverter.ToString(algorithm.ComputeHash(model)).Replace("-", string.Empty);
        }

        // Las fechas cambian al clonar Git; el contenido permite reutilizar la escena respaldada en otro equipo.
        private static string ContentHash(string path)
        {
            using (var algorithm = SHA256.Create())
                return BitConverter.ToString(algorithm.ComputeHash(Encoding.UTF8.GetBytes(
                    File.ReadAllText(path).Replace("\r\n", "\n")))).Replace("-", string.Empty);
        }
    }
}
