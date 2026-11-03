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
    public static class ReviewBuildScene
    {
        public static void Populate(string folder,string assetFolder,WorldBuildData world,WorldReviewData streaming,CharacterManifest characters,PedestrianActor[] actors)
        {
            var visuals=new Dictionary<string,GameObject>(StringComparer.Ordinal);
            for(int i=0;i<characters.characters.Length;i++)visuals.Add(characters.characters[i].id,ReviewBuildAssets.Visual(folder,characters.characters[i],actors[i]));
            var roleIds=new[]{"Player01_Thief","Player02_Hacker","Player03_Distractor","Player04_Muscle"};var roles=roleIds.Select(id=>visuals[id]).ToArray();
            var civilians=characters.characters.Select((c,i)=>new {Entry=c,Actor=actors[i]}).Where(x=>x.Entry.id.StartsWith("NPC",StringComparison.Ordinal) && int.Parse(x.Entry.id.Substring(3,2))<=10).OrderBy(x=>x.Entry.id,StringComparer.Ordinal).Select(x=>x.Actor).ToArray();
            if(civilians.Length!=10)throw new InvalidOperationException("Se requieren diez civiles distintos.");
            var inputObject=new GameObject("Controles de la prueba");var input=inputObject.AddComponent<ReviewInput>();
            var playerObject=new GameObject("Jugador de revisión");playerObject.layer=30;
            var controller=playerObject.AddComponent<CharacterController>();controller.height=1.75f;controller.center=new Vector3(0,.875f,0);controller.radius=.24f;controller.skinWidth=.025f;controller.stepOffset=.28f;controller.slopeLimit=50;controller.minMoveDistance=0;
            var player=playerObject.AddComponent<ReviewPlayerMotor>();var character=playerObject.AddComponent<ReviewCharacterView>();
            var cameraObject=new GameObject("Main Camera");cameraObject.tag="MainCamera";var camera=cameraObject.AddComponent<Camera>();cameraObject.AddComponent<AudioListener>();camera.cullingMask=~(1<<31);camera.farClipPlane=280;camera.nearClipPlane=.08f;camera.backgroundColor=new Color(.64f,.78f,.88f);
            var cameraRig=cameraObject.AddComponent<ReviewCamera>();var cityObject=new GameObject("Ciudad por sectores");var stream=cityObject.AddComponent<WorldReviewStream>();
            Vector3 spawn=streaming.Destinations.First(p=>p.Id=="Minimarket").Position;
            player.Configure(input,cameraRig,stream,spawn);cameraRig.Configure(input,player.transform);stream.Configure(streaming,cameraObject.transform);character.Configure(input,player,roles);
            var doors=ReviewBuildWorld.Doors(folder,world,player.transform);var shops=ReviewBuildActivities.Create(folder,assetFolder,world,civilians,doors);
            var settings=ScriptableObject.CreateInstance<PedestrianSettings>();settings.BrowseSeconds=1.5f;settings.PaySeconds=.9f;settings.ActivationRadius=120;settings.DeactivationRadius=180;AssetDatabase.CreateAsset(settings,folder+"/Data/PedestrianSettings.asset");
            var populationObject=new GameObject("Población local");var director=populationObject.AddComponent<CityPopulationDirector>();var authority=populationObject.AddComponent<LocalCityLifeAuthority>();director.Configure(settings,civilians,shops,player.transform,authority,null);
            populationObject.AddComponent<ReviewActivityGate>().Configure(stream,player.transform,director);
            var streetPopulation=ReviewStreetBuilder.Create(folder,civilians,player.transform,stream);
            foreach(var traffic in shops.Select(s=>s.Traffic))traffic.ConfigureBlocker(player.transform);
            var sunObject=new GameObject("Sol");var sun=sunObject.AddComponent<Light>();sun.type=LightType.Directional;sun.intensity=1.25f;sun.shadows=LightShadows.Soft;sun.cullingMask=~(1<<31);sunObject.transform.rotation=Quaternion.Euler(48,-30,0);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.58f,.64f,.69f);RenderSettings.sun=sun;RenderSettings.fog=true;RenderSettings.fogMode=FogMode.Linear;RenderSettings.fogColor=new Color(.65f,.76f,.83f);RenderSettings.fogStartDistance=130;RenderSettings.fogEndDistance=245;
            var catalog=BuildCatalog(folder,assetFolder,characters,visuals);var previewObject=new GameObject("Inspección de modelos");var preview=previewObject.AddComponent<ReviewModelPreview>();
            var ui=new GameObject("Interfaz de revisión").AddComponent<ReviewInterface>();ui.Configure(input,player,cameraRig,character,stream,catalog,preview,director,shops);
            ui.ConfigureStreet(streetPopulation);
            new GameObject("Registro de prueba").AddComponent<ReviewRuntimeChecks>().Configure(folder,stream,player,character,director,streetPopulation);
            Selection.activeGameObject=playerObject;
        }
        private static ReviewCatalog BuildCatalog(string folder,string assetFolder,CharacterManifest characters,Dictionary<string,GameObject> visuals)
        {
            var models=new List<ReviewModel>();
            foreach(var entry in characters.characters)models.Add(new ReviewModel{Id=entry.id,Label=entry.id.Replace('_',' '),Category=ReviewCategory.Character,Prefab=visuals[entry.id]});
            foreach(var item in new[]{("Vehicles",ReviewCategory.Vehicle),("Weapons",ReviewCategory.Equipment),("Props",ReviewCategory.Prop)})
                foreach(string file in Directory.GetFiles(assetFolder+"/Art/"+item.Item1,"*.fbx").OrderBy(x=>x,StringComparer.Ordinal))
                {string id=Path.GetFileNameWithoutExtension(file);var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(file.Replace('\\','/'));if(prefab!=null)models.Add(new ReviewModel{Id=id,Label=id.Replace('_',' '),Category=item.Item2,Prefab=prefab});}
            var data=ScriptableObject.CreateInstance<ReviewCatalog>();data.Models=models.ToArray();AssetDatabase.CreateAsset(data,folder+"/Data/ReviewCatalog.asset");return data;
        }
    }
}
