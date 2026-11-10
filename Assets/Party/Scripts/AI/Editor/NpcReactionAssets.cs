using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.Core.Editor;

namespace Alarma.AI.Editor
{
    // Prepara las reacciones de los civiles (Task 13): para cada personaje arma su doble de reacción (Prefabs/Reaccion_<id>)
    // con Animator propio (reposo, caminar y correr del personaje más los clips de build_npc_reaction_clips.py), cuerpo
    // con física para caer (NpcRagdoll, armado sobre la pose de reposo) y cerebro (NpcReactions); y agrega a cada
    // prefab de civil el disparador que lo reemplaza por su doble (NpcReactionTrigger). Los peatones son variantes de esos
    // prefabs y lo heredan. No modifica el código de la población.
    public static class NpcReactionAssets
    {
        private const string Folder = "Assets/Party/Art/Characters/Animations";
        private const string ManifestPath = Folder + "/npc_reaction_clips.json";
        private const string SettingsPath = "Assets/Party/Data/NPC/ReaccionesCiviles.asset";
        private const int NpcLayer = 29;

        public static void Prepare(string output, IEnumerable<GameObject> civilianPrefabs)
        {
            if (!File.Exists(ManifestPath))
            {
                Debug.LogWarning("Faltan los clips de reacción de los civiles (build_npc_reaction_clips.py): los civiles no reaccionarán.");
                return;
            }
            var manifest = JsonUtility.FromJson<ClipManifest>(File.ReadAllText(ManifestPath));
            foreach (var file in manifest.files) ClipRemapper.ConfigureImport(Folder + "/" + file.file, name => manifest.clips.Any(c => c.id == name && c.loop));
            var settings = LoadOrCreateSettings();
            var noise = EventAssets.Noise();
            var reports = EventAssets.CrimeReports();
            var doubles = new Dictionary<string, NpcReactions>();
            foreach (var prefab in civilianPrefabs)
            {
                string path = AssetDatabase.GetAssetPath(prefab);
                var contents = PrefabUtility.LoadPrefabContents(path);
                try
                {
                    var animator = contents.GetComponentInChildren<Animator>(true) ?? throw new InvalidOperationException(path + " no tiene Animator.");
                    string id = CharacterId(animator);
                    if (!doubles.TryGetValue(id, out var reaction)) doubles[id] = reaction = MakeDouble(output, id, manifest, settings, noise, reports);
                    var trigger = contents.GetComponent<NpcReactionTrigger>() ?? contents.AddComponent<NpcReactionTrigger>();
                    trigger.Configure(reaction, noise, animator.transform);
                    PrefabUtility.SaveAsPrefabAsset(contents, path);
                }
                finally { PrefabUtility.UnloadPrefabContents(contents); }
            }
            AssetDatabase.SaveAssets();
        }

        private static string CharacterId(Animator animator)
        {
            var root = ClipRemapper.RootBone(animator.transform) ?? throw new InvalidOperationException(animator.name + " no tiene el esqueleto del pack.");
            string rig = root.parent != null ? root.parent.name : animator.name;
            return rig.EndsWith("_Rig", StringComparison.Ordinal) ? rig.Substring(0, rig.Length - 4) : rig;
        }

