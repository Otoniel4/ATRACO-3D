using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.AI.Security;
using Alarma.Core.Editor;

namespace Alarma.AI.Editor
{
    // Prepara al guardia que defiende su local (Task 14): prefab Prefabs/Guardia_<id> con su Animator de posturas
    // (reposo, caminar y correr del personaje, golpe del pack y levantarse de build_npc_reaction_clips.py), cuerpo con
    // física para caer, movimiento, porra en la mano y cerebro (SecurityGuard). En su puesto sigue mirando a los lados.
    public static class GuardAssets
    {
        private const string Clips = "Assets/Party/Art/Characters/Animations/Alarma_NpcReactions_Men.fbx";
        private const string Baton = "Assets/Party/Art/Weapons/Weapon_Baton.fbx";
        private const string SettingsPath = "Assets/Party/Data/NPC/Guardias.asset";
        private const int NpcLayer = 29;
        // Postura → clip propio de build_npc_reaction_clips.py (esqueleto del pack, se adapta al personaje).
        private static readonly Dictionary<GuardPose, string> Made = new Dictionary<GuardPose, string>
        {
            [GuardPose.LevantarseEspalda] = "LevantarseEspalda", [GuardPose.LevantarseBoca] = "LevantarseBoca",
        };

        // Devuelve el prefab del guardia, o null si faltan los clips (entonces queda el guardia de adorno).
        public static GameObject MakeGuard(string output, string id)
        {
            if (!File.Exists(Clips))
            {
                Debug.LogWarning("Faltan los clips de build_npc_reaction_clips.py: los guardias no defenderán su local.");
                return null;
            }
            ClipRemapper.ConfigureImport(Clips, name => false);
            var settings = LoadOrCreateSettings();
            string modelPath = output + "/Art/Characters/" + id + ".fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath) ?? throw new FileNotFoundException("Falta el modelo del guardia", modelPath);
            var root = new GameObject("Guardia_" + id) { layer = NpcLayer };
            try
            {
                var capsule = root.AddComponent<CapsuleCollider>();
                capsule.height = 1.75f; capsule.radius = .28f; capsule.center = new Vector3(0f, .875f, 0f);
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(model);
                visual.transform.SetParent(root.transform, false);
                foreach (var t in visual.GetComponentsInChildren<Transform>(true))
                {
                    t.gameObject.layer = NpcLayer;
                    if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
                }
                var animator = visual.GetComponentInChildren<Animator>() ?? visual.AddComponent<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                // Los clips que el importador no renombra conservan el nombre de la toma («Rig|Clip»): se busca por el final.
                var own = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal))
                    .GroupBy(c => c.name.Split('|').Last()).ToDictionary(g => g.Key, g => g.First());
                AnimationClip Own(string name) => own.TryGetValue(name, out var clip) ? clip : throw new InvalidOperationException("Falta el clip " + name + " en " + modelPath);
                string folder = output + "/Controllers/Guardias/" + id;
                Directory.CreateDirectory(folder);
                var rootBone = ClipRemapper.RootBone(animator.transform) ?? throw new InvalidOperationException(id + " no tiene el esqueleto del pack.");
                var pack = AssetDatabase.LoadAllAssetsAtPath(Clips).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToDictionary(c => c.name);
                // Reposo, caminar y correr: los de la Universal Animation Library si están; si no, los del modelo.
                var better = LocomotionClips.For(animator, folder + "/Locomocion");
                Motion Move(string mode, string fallback) => better?.Invoke(mode) ?? Own(fallback);
                var motions = new Dictionary<GuardPose, Motion>
                {
                    [GuardPose.Quieto] = Move("Idle", "Idle"), [GuardPose.Caminar] = Move("Walk", "Walk"), [GuardPose.Correr] = Move("Sprint", "Run"),
                    [GuardPose.Golpear] = Own("Punch_Right"), // del pack: el brazo derecho lanza el golpe; la porra la mueve GuardBody
                };
                foreach (var entry in Made)
                {
                    var clip = pack.TryGetValue(entry.Value, out var found) ? found : throw new InvalidOperationException("Falta el clip " + entry.Value + " en " + Clips);
                    motions[entry.Key] = ClipRemapper.Remap(clip, animator.transform, rootBone, folder + "/" + entry.Value + ".anim", false);
                }
                animator.runtimeAnimatorController = PoseController.Create(folder + "/Guardia_" + id + ".controller", GuardBody.Parameter, motions,
                    GuardPose.Quieto, pose => pose == GuardPose.LevantarseEspalda || pose == GuardPose.LevantarseBoca);
                // Cuerpo con física armado sobre el reposo: las articulaciones nacen con el cuerpo de pie y los brazos abajo.
                Own("Idle").SampleAnimation(animator.gameObject, 0f);
                var ragdoll = root.AddComponent<NpcRagdoll>();
                ragdoll.Build(animator, capsule);
                var body = root.AddComponent<GuardBody>();
                body.Configure(animator, MakeBaton(visual.transform, id));
                var motor = root.AddComponent<NpcFleeMotor>();
                var look = root.AddComponent<SentryLook>();
                root.AddComponent<SecurityGuard>().Configure(settings, motor, body, ragdoll, look, EventAssets.Suspects(), EventAssets.Noise(), EventAssets.CrimeReports());
                Directory.CreateDirectory(output + "/Prefabs");
                return PrefabUtility.SaveAsPrefabAsset(root, output + "/Prefabs/Guardia_" + id + ".prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        private static GuardSettings LoadOrCreateSettings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<GuardSettings>(SettingsPath);
            if (settings != null) return settings;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath));
            settings = ScriptableObject.CreateInstance<GuardSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }

        // Porra (Weapon_Baton) en el agarre de la mano derecha, apagada en el puesto. Su punto de agarre (Grip_R) queda
        // en la mano; GuardBody la inclina con el golpe.
        private static Transform MakeBaton(Transform visual, string id)
        {
            var grip = visual.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.StartsWith("Grip_R6_", StringComparison.Ordinal))
                       ?? throw new InvalidOperationException(id + " no tiene el agarre Grip_R6 de la mano derecha.");
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(Baton) ?? throw new FileNotFoundException("Falta la porra", Baton);
            var holder = new GameObject("Porra en mano") { layer = NpcLayer }.transform;
            holder.SetParent(grip, false);
            Vector3 scale = holder.lossyScale;
            holder.localScale = new Vector3(1f / scale.x, 1f / scale.y, 1f / scale.z); // tamaño real aunque el hueso tenga escala
            holder.rotation = visual.rotation;
            var model = (GameObject)PrefabUtility.InstantiatePrefab(asset);
            model.transform.SetParent(holder, false);
            foreach (var t in model.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = NpcLayer;
            foreach (var collider in model.GetComponentsInChildren<Collider>(true)) UnityEngine.Object.DestroyImmediate(collider);
            var hand = model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "Grip_R");
            if (hand != null) model.transform.position += holder.position - hand.position;
            holder.gameObject.SetActive(false);
            return holder;
        }
    }
}
