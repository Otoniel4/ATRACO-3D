using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewCharacterAssets
    {
        public const string Source="Assets/Party/Art/BlenderScripts/PlaytestR8~";
        public static void Prepare(string folder,string prepared,CharacterManifest characters)
        {
            foreach(string kind in new[]{"Characters","Doors"})
            {
                Directory.CreateDirectory(folder+"/Art/"+kind);
                foreach(string path in Directory.GetFiles(Source+"/export/"+kind,"*.fbx"))File.Copy(path,folder+"/Art/"+kind+"/"+Path.GetFileName(path),true);
            }
            File.Copy(Source+"/city_map.png",folder+"/Art/city_map.png");AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            CityLifeImport.ConfigureCharacters(folder,characters);
            var colors=JsonUtility.FromJson<ColorManifest>(File.ReadAllText(Source+"/door_materials.json"));
            foreach(var c in colors.materials)
            {
                var m=new Material(Shader.Find("Universal Render Pipeline/Lit")){name=c.name};m.SetColor("_BaseColor",new Color(c.r,c.g,c.b,c.a));m.SetFloat("_Metallic",c.metallic);m.SetFloat("_Smoothness",1-c.roughness);
                if(c.a<1){m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);m.SetFloat("_Cull",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.SetOverrideTag("RenderType","Transparent");m.renderQueue=3000;}
                AssetDatabase.CreateAsset(m,folder+"/Materials/"+c.name+".mat");
            }
            foreach(string kind in new[]{"Characters","Doors"})foreach(string file in Directory.GetFiles(folder+"/Art/"+kind,"*.fbx"))
            {
                string path=file.Replace('\\','/');var importer=(ModelImporter)AssetImporter.GetAtPath(path);var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                foreach(var original in model.GetComponentsInChildren<Renderer>(true).SelectMany(r=>r.sharedMaterials).Where(m=>m!=null).Distinct())
                {
                    string source=kind=="Doors"?folder:prepared;var material=AssetDatabase.LoadAssetAtPath<Material>(source+"/Materials/"+original.name+".mat");
                    if(material!=null)importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),original.name),material);
                }
                importer.SaveAndReimport();
                if(kind=="Characters")ReviewBuildAcceptance.ValidateAnimation(path);
            }
            var texture=(TextureImporter)AssetImporter.GetAtPath(folder+"/Art/city_map.png");texture.textureCompression=TextureImporterCompression.Uncompressed;texture.mipmapEnabled=false;texture.wrapMode=TextureWrapMode.Clamp;texture.maxTextureSize=2048;texture.SaveAndReimport();
        }
    }
}
