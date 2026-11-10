using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Alarma.Core.Editor
{
    // Clips de locomoción de la Universal Animation Library de Quaternius (CC0), ya pasados al esqueleto del pack por
    // retarget_ual_clips.py. Para un personaje del elenco entrega cada clip adaptado a su esqueleto (ClipRemapper) y con
    // los pies pegados al final de sus piernas. Lo usan peatones, clientes, jugador y dobles de reacción; si faltan los
    // archivos devuelve null y cada uno sigue con los clips de su propio modelo.
    public static class LocomotionClips
    {
        private const string Folder = "Assets/Party/Art/Characters/Animations";
        private const string ManifestPath = Folder + "/locomotion_clips.json";
        // Nombre con que cada Animator pide su locomoción → clip del manifiesto.
        private static readonly Dictionary<string, string> Modes = new Dictionary<string, string>
        {
            ["Idle"] = "Quieto", ["Walk"] = "Caminar", ["Run"] = "Trotar", ["Sprint"] = "Correr",
        };

        // Buscador de clips para este personaje: acepta el modo («Walk») o el id del manifiesto («Caminar»).
        // Los clips adaptados se guardan en «outputFolder».
        public static Func<string, AnimationClip> For(Animator animator, string outputFolder)
        {
            if (!File.Exists(ManifestPath)) return null;
            var rootBone = ClipRemapper.RootBone(animator.transform);
            if (rootBone == null) return null;
            var manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(ManifestPath));
            foreach (var file in manifest.files) ClipRemapper.ConfigureImport(Folder + "/" + file.file, name => manifest.clips.Any(c => c.id == name && c.loop));
            string rig = rootBone.parent != null ? rootBone.parent.name : animator.name;
            string id = rig.EndsWith("_Rig", StringComparison.Ordinal) ? rig.Substring(0, rig.Length - 4) : rig;
            string pack = manifest.roles.FirstOrDefault(r => r.id == id)?.pack ?? "Men";
            string source = Folder + "/" + manifest.files.First(f => f.pack == pack).file;
            var packClips = AssetDatabase.LoadAllAssetsAtPath(source).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToDictionary(c => c.name);
            var legs = Legs(rootBone);
            var done = new Dictionary<string, AnimationClip>();
            return request =>
            {
                string name = Modes.TryGetValue(request, out var mapped) ? mapped : request;
                if (done.TryGetValue(name, out var ready)) return ready;
                var entry = manifest.clips.FirstOrDefault(c => c.id == name);
                if (entry == null || !packClips.TryGetValue(name, out var clip)) return null;
                Directory.CreateDirectory(outputFolder);
                var remapped = ClipRemapper.Remap(clip, animator.transform, rootBone, outputFolder + "/" + name + ".anim", entry.loop);
                PinFeet(remapped, animator, legs);
                return done[name] = remapped;
            };
        }

        // Cada pie con su canilla y dónde queda respecto de ella con el cuerpo como viene en el modelo. Hay que pedirlo
        // antes de posar al personaje con ningún clip.
        private static (Transform foot, Transform shin, Vector3 offset)[] Legs(Transform rootBone)
        {
            Transform Bone(string name) => rootBone.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name)
                                           ?? throw new InvalidOperationException("Falta el hueso " + name + " bajo " + rootBone.name);
            return new[] { "L", "R" }.Select(side =>
            {
                Transform foot = Bone("Foot." + side), shin = Bone("LowerLeg." + side);
                return (foot, shin, shin.InverseTransformPoint(foot.position));
            }).ToArray();
        }

        // En el elenco los pies cuelgan de la raíz y el clip los ubica por posición, medida en el esqueleto del pack.
        // Cada personaje tiene piernas de otro largo, así que aquí se reescribe la posición de cada pie, cuadro a
        // cuadro, al final de su pierna. La pose del personaje queda como estaba.
        private static void PinFeet(AnimationClip clip, Animator animator, (Transform foot, Transform shin, Vector3 offset)[] legs)
        {
            var bones = animator.GetComponentsInChildren<Transform>(true);
            var before = bones.Select(b => (b.localPosition, b.localRotation)).ToArray();
            var curves = legs.Select(_ => new[] { new AnimationCurve(), new AnimationCurve(), new AnimationCurve() }).ToArray();
            int frames = Mathf.Max(1, Mathf.RoundToInt(clip.length * clip.frameRate));
            for (int f = 0; f <= frames; f++)
            {
                float time = f / clip.frameRate;
                clip.SampleAnimation(animator.gameObject, time);
                for (int i = 0; i < legs.Length; i++)
                {
                    Vector3 local = legs[i].foot.parent.InverseTransformPoint(legs[i].shin.TransformPoint(legs[i].offset));
                    for (int axis = 0; axis < 3; axis++) curves[i][axis].AddKey(time, local[axis]);
                }
            }
            for (int b = 0; b < bones.Length; b++) bones[b].SetLocalPositionAndRotation(before[b].localPosition, before[b].localRotation);
            string[] properties = { "m_LocalPosition.x", "m_LocalPosition.y", "m_LocalPosition.z" };
            for (int i = 0; i < legs.Length; i++)
            {
                string path = AnimationUtility.CalculateTransformPath(legs[i].foot, animator.transform);
                for (int axis = 0; axis < 3; axis++)
                    AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve(path, typeof(Transform), properties[axis]), curves[i][axis]);
            }
            EditorUtility.SetDirty(clip);
        }

        // Forma de locomotion_clips.json.
        [Serializable] private sealed class Manifest { public FileEntry[] files = Array.Empty<FileEntry>(); public RoleEntry[] roles = Array.Empty<RoleEntry>(); public ClipEntry[] clips = Array.Empty<ClipEntry>(); }
        [Serializable] private sealed class FileEntry { public string pack, file; }
        [Serializable] private sealed class RoleEntry { public string id, pack; }
        [Serializable] private sealed class ClipEntry { public string id; public bool loop; }
    }
}
