using System;
using System.Linq;
using UnityEditor;

namespace Alarma.AI.CityLife.Editor
{
    [Serializable] public sealed class ColorEntry { public string name; public float r,g,b,a,metallic,roughness,emission; }
    [Serializable] public sealed class ColorManifest { public ColorEntry[] materials; }
    [Serializable] public sealed class CharacterEntry { public string id; public string rig; }
    [Serializable] public sealed class CharacterManifest { public CharacterEntry[] characters; }

    // Importación de los personajes del elenco: rig genérico y clips con los nombres que usa el Animator.
    public static class CityLifeImport
    {
        public static void ConfigureCharacters(string destination, CharacterManifest characters)
        {
            foreach (CharacterEntry entry in characters.characters)
            {
                string path = destination + "/Art/Characters/" + entry.id + ".fbx";
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                if (importer == null) throw new InvalidOperationException("No se importó " + path);
                importer.importAnimation = true; importer.animationType = ModelImporterAnimationType.Generic;
                importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                importer.motionNodeName = ""; importer.globalScale = 1f;
                ModelImporterClipAnimation[] clips = importer.defaultClipAnimations;
                foreach (ModelImporterClipAnimation clip in clips)
                {
                    string mode = Modes.FirstOrDefault(m => Matches(clip.name,m));
                    if (mode == null) continue;
                    clip.lockRootRotation=true;clip.lockRootHeightY=true;clip.lockRootPositionXZ=true;clip.keepOriginalOrientation=true;clip.keepOriginalPositionXZ=true;
                    clip.name = mode; clip.loopTime = mode != "Pay"; clip.loopPose = mode != "Pay";
                }
                importer.clipAnimations = clips; importer.SaveAndReimport();
            }
        }
        internal static readonly string[] Modes = { "Idle", "Walk", "Run", "Browse", "Pay", "CarryWalk" };
        internal static bool Matches(string name, string mode) => name == mode || name.EndsWith("_" + mode, StringComparison.Ordinal) || name.EndsWith("|" + mode, StringComparison.Ordinal);
    }
}
