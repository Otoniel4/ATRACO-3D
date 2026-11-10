using System;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Alarma.Core.Editor
{
    // Clips hechos sobre el esqueleto del pack (build_action_clips.py, build_npc_reaction_clips.py) para cualquier
    // personaje del elenco: copia el clip con la ruta de huesos del personaje (cada uno nombra distinto su esqueleto) y
    // solo con giros, más la posición de cadera y pies, para no cambiar sus proporciones. Lo usan jugador y NPC.
    public static class ClipRemapper
    {
        // Huesos que además de girar se desplazan: la cadera al agacharse o caer y los pies al dar un paso o arrodillarse.
        private static readonly string[] Moved = { "Body", "Foot.L", "Foot.R" };

        // «Root» del pack dentro del personaje: el primer hueso con «Body» como hijo.
        public static Transform RootBone(Transform character)
            => character.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "Root" && t.Find("Body") != null);

        public static AnimationClip Remap(AnimationClip source, Transform animatorRoot, Transform rootBone, string path, bool loop)
        {
            string targetRoot = AnimationUtility.CalculateTransformPath(rootBone, animatorRoot);
            var bindings = AnimationUtility.GetCurveBindings(source).Where(b => b.type == typeof(Transform)).ToArray();
            // Prefijo hasta «Root» en el clip (depende de cómo Unity armó la jerarquía del FBX).
            string sourceRoot = bindings.Select(b => b.path).Where(p => p == "Root" || p.EndsWith("/Root", StringComparison.Ordinal))
                .OrderBy(p => p.Length).FirstOrDefault() ?? throw new InvalidOperationException("El clip " + source.name + " no anima Root.");
            var clip = new AnimationClip { name = source.name, frameRate = source.frameRate };
            foreach (var binding in bindings)
            {
                bool rotation = binding.propertyName.StartsWith("m_LocalRotation", StringComparison.Ordinal)
                                || binding.propertyName.StartsWith("localEulerAngles", StringComparison.Ordinal);
                bool moved = binding.propertyName.StartsWith("m_LocalPosition", StringComparison.Ordinal)
                             && Moved.Any(name => binding.path.EndsWith("/" + name, StringComparison.Ordinal));
                if ((!rotation && !moved) || !(binding.path == sourceRoot || binding.path.StartsWith(sourceRoot + "/", StringComparison.Ordinal))) continue;
                var copy = EditorCurveBinding.FloatCurve(targetRoot + binding.path.Substring(sourceRoot.Length), typeof(Transform), binding.propertyName);
                AnimationUtility.SetEditorCurve(clip, copy, AnimationUtility.GetEditorCurve(source, binding));
            }
            var settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = loop;
            AnimationUtility.SetAnimationClipSettings(clip, settings);
            return Save(clip, path);
        }

        // Importación genérica de un FBX de clips (el elenco no es Humanoid): un clip por toma, con el nombre que va
        // después de «|» y repetido en bucle si «loops» lo dice. Solo reimporta si algo cambió.
        public static void ConfigureImport(string path, Func<string, bool> loops)
        {
            var importer = AssetImporter.GetAtPath(path) as ModelImporter ?? throw new System.IO.FileNotFoundException("Falta el FBX de clips", path);
            var clips = importer.defaultClipAnimations.Select(take =>
            {
                take.name = take.takeName.Split('|').Last();
                take.loopTime = loops(take.name);
                return take;
            }).ToArray();
            bool ready = importer.animationType == ModelImporterAnimationType.Generic && importer.importAnimation
                         && importer.clipAnimations.Select(c => c.name + c.loopTime).SequenceEqual(clips.Select(c => c.name + c.loopTime));
            if (ready) return;
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            importer.importAnimation = true;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.clipAnimations = clips;
            importer.SaveAndReimport();
        }

        // Guarda un asset nuevo o pisa el existente conservando su GUID (quien lo referencia sigue apuntando a él).
        public static T Save<T>(T asset, string path) where T : UnityEngine.Object
        {
            var existing = AssetDatabase.LoadAssetAtPath<T>(path);
            if (existing == null) { AssetDatabase.CreateAsset(asset, path); return asset; }
            EditorUtility.CopySerialized(asset, existing);
            UnityEngine.Object.DestroyImmediate(asset);
            return existing;
        }
    }
}
