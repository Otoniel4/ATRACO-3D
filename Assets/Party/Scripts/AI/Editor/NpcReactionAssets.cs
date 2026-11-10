using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
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
        private const string PhoneFolder = "Assets/Party/Art/Props";
        // Agarres del celular (mismos valores que GRIPS en build_npc_reaction_clips.py): centro desde la muñeca hacia los
        // dedos, fuera de la palma y hacia el índice. Al grabar va de pie entre los dedos y el pulgar; al hablar, a lo
        // largo de la palma. Las manos del elenco son grandes: se agranda un poco.
        private static readonly Vector3 FilmGrip = new Vector3(.128f, .055f, .045f), CallGrip = new Vector3(.13f, .028f, .03f);
        private const float PhoneScale = 1.15f;

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
                // Levantarse entra sin transición: la mezcla desde la caída la hace NpcRagdoll.
                animator.runtimeAnimatorController = PoseController.Create(folder + "/Reaccion_" + id + ".controller", NpcReactionAnimator.Parameter, motions,
                    ReactionPose.Quieto, pose => pose == ReactionPose.LevantarseEspalda || pose == ReactionPose.LevantarseBoca);
                // Cuerpo con física armado sobre el reposo: las articulaciones nacen con el cuerpo de pie y los brazos abajo.
                Own("Idle").SampleAnimation(animator.gameObject, 0f);
                var ragdoll = root.AddComponent<NpcRagdoll>();
                ragdoll.Build(animator, capsule);
                var poses = root.AddComponent<NpcReactionAnimator>();
                poses.Configure(animator);
                var motor = root.AddComponent<NpcFleeMotor>();
                var reactions = root.AddComponent<NpcReactions>();
                reactions.Configure(settings, noise, poses, motor, ragdoll, reports, MakePhone(root, animator, rootBone, id));
                return PrefabUtility.SaveAsPrefabAsset(root, output + "/Prefabs/Reaccion_" + id + ".prefab").GetComponent<NpcReactions>();
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        // Celular en la mano derecha (modelo de build_npc_phone.py, con la funda de un color por personaje) y barra de la
        // llamada sobre la cabeza del testigo, apagados hasta que grabe (WitnessPhone). Sus dos agarres siguen la misma
        // regla que los clips Grabar y Llamar (build_npc_reaction_clips.py): los ejes de la mano salen de la muñeca y los
        // nudillos, y los dedos de los clips cierran alrededor de ese lugar.
        private static WitnessPhone MakePhone(GameObject root, Animator animator, Transform rootBone, string id)
        {
            Transform Bone(string name) => rootBone.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name)
                                           ?? throw new InvalidOperationException("Falta el hueso " + name + " en " + animator.name);
            Transform wrist = Bone("Wrist.R");
            // Los huesos «2» de cada dedo nacen en los nudillos.
            Vector3 along = (Bone("Middle2.R").position - wrist.position).normalized;
            Vector3 across = (Bone("Index2.R").position - Bone("Pinky2.R").position).normalized;
            Vector3 palm = Vector3.Cross(along, across).normalized;
            if (Vector3.Dot(palm, -animator.transform.right) < 0f) palm = -palm; // en reposo la palma derecha mira al cuerpo
            var manifest = JsonUtility.FromJson<PhoneManifest>(File.ReadAllText(PhoneFolder + "/Prop_NpcPhone.json"));
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(PhoneFolder + "/" + manifest.model) ?? throw new FileNotFoundException("Falta el celular (build_npc_phone.py)", manifest.model);
            var phone = new GameObject("Celular") { layer = NpcLayer };
            phone.transform.SetParent(wrist, true);
            // Lugar del celular respecto de la muñeca: pantalla (+Z del modelo) hacia «screen» y borde de arriba (+Y) hacia «up».
            Pose Grip(Vector3 offset, Vector3 screen, Vector3 up)
            {
                phone.transform.SetPositionAndRotation(wrist.position + along * offset.x + palm * offset.y + across * offset.z, Quaternion.LookRotation(screen, up));
                return new Pose(phone.transform.localPosition, phone.transform.localRotation);
            }
            Pose call = Grip(CallGrip, palm, along);    // hablar: sobre la palma, a lo largo de la mano
            Pose film = Grip(FilmGrip, -along, across); // grabar: de pie, pantalla hacia la muñeca, arriba hacia el índice
            Vector3 scale = wrist.lossyScale;
            phone.transform.localScale = new Vector3(PhoneScale / scale.x, PhoneScale / scale.y, PhoneScale / scale.z);
            var model = (GameObject)PrefabUtility.InstantiatePrefab(asset);
            model.transform.SetParent(phone.transform, false);
            int tint = (id.Aggregate(17, (hash, letter) => unchecked(hash * 31 + letter)) & int.MaxValue) % Math.Max(1, manifest.cases.Length);
            foreach (var renderer in model.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.gameObject.layer = NpcLayer;
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.sharedMaterials = renderer.sharedMaterials.Select(source =>
                {
                    var entry = manifest.materials.FirstOrDefault(m => source != null && m.name == source.name);
                    if (entry == null) return source;
                    bool isCase = entry.name == manifest.caseMaterial && manifest.cases.Length > 0;
                    return Flat(isCase ? entry.name + "_" + tint : entry.name, Hex(isCase ? manifest.cases[tint] : entry.color), entry.unlit);
                }).ToArray();
            }
            GameObject Quad(string name, Material material)
            {
                var shape = GameObject.CreatePrimitive(PrimitiveType.Quad);
                shape.name = name;
                UnityEngine.Object.DestroyImmediate(shape.GetComponent<Collider>());
                var renderer = shape.GetComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                return shape;
            }
            const float width = .5f;
            var bar = new GameObject("Llamada");
            bar.transform.SetParent(root.transform, false);
            bar.transform.localPosition = new Vector3(0f, 2.05f, 0f);
            var back = Quad("Fondo", Flat("Testigo_Celular", new Color(.08f, .09f, .11f)));
            back.transform.SetParent(bar.transform, false);
            back.transform.localScale = new Vector3(width + .04f, .09f, 1f);
            var fill = Quad("Avance", Flat("Testigo_Barra", new Color(.95f, .2f, .15f)));
            fill.transform.SetParent(bar.transform, false);
            fill.transform.localScale = new Vector3(0f, .055f, 1f);
            phone.SetActive(false);
            bar.SetActive(false);
            var view = root.AddComponent<WitnessPhone>();
            view.Configure(phone, bar.transform, fill.transform, width, film, call);
            return view;
        }

        private static Color Hex(string value) => ColorUtility.TryParseHtmlString("#" + value, out var color) ? color : Color.magenta;

        // Material de color plano (Data/NPC), sin luz o con ella: se crea una vez y lo comparten todos los dobles.
        private static Material Flat(string name, Color color, bool unlit = true)
        {
            string path = "Assets/Party/Data/NPC/" + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find(unlit ? "Universal Render Pipeline/Unlit" : "Universal Render Pipeline/Lit"));
                if (!unlit) material.SetFloat("_Smoothness", .25f);
                AssetDatabase.CreateAsset(material, path);
            }
            if (material.color != color) { material.color = color; EditorUtility.SetDirty(material); } // sigue al json del modelo
            return material;
        }

        // Forma de Prop_NpcPhone.json.
        [Serializable] private sealed class PhoneManifest { public string model = "", caseMaterial = ""; public string[] cases = Array.Empty<string>(); public PhoneMaterial[] materials = Array.Empty<PhoneMaterial>(); }
        [Serializable] private sealed class PhoneMaterial { public string name = "", color = ""; public bool unlit; }

        // Forma de npc_reaction_clips.json.
        [Serializable] private sealed class ClipManifest { public FileEntry[] files = Array.Empty<FileEntry>(); public RoleEntry[] roles = Array.Empty<RoleEntry>(); public ClipEntry[] clips = Array.Empty<ClipEntry>(); }
        [Serializable] private sealed class FileEntry { public string pack, file; }
        [Serializable] private sealed class RoleEntry { public string id, pack; }
        [Serializable] private sealed class ClipEntry { public string id; public bool loop; }
    }
}
