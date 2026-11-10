using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.Core.Editor;

namespace Alarma.Police.Editor
{
    // Prepara la policía a pie (Task 19): arma el prefab del agente (Prefabs/Agente_Police_Male) con su Animator de
    // posturas (reposo, caminar y correr del personaje, apuntar del pack, y esposar y levantarse de
    // build_npc_reaction_clips.py), cuerpo con física para la caída, movimiento, pistola en la mano y cerebro; y pone en
    // la escena la central con su reserva de agentes.
    public static class PoliceAssets
    {
        private const string Id = "Police_Male";
        private const string Clips = "Assets/Party/Art/Characters/Animations/Alarma_NpcReactions_Men.fbx";
        private const string Pistol = "Assets/Party/Art/Weapons/Weapon_Pistol.fbx";
        private const string SettingsPath = "Assets/Party/Data/Police/Policia.asset";
        private const int NpcLayer = 29;
        // Postura → clip propio de build_npc_reaction_clips.py (esqueleto del pack, se adapta al personaje).
        private static readonly Dictionary<PolicePose, string> Made = new Dictionary<PolicePose, string>
        {
            [PolicePose.Esposar] = "Esposar", [PolicePose.LevantarseEspalda] = "LevantarseEspalda", [PolicePose.LevantarseBoca] = "LevantarseBoca",
        };

        // Devuelve la central ya puesta en la escena abierta, o null si faltan los clips.
        public static GameObject Install(string output)
        {
            if (!File.Exists(Clips))
            {
                Debug.LogWarning("Faltan los clips de la policía (build_npc_reaction_clips.py): no habrá policía a pie.");
                return null;
            }
            var settings = LoadOrCreateSettings();
            var officer = MakeOfficer(output, settings);
            var root = new GameObject("Policía");
            var pool = root.AddComponent<PoliceOfficerPool>();
            pool.Configure(officer);
            root.AddComponent<PoliceDispatcher>().Configure(EventAssets.CrimeReports(), EventAssets.PoliceResponse(), settings, pool);
            return root;
        }

        private static PoliceSettings LoadOrCreateSettings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<PoliceSettings>(SettingsPath);
            if (settings != null) return settings;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath));
            settings = ScriptableObject.CreateInstance<PoliceSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }

        private static PoliceOfficer MakeOfficer(string output, PoliceSettings settings)
        {
            string modelPath = output + "/Art/Characters/" + Id + ".fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath) ?? throw new FileNotFoundException("Falta el modelo del policía", modelPath);
            var root = new GameObject("Agente_" + Id) { layer = NpcLayer };
            try
            {
                var capsule = root.AddComponent<CapsuleCollider>();
                capsule.height = 1.8f; capsule.radius = .25f; capsule.center = new Vector3(0f, .9f, 0f);
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(model);
                visual.transform.SetParent(root.transform, false);
                foreach (var t in visual.GetComponentsInChildren<Transform>(true))
                {
                    t.gameObject.layer = NpcLayer;
                    if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
                }
                var animator = visual.GetComponentInChildren<Animator>() ?? visual.AddComponent<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                // Los clips que el importador no renombra conservan el nombre de la toma («Rig|Clip»): se busca por el final.
                var own = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal))
                    .GroupBy(c => c.name.Split('|').Last()).ToDictionary(g => g.Key, g => g.First());
                AnimationClip Own(string name) => own.TryGetValue(name, out var clip) ? clip : throw new InvalidOperationException("Falta el clip " + name + " en " + modelPath);
                string folder = output + "/Controllers/Policia/" + Id;
                Directory.CreateDirectory(folder);
                var rootBone = ClipRemapper.RootBone(animator.transform) ?? throw new InvalidOperationException(Id + " no tiene el esqueleto del pack.");
                var pack = AssetDatabase.LoadAllAssetsAtPath(Clips).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToDictionary(c => c.name);
                // Reposo, caminar y correr: los de la Universal Animation Library si están; si no, los del modelo.
                var better = LocomotionClips.For(animator, folder + "/Locomocion");
                Motion Move(string mode, string fallback) => better?.Invoke(mode) ?? Own(fallback);
                var motions = new Dictionary<PolicePose, Motion>
                {
                    [PolicePose.Quieto] = Move("Idle", "Idle"), [PolicePose.Caminar] = Move("Walk", "Walk"), [PolicePose.Correr] = Move("Sprint", "Run"),
                    [PolicePose.Apuntar] = Own("Idle_Gun_Pointing"), // del pack: brazo extendido con la pistola
                };
                foreach (var entry in Made)
                {
                    var clip = pack.TryGetValue(entry.Value, out var found) ? found : throw new InvalidOperationException("Falta el clip " + entry.Value + " en " + Clips);
                    motions[entry.Key] = ClipRemapper.Remap(clip, animator.transform, rootBone, folder + "/" + entry.Value + ".anim", false);
                }
                animator.runtimeAnimatorController = PoseController.Create(folder + "/Agente_" + Id + ".controller", PoliceAnimator.Parameter, motions,
                    PolicePose.Quieto, pose => pose == PolicePose.LevantarseEspalda || pose == PolicePose.LevantarseBoca);
                // Cuerpo con física armado sobre el reposo: las articulaciones nacen con el cuerpo de pie y los brazos abajo.
                Own("Idle").SampleAnimation(animator.gameObject, 0f);
                var ragdoll = root.AddComponent<NpcRagdoll>();
                ragdoll.Build(animator, capsule);
                var poses = root.AddComponent<PoliceAnimator>();
                poses.Configure(animator);
                var motor = root.AddComponent<NpcFleeMotor>();
                var sidearm = MakeSidearm(root, visual.transform, settings);
                root.AddComponent<PoliceOfficer>().Configure(settings, motor, poses, ragdoll, sidearm, EventAssets.Suspects());
                Directory.CreateDirectory(output + "/Prefabs");
                return PrefabUtility.SaveAsPrefabAsset(root, output + "/Prefabs/Agente_" + Id + ".prefab").GetComponent<PoliceOfficer>();
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Pistola del jugador (Weapon_Pistol) en el agarre de la mano derecha, apagada hasta que apunte. Su punto de agarre
        // (Grip_R) queda en la mano; PoliceSidearm la gira hacia el blanco.
        private static PoliceSidearm MakeSidearm(GameObject root, Transform visual, PoliceSettings settings)
        {
            var grip = visual.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal))
                       ?? throw new InvalidOperationException(Id + " no tiene el agarre Grip_R6 de la mano derecha.");
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(Pistol) ?? throw new FileNotFoundException("Falta la pistola", Pistol);
            var holder = new GameObject("Pistola en mano") { layer = NpcLayer }.transform;
            holder.SetParent(grip, false);
            Vector3 scale = holder.lossyScale;
            holder.localScale = new Vector3(1f / scale.x, 1f / scale.y, 1f / scale.z); // tamaño real aunque el hueso tenga escala
            var model = (GameObject)PrefabUtility.InstantiatePrefab(asset);
            model.transform.SetParent(holder, false);
            foreach (var t in model.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = NpcLayer;
            foreach (var collider in model.GetComponentsInChildren<Collider>(true)) UnityEngine.Object.DestroyImmediate(collider);
            var hand = model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "Grip_R");
            if (hand != null) model.transform.position += holder.position - hand.position;
            var muzzle = model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "MuzzlePoint") ?? holder;
            holder.gameObject.SetActive(false);
            var sidearm = root.AddComponent<PoliceSidearm>();
            sidearm.Configure(holder, muzzle, EventAssets.Noise(), settings);
            return sidearm;
        }
    }
}