        private static NpcReactionSettings LoadOrCreateSettings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<NpcReactionSettings>(SettingsPath);
            if (settings != null) return settings;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath));
            settings = ScriptableObject.CreateInstance<NpcReactionSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }

        private static NpcReactions MakeDouble(string output, string id, ClipManifest manifest, NpcReactionSettings settings, Alarma.Core.Events.NoiseChannel noise,
            Alarma.Core.Events.CrimeReportChannel reports)
        {
            string modelPath = output + "/Art/Characters/" + id + ".fbx";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath) ?? throw new FileNotFoundException("Falta el modelo del civil", modelPath);
            var root = new GameObject("Reaccion_" + id) { layer = NpcLayer };
            try
            {
                var capsule = root.AddComponent<CapsuleCollider>();
                capsule.height = 1.7f; capsule.radius = .23f; capsule.center = new Vector3(0f, .85f, 0f);
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(model);
                visual.transform.SetParent(root.transform, false);
                foreach (var t in visual.GetComponentsInChildren<Transform>(true))
                {
                    t.gameObject.layer = NpcLayer;
                    if (t.name.StartsWith("ShoppingBag_", StringComparison.Ordinal)) t.gameObject.SetActive(false);
                }
                var animator = visual.GetComponentInChildren<Animator>() ?? visual.AddComponent<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                var own = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().ToDictionary(c => c.name, c => c);
                AnimationClip Own(string name) => own.TryGetValue(name, out var clip) ? clip : throw new InvalidOperationException("Falta el clip " + name + " en " + modelPath);
                string folder = output + "/Controllers/Reacciones/" + id;
                Directory.CreateDirectory(folder);
                var rootBone = ClipRemapper.RootBone(animator.transform);
                string pack = manifest.roles.FirstOrDefault(r => r.id == id)?.pack ?? "Men";
                string source = Folder + "/" + manifest.files.First(f => f.pack == pack).file;
                var packClips = AssetDatabase.LoadAllAssetsAtPath(source).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToDictionary(c => c.name);
                // Reposo, caminar y correr: los de la Universal Animation Library si están; si no, los del modelo.
                var better = LocomotionClips.For(animator, folder + "/Locomocion");
                Motion Move(string mode, string own) => better?.Invoke(mode) ?? Own(own);
                var motions = new Dictionary<ReactionPose, Motion> { [ReactionPose.Quieto] = Move("Idle", "Idle"), [ReactionPose.Caminar] = Move("Walk", "Walk"), [ReactionPose.Correr] = Move("Sprint", "Run") };
                foreach (var entry in manifest.clips)
                {
                    if (!Enum.TryParse(entry.id, out ReactionPose pose)) continue;
                    var clip = packClips.TryGetValue(entry.id, out var found) ? found : throw new InvalidOperationException("Falta el clip " + entry.id + " en " + source);
                    motions[pose] = ClipRemapper.Remap(clip, animator.transform, rootBone, folder + "/" + entry.id + ".anim", entry.loop);
                }
                animator.runtimeAnimatorController = Controller(folder + "/Reaccion_" + id + ".controller", motions);
                // Cuerpo con física armado sobre el reposo: las articulaciones nacen con el cuerpo de pie y los brazos abajo.
                Own("Idle").SampleAnimation(animator.gameObject, 0f);
                var ragdoll = root.AddComponent<NpcRagdoll>();
                ragdoll.Build(animator, capsule);
                var poses = root.AddComponent<NpcReactionAnimator>();
                poses.Configure(animator);
                var motor = root.AddComponent<NpcFleeMotor>();
                var reactions = root.AddComponent<NpcReactions>();
                reactions.Configure(settings, noise, poses, motor, ragdoll, reports, MakePhone(root, animator, rootBone));
                return PrefabUtility.SaveAsPrefabAsset(root, output + "/Prefabs/Reaccion_" + id + ".prefab").GetComponent<NpcReactions>();
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Celular en la mano derecha y barra de la llamada sobre la cabeza del testigo, apagados hasta que grabe
        // (WitnessPhone). Se arma con el cuerpo en reposo: el celular queda a lo largo de la mano.
        private static WitnessPhone MakePhone(GameObject root, Animator animator, Transform rootBone)
        {
            Transform Bone(string name) => rootBone.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name)
                                           ?? throw new InvalidOperationException("Falta el hueso " + name + " en " + animator.name);
            GameObject Shape(PrimitiveType type, string name, Material material)
            {
                var shape = GameObject.CreatePrimitive(type);
                shape.name = name;
                UnityEngine.Object.DestroyImmediate(shape.GetComponent<Collider>());
                var renderer = shape.GetComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                return shape;
            }
            Transform wrist = Bone("Wrist.R"), forearm = Bone("LowerArm.R");
            Vector3 along = (wrist.position - forearm.position).normalized;
            var dark = Flat("Testigo_Celular", new Color(.08f, .09f, .11f));
            var phone = Shape(PrimitiveType.Cube, "Celular", dark);
            phone.layer = NpcLayer;
            phone.transform.SetPositionAndRotation(wrist.position + along * .1f, Quaternion.LookRotation(animator.transform.right, along));
            phone.transform.SetParent(wrist, true);
            Vector3 scale = wrist.lossyScale;
            phone.transform.localScale = new Vector3(.075f / scale.x, .15f / scale.y, .012f / scale.z);
            const float width = .5f;
            var bar = new GameObject("Llamada");
            bar.transform.SetParent(root.transform, false);
            bar.transform.localPosition = new Vector3(0f, 2.05f, 0f);
            var back = Shape(PrimitiveType.Quad, "Fondo", dark);
            back.transform.SetParent(bar.transform, false);
            back.transform.localScale = new Vector3(width + .04f, .09f, 1f);
            var fill = Shape(PrimitiveType.Quad, "Avance", Flat("Testigo_Barra", new Color(.95f, .2f, .15f)));
            fill.transform.SetParent(bar.transform, false);
            fill.transform.localScale = new Vector3(0f, .055f, 1f);
            phone.SetActive(false);
            bar.SetActive(false);
            var view = root.AddComponent<WitnessPhone>();
            view.Configure(phone, bar.transform, fill.transform, width);
            return view;
        }

        // Material de color plano sin luz (Data/NPC): se crea una vez y lo comparten todos los dobles.
        private static Material Flat(string name, Color color)
        {
            string path = "Assets/Party/Data/NPC/" + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material != null) return material;
            material = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { color = color };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        // Un estado por postura (mismo nombre que ReactionPose); entra cuando «Reaccion» vale su número. Levantarse entra
        // sin transición: la mezcla desde la caída la hace NpcRagdoll.
        private static AnimatorController Controller(string path, Dictionary<ReactionPose, Motion> motions)
        {
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);
            controller.AddParameter(NpcReactionAnimator.Parameter, AnimatorControllerParameterType.Int);
            var machine = controller.layers[0].stateMachine;
            foreach (ReactionPose pose in Enum.GetValues(typeof(ReactionPose)))
            {
                if (!motions.TryGetValue(pose, out var motion)) throw new InvalidOperationException("Falta el clip de la postura " + pose);
                var state = machine.AddState(pose.ToString());
                state.motion = motion;
                if (pose == ReactionPose.Quieto) machine.defaultState = state;
                bool getUp = pose == ReactionPose.LevantarseEspalda || pose == ReactionPose.LevantarseBoca;
                var enter = machine.AddAnyStateTransition(state);
                enter.hasExitTime = false; enter.duration = getUp ? 0f : .2f; enter.canTransitionToSelf = false;
                enter.AddCondition(AnimatorConditionMode.Equals, (int)pose, NpcReactionAnimator.Parameter);
            }
            return controller;
        }

        // Forma de npc_reaction_clips.json.
        [Serializable] private sealed class ClipManifest { public FileEntry[] files = Array.Empty<FileEntry>(); public RoleEntry[] roles = Array.Empty<RoleEntry>(); public ClipEntry[] clips = Array.Empty<ClipEntry>(); }
        [Serializable] private sealed class FileEntry { public string pack, file; }
        [Serializable] private sealed class RoleEntry { public string id, pack; }
        [Serializable] private sealed class ClipEntry { public string id; public bool loop; }
    }
}
