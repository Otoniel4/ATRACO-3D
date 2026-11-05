using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
using Alarma.AI.Security;
using Alarma.AI.Street;

namespace Alarma.City.Editor
{
    // Personajes de la ciudad: los cuatro protagonistas (F1 a F4) y los diez civiles que pasean por las aceras.
    // Se copian solo sus FBX del elenco; guardias y policías llegarán con los locales.
    internal static class City25Characters
    {
        private static readonly string[] Roles = { "Player01_Thief", "Player02_Hacker", "Player03_Distractor", "Player04_Muscle" };
        private static readonly string[] Sentries = { "Security_Male", "Police_Male" }; // guardia con porra y policía con pistola

        public static (GameObject[] roles, SidewalkWalker[] walkers, GameObject[] civilians, PedestrianActor[] shoppers, GameObject guard, GameObject police) Prepare(string folder)
        {
            string[] civilians = Directory.GetFiles(City25Paths.Cast, "NPC*.fbx").Select(Path.GetFileNameWithoutExtension)
                .Where(id => int.Parse(id.Substring(3, 2)) <= 10).OrderBy(id => id, StringComparer.Ordinal).ToArray();
            if (civilians.Length != 10) throw new InvalidOperationException("Se esperaban diez civiles en " + City25Paths.Cast);
            var manifest = new CharacterManifest { characters = Roles.Concat(civilians).Concat(Sentries).Select(id => new CharacterEntry { id = id, rig = id + "_Rig" }).ToArray() };
            Directory.CreateDirectory(folder + "/Art/Characters");
            foreach (var c in manifest.characters) File.Copy(City25Paths.Cast + "/" + c.id + ".fbx", folder + "/Art/Characters/" + c.id + ".fbx", true);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            CityLifeImport.ConfigureCharacters(folder, manifest);
            var models = manifest.characters.Select(c => Model(folder, c.id)).ToArray();
            var materials = FlatMaterialLibrary.Create(folder, City25Paths.ColorManifests, FlatMaterialLibrary.UsedNames(models));
            FlatMaterialLibrary.Remap(models, materials, "Ciudad 2 km");
            var roles = manifest.characters.Take(Roles.Length).Select(c => Visual(folder, c.id, PedestrianPrefabFactory.MakePrefab(folder, c))).ToArray();
            // Los modelos de civiles también se sientan en los autos que circulan.
            // Los mismos civiles compran en los locales (con su lógica de compra) y atienden la caja.
            var shoppers = manifest.characters.Where(c => civilians.Contains(c.id)).Select(c => PedestrianPrefabFactory.MakePrefab(folder, c)).ToArray();
            return (roles, shoppers.Select((actor, index) => Walker(folder, civilians[index], actor)).ToArray(), civilians.Select(id => AssetDatabase.LoadAssetAtPath<GameObject>(Model(folder, id))).ToArray(), shoppers,
                    Sentry(folder, Sentries[0]), Sentry(folder, Sentries[1]));
        }

        private static string Model(string folder, string id) => folder + "/Art/Characters/" + id + ".fbx";

        // Solo el modelo animado: el jugador no necesita la lógica de peatón.
        private static GameObject Visual(string folder, string id, PedestrianActor actor)
        {
            var model = actor.GetComponentInChildren<Animator>(true).gameObject;
            var copy = new GameObject(id + "_Visual");
            var body = UnityEngine.Object.Instantiate(model);
            body.transform.SetParent(copy.transform, false);
            // Brazo con alcance (IK) para empujar puertas igual que los NPC.
            var grip = body.GetComponentsInChildren<Transform>(true).First(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal));
            body.AddComponent<PedestrianReach>().Configure(grip);
            try { return PrefabUtility.SaveAsPrefabAsset(copy, folder + "/Prefabs/" + id + "_Visual.prefab"); }
            finally { UnityEngine.Object.DestroyImmediate(copy); }
        }

        // Guardia o policía de puesto fijo: quieto en reposo, con cuerpo para que nadie lo atraviese, mirando alrededor.
        private static GameObject Sentry(string folder, string id)
        {
            string path = Model(folder, id);
            var root = new GameObject("Puesto_" + id);
            try
            {
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));
                visual.transform.SetParent(root.transform, false);
                var animator = visual.GetComponentInChildren<Animator>() ?? visual.AddComponent<Animator>();
                animator.runtimeAnimatorController = CityLifeAnimatorFactory.Create(folder + "/Controllers/Puesto_" + id + ".controller", path);
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.CullCompletely;
                foreach (var t in visual.GetComponentsInChildren<Transform>(true))
                    if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
                var body = root.AddComponent<CapsuleCollider>(); body.height = 1.75f; body.radius = .28f; body.center = new Vector3(0f, .875f, 0f);
                foreach (var t in root.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = 29;
                root.AddComponent<SentryLook>();
                return PrefabUtility.SaveAsPrefabAsset(root, folder + "/Prefabs/Puesto_" + id + ".prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Un mismo cuerpo pasea y visita comercios con su rutina interior.
        private static SidewalkWalker Walker(string folder, string id, PedestrianActor actor)
        {
            var root = (GameObject)PrefabUtility.InstantiatePrefab(actor.gameObject);
            root.name = "Peaton_" + id;
            try
            {
                var animator = root.GetComponentInChildren<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                root.GetComponent<CapsuleCollider>().radius = .25f;
                root.AddComponent<Rigidbody>().isKinematic = true; // se mueve por código sin que la física lo empuje
                root.AddComponent<SidewalkWalker>().Configure(animator);
                return PrefabUtility.SaveAsPrefabAsset(root, folder + "/Prefabs/Peaton_" + id + ".prefab").GetComponent<SidewalkWalker>();
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
