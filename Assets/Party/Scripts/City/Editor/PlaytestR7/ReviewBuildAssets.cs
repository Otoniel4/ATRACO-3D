using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewBuildAssets
    {
        public const string Source="Assets/Party/Art/BlenderScripts/PlaytestR9~";
        public static void CheckSources(WorldBuildData world)
        {
            if(world==null || world.cells==null || world.cells.Length<32 || world.shops==null || world.shops.Length!=5)throw new InvalidOperationException("La preparación de ciudad R9 está incompleta.");
            foreach(var cell in world.cells)if(!File.Exists((cell.reuse?ReviewWorldAssets.Legacy:Source)+"/export/"+cell.file))throw new FileNotFoundException("Falta parte de ciudad",cell.file);
            foreach(var door in world.doors)if(!File.Exists(Source+"/export/"+door.file))throw new FileNotFoundException("Falta puerta",door.file);
            if(!File.Exists(CityLifeImport.ReviewFolder+"/traffic_graph.json"))throw new FileNotFoundException("Falta el grafo comprobado R6.");
        }
        public static void PrepareOutput(string folder)
        {
            foreach(string child in new[]{"Art","Data","Materials","Controllers","Prefabs","Scenes","Resources"})Directory.CreateDirectory(folder+"/"+child);
            AssetDatabase.Refresh();
        }
        public static void Copy(string folder)
        {
            PrepareOutput(folder);
            AssetDatabase.StartAssetEditing();
            try
            {
                CopyTree(Source+"/export",folder+"/Art");
                foreach(string name in new[]{"Vehicles","Weapons","Props"})
                    foreach(string path in Directory.GetFiles("Assets/Party/Art/"+name,"*.fbx",SearchOption.TopDirectoryOnly))
                    {string target=folder+"/Art/"+name+"/"+Path.GetFileName(path);if(!File.Exists(target)){Directory.CreateDirectory(Path.GetDirectoryName(target));File.Copy(path,target);}}
            }
            finally{AssetDatabase.StopAssetEditing();}
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }
        private static void CopyTree(string source,string target)
        {
            foreach(string path in Directory.GetFiles(source,"*.fbx",SearchOption.AllDirectories))
            {string relative=path.Substring(source.Length).TrimStart('/','\\');string destination=target+"/"+relative.Replace('\\','/');Directory.CreateDirectory(Path.GetDirectoryName(destination));File.Copy(path,destination,false);}
        }
        public static CharacterManifest Characters()=>JsonUtility.FromJson<CharacterManifest>(File.ReadAllText(ReviewCharacterAssets.Source+"/characters.json"));
        public static void ConfigureModels(string folder,CharacterManifest characters)
        {
            CityLifeImport.ConfigureCharacters(folder,characters);
            foreach(string file in Directory.GetFiles(folder+"/Art/World","*.fbx"))
            {
                var importer=(ModelImporter)AssetImporter.GetAtPath(file.Replace('\\','/'));if(importer==null)throw new InvalidOperationException("No se importó "+file);
                // Colores planos sin mapas de normales: las tangentes solo ocuparían disco y memoria.
                importer.importAnimation=false;importer.isReadable=true;importer.globalScale=1;importer.importTangents=ModelImporterTangents.None;importer.SaveAndReimport();
            }
        }
        public static void Materials(string folder)
        {
            var entries=new Dictionary<string,ColorEntry>(StringComparer.Ordinal);
            foreach(string path in new[]{CityLifeImport.ReviewFolder+"/materials.json",Source+"/materials.json",Source+"/prop_materials.json"})
                foreach(var entry in JsonUtility.FromJson<ColorManifest>(File.ReadAllText(path)).materials)entries[entry.name]=entry;
            foreach(string path in Directory.GetFiles("Assets/Party/Art/Materials","*Palette.json"))
            {
                var palette=JsonUtility.FromJson<OriginalPalette>(File.ReadAllText(path));if(palette?.colors==null)continue;
                foreach(var entry in palette.colors)
                {
                    if(!ColorUtility.TryParseHtmlString("#"+entry.hex,out Color c))continue;
                    string name="Alarma_"+entry.name;entries[name]=new ColorEntry{name=name,r=c.r,g=c.g,b=c.b,a=1,roughness=.88f};
                }
            }
            Shader lit=Shader.Find("Universal Render Pipeline/Lit");if(lit==null)throw new InvalidOperationException("No se encontró URP/Lit.");
            Directory.CreateDirectory(folder+"/Shaders");File.Copy(CityLifeImport.ReviewFolder+"/Unity/SharedSupport~/TreeWindURP.shader",folder+"/Shaders/TreeWindURP.shader");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);Shader wind=AssetDatabase.LoadAssetAtPath<Shader>(folder+"/Shaders/TreeWindURP.shader");
            var materials=new Dictionary<string,Material>(StringComparer.Ordinal);
            foreach(var e in entries.Values)
            {
                bool plant=e.name.StartsWith("WindTree_",StringComparison.Ordinal) || e.name.StartsWith("WindPlant_",StringComparison.Ordinal);
                var m=new Material(plant && wind!=null?wind:lit){name=e.name,enableInstancing=true};m.SetColor("_BaseColor",new Color(e.r,e.g,e.b,e.a));
                if(m.HasProperty("_Metallic"))m.SetFloat("_Metallic",e.metallic);if(m.HasProperty("_Smoothness"))m.SetFloat("_Smoothness",1-e.roughness);
                if(e.a<.99f && !plant)
                {
                    m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);m.SetFloat("_Cull",0);
                    m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.SetOverrideTag("RenderType","Transparent");m.SetShaderPassEnabled("ShadowCaster",false);m.renderQueue=(int)RenderQueue.Transparent;
                }
                string safe=string.Concat(e.name.Select(c=>Path.GetInvalidFileNameChars().Contains(c)?'_':c));AssetDatabase.CreateAsset(m,folder+"/Materials/"+safe+".mat");materials[e.name]=m;
            }
            string[] files=Directory.GetFiles(folder+"/Art","*.fbx",SearchOption.AllDirectories);
            for(int i=0;i<files.Length;i++)
            {
                if(EditorUtility.DisplayCancelableProgressBar("Preparar Alarma","Materiales: "+Path.GetFileName(files[i]),.2f+.25f*i/files.Length))throw new OperationCanceledException();
                string path=files[i].Replace('\\','/');var importer=(ModelImporter)AssetImporter.GetAtPath(path);var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if(model==null || importer==null)throw new InvalidOperationException("Modelo no disponible: "+path);
                foreach(var original in model.GetComponentsInChildren<Renderer>(true).SelectMany(r=>r.sharedMaterials).Where(m=>m!=null).Distinct())
                    if(materials.TryGetValue(original.name,out var target))importer.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),original.name),target);
                importer.SaveAndReimport();
            }
        }
        public static PedestrianActor[] Actors(string folder,string assetFolder,CharacterManifest characters)
        {return characters.characters.Select(c=>CityLifeSceneBuilder.MakePrefab(assetFolder,folder,c)).ToArray();}
        public static GameObject Visual(string folder,CharacterEntry entry,PedestrianActor actor)
        {
            var model=actor.GetComponentInChildren<Animator>(true).gameObject;var copy=new GameObject(entry.id+"_Visual");var imported=UnityEngine.Object.Instantiate(model);imported.transform.SetParent(copy.transform,false);
            try{return PrefabUtility.SaveAsPrefabAsset(copy,folder+"/Prefabs/"+entry.id+"_Visual.prefab");}
            finally{UnityEngine.Object.DestroyImmediate(copy);}
        }
        [Serializable] private sealed class OriginalPalette{public OriginalColor[] colors=Array.Empty<OriginalColor>();}
        [Serializable] private sealed class OriginalColor{public string name,hex;}
    }
}
