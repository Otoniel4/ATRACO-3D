using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using Alarma.Animation;
using Alarma.Core.Editor;

namespace Alarma.Player.Editor
{
    // Pone los clips de uso de objetos en el Animator de cada protagonista. Los clips salen de Art/Characters/Animations
    // (build_action_clips.py): un FBX por esqueleto del pack (Men y Women) e item_action_clips.json, que dice cuál usa
    // cada personaje. Cada clip se copia con la ruta de huesos de ese personaje y solo con giros (más la posición de la
    // cadera y los pies), para no cambiar sus proporciones. Agrega dos capas que maneja ItemActionAnimator: «Acciones torso»
    // (máscara desde el abdomen, se puede caminar) y «Acciones cuerpo» (todo el cuerpo).
    public static class ItemActionAnimatorAssets
    {
        private const string Folder = "Assets/Party/Art/Characters/Animations";
        private const string ManifestPath = Folder + "/item_action_clips.json";

        public static void AddTo(IEnumerable<GameObject> roles)
        {
            if (!File.Exists(ManifestPath))
            {
                Debug.LogWarning("Faltan los clips de uso de objetos (build_action_clips.py): los objetos se usarán sin mover el cuerpo.");
                return;
            }
            var manifest = JsonUtility.FromJson<ClipManifest>(File.ReadAllText(ManifestPath));
            foreach (var file in manifest.files) ClipRemapper.ConfigureImport(Folder + "/" + file.file, name => manifest.clips.Any(c => c.id == name && c.loop));
            foreach (var role in roles) AddTo(role, manifest);
            AssetDatabase.SaveAssets();
        }

        private static void AddTo(GameObject role, ClipManifest manifest)
        {
            var animator = role.GetComponentInChildren<Animator>(true);
            if (animator == null || !(animator.runtimeAnimatorController is AnimatorController controller))
            {
                Debug.LogWarning("El rol " + role.name + " no tiene Animator Controller: queda sin clips de uso de objetos.", role);
                return;
            }
            var rootBone = ClipRemapper.RootBone(animator.transform)
                           ?? throw new InvalidOperationException("El rol " + role.name + " no tiene el esqueleto del pack (Root/Body).");
            string roleId = rootBone.parent != null && rootBone.parent.name.EndsWith("_Rig", StringComparison.Ordinal)
                ? rootBone.parent.name.Substring(0, rootBone.parent.name.Length - 4) : role.name.Replace("_Visual", "");
            string pack = manifest.roles.FirstOrDefault(r => r.id == roleId)?.pack ?? "Men";
            string source = Folder + "/" + manifest.files.First(f => f.pack == pack).file;
            var sourceClips = AssetDatabase.LoadAllAssetsAtPath(source).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__", StringComparison.Ordinal)).ToDictionary(c => c.name);
            string folder = Path.GetDirectoryName(AssetDatabase.GetAssetPath(controller)).Replace('\\', '/') + "/Acciones/" + roleId;
            Directory.CreateDirectory(folder);
            var clips = manifest.clips.ToDictionary(c => c.id, c => ClipRemapper.Remap(
                sourceClips.TryGetValue(c.id, out var clip) ? clip : throw new InvalidOperationException("Falta el clip " + c.id + " en " + source),
                animator.transform, rootBone, folder + "/" + c.id + ".anim", c.loop));
            var mask = TorsoMask(animator, rootBone, folder + "/Torso.mask");
            Rebuild(controller, manifest.clips, clips, mask);
            EditorUtility.SetDirty(controller);
        }

        // Máscara del torso: del abdomen hacia arriba (columna, brazos y cabeza); piernas y cadera siguen la locomoción.
        private static AvatarMask TorsoMask(Animator animator, Transform rootBone, string path)
        {
            var mask = new AvatarMask { name = "Torso" };
            mask.AddTransformPath(animator.transform, true);
            for (int i = 0; i < mask.transformCount; i++)
                mask.SetTransformActive(i, mask.GetTransformPath(i).Split('/').Contains("Abdomen"));
            return ClipRemapper.Save(mask, path);
        }

        private static void Rebuild(AnimatorController controller, ClipEntry[] entries, Dictionary<string, AnimationClip> clips, AvatarMask mask)
        {
            // Se quitan las capas y parámetros de una preparación anterior.
            for (int i = controller.layers.Length - 1; i >= 0; i--)
                if (controller.layers[i].name == ItemActionAnimator.TorsoLayer || controller.layers[i].name == ItemActionAnimator.BodyLayer) controller.RemoveLayer(i);
            foreach (var parameter in controller.parameters.Where(p => p.name == ItemActionAnimator.UsingParameter || p.name == ItemActionAnimator.ActionParameter).ToArray())
                controller.RemoveParameter(parameter);
            controller.AddParameter(ItemActionAnimator.UsingParameter, AnimatorControllerParameterType.Bool);
            controller.AddParameter(ItemActionAnimator.ActionParameter, AnimatorControllerParameterType.Int);
            AddLayer(controller, ItemActionAnimator.TorsoLayer, mask, entries.Where(e => !e.fullBody), clips);
            AddLayer(controller, ItemActionAnimator.BodyLayer, null, entries.Where(e => e.fullBody), clips);
        }

        // Estado vacío de espera y un estado por clip: entra con Usando y su número en Accion, sale al soltar Usando.
        // Write Defaults apagado: la capa con peso 0 o en espera no pisa la pose de la locomoción.
        private static void AddLayer(AnimatorController controller, string name, AvatarMask mask, IEnumerable<ClipEntry> entries, Dictionary<string, AnimationClip> clips)
        {
            var machine = new AnimatorStateMachine { name = name, hideFlags = HideFlags.HideInHierarchy };
            AssetDatabase.AddObjectToAsset(machine, controller);
            var waiting = machine.AddState("Sin acción");
            waiting.writeDefaultValues = false;
            machine.defaultState = waiting;
            foreach (var entry in entries)
            {
                var state = machine.AddState(entry.id);
                state.motion = clips[entry.id];
                state.writeDefaultValues = false;
                var enter = machine.AddAnyStateTransition(state);
                enter.hasExitTime = false; enter.duration = .12f; enter.canTransitionToSelf = false;
                enter.AddCondition(AnimatorConditionMode.If, 0, ItemActionAnimator.UsingParameter);
                enter.AddCondition(AnimatorConditionMode.Equals, entry.animationId, ItemActionAnimator.ActionParameter);
                var leave = state.AddTransition(waiting);
                leave.hasExitTime = false; leave.duration = .15f;
                leave.AddCondition(AnimatorConditionMode.IfNot, 0, ItemActionAnimator.UsingParameter);
            }
            controller.AddLayer(new AnimatorControllerLayer
            {
                name = name, stateMachine = machine, avatarMask = mask, defaultWeight = 0f, blendingMode = AnimatorLayerBlendingMode.Override,
            });
        }

        // Forma de item_action_clips.json.
        [Serializable] private sealed class ClipManifest { public string rig; public FileEntry[] files = Array.Empty<FileEntry>(); public RoleEntry[] roles = Array.Empty<RoleEntry>(); public ClipEntry[] clips = Array.Empty<ClipEntry>(); }
        [Serializable] private sealed class FileEntry { public string pack, file; }
        [Serializable] private sealed class RoleEntry { public string id, pack; }
        [Serializable] private sealed class ClipEntry { public string id; public int animationId; public bool fullBody, loop; }
    }
}
