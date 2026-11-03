using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace Alarma.AI.CityLife.Editor
{
    [Serializable] public sealed class ColorEntry { public string name; public float r,g,b,a,metallic,roughness; }
    [Serializable] public sealed class ColorManifest { public ColorEntry[] materials; }
    [Serializable] public sealed class CharacterEntry { public string id; public string rig; }
    [Serializable] public sealed class CharacterManifest { public CharacterEntry[] characters; }

    public static class CityLifeImport
    {
        public const string ReviewFolder = "Assets/Party/Art/BlenderScripts/CityLifeR6~";
        public static void CopyAssets(string destination)
        {
            string source = ReviewFolder + "/export";
            if (!Directory.Exists(source)) throw new DirectoryNotFoundException("Falta la entrega R6: " + source);
            foreach (string file in Directory.GetFiles(source, "*.fbx", SearchOption.AllDirectories))
            {
                string relative = file.Substring(source.Length).TrimStart('/', '\\');
                if (relative.Replace('\\','/').StartsWith("Map/",StringComparison.Ordinal)) continue;
                string target = destination + "/Art/" + relative.Replace('\\','/');
                Directory.CreateDirectory(Path.GetDirectoryName(target)); File.Copy(file, target, false);
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }
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
        public static void CreateMaterials(string destination)
        {
            var data = JsonUtility.FromJson<ColorManifest>(File.ReadAllText(ReviewFolder + "/materials.json"));
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) throw new InvalidOperationException("No está disponible URP/Lit en el proyecto actual.");
            Shader wind=Shader.Find("Alarma/Vegetation/Natural Wind R3");
            if(wind==null)
            {
                Directory.CreateDirectory(destination+"/Shaders");
                foreach(string file in new[]{"TreeWindURP.shader","TreeWindURP.shader.meta"})
                    File.Copy(ReviewFolder+"/Unity/SharedSupport~/"+file,destination+"/Shaders/"+file,false);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                wind=AssetDatabase.LoadAssetAtPath<Shader>(destination+"/Shaders/TreeWindURP.shader");
            }
            foreach (ColorEntry color in data.materials)
            {
                bool vegetation=color.name.StartsWith("WindPlant_",StringComparison.Ordinal)||color.name.StartsWith("WindTree_",StringComparison.Ordinal);
                var material = new Material(vegetation&&wind!=null?wind:shader) { name = color.name };
                material.enableInstancing=true;
                material.SetColor("_BaseColor",new Color(color.r,color.g,color.b,color.a));
                if(material.HasProperty("_Metallic"))material.SetFloat("_Metallic",color.metallic);
                if(material.HasProperty("_Smoothness"))material.SetFloat("_Smoothness",1f-color.roughness);
                if (color.a < .99f)
                {
                    material.SetFloat("_Surface",1); material.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);
                    material.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha); material.SetFloat("_ZWrite",0);
                    material.SetFloat("_SrcBlendAlpha",1);material.SetFloat("_DstBlendAlpha",(float)BlendMode.OneMinusSrcAlpha);material.SetFloat("_Cull",0);
                    material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); material.SetOverrideTag("RenderType","Transparent");
                    material.SetShaderPassEnabled("ShadowCaster",false);
                    material.renderQueue = (int)RenderQueue.Transparent;
                }
                string path = destination + "/Materials/" + SafeName(color.name) + ".mat";
                AssetDatabase.CreateAsset(material,path);
            }
            foreach (string path in AssetDatabase.FindAssets("t:Model",new[]{destination+"/Art"}).Select(AssetDatabase.GUIDToAssetPath))
            {
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                if (importer == null) continue;
                GameObject model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if(model==null)continue;
                foreach (Material original in model.GetComponentsInChildren<Renderer>(true).SelectMany(r=>r.sharedMaterials).Where(m=>m!=null).Distinct())
                {
                    var material = AssetDatabase.LoadAssetAtPath<Material>(destination+"/Materials/"+SafeName(original.name)+".mat");
                    if (material != null) importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),original.name),material);
                }
                importer.SaveAndReimport();
            }
        }
        private static string SafeName(string name) => string.Concat(name.Select(c => Path.GetInvalidFileNameChars().Contains(c) ? '_' : c));
    }
}
