using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
namespace Alarma.City.Playtest.Editor
{
    // Única entrada de usuario. Publica la escena solo después de prepararla y comprobarla completa.
    public static class AlarmaPlaytestBuilder
    {
        private const string Version="playtest-r9-3";
        private const string Generated="Assets/Party/Generated";
        private const string Latest=Generated+"/AlarmaPlaytestReady.json";
        private const string LastFailure=Generated+"/AlarmaPlaytestFailure.json";
        private static bool building;
        [MenuItem("Alarma/Crear y probar juego",false,0)]
        public static void BuildAndPlay()
        {
            if(building || EditorApplication.isPlayingOrWillChangePlaymode)return;
            var previous=SceneManager.GetActiveScene();Scene stage=default;string folder=null,assetFolder=null;building=true;
            try
            {
                ReviewSceneProtection.Capture();
                ReviewSpatialImport.Begin();
                if(File.Exists(Latest))
                {
                    var ready=JsonUtility.FromJson<ReviewBuildRecord>(File.ReadAllText(Latest));
                    if(ready.complete && ready.version==Version && File.Exists(ready.scene)){EditorSceneManager.OpenScene(ready.scene,OpenSceneMode.Single);StartPlay();return;}
                }
                var world=JsonUtility.FromJson<WorldBuildData>(File.ReadAllText(ReviewCharacterAssets.Source+"/world.json"));ReviewBuildAssets.CheckSources(world);
                // Se valida la creación de escena antes del trabajo pesado de importación.
                stage=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);SceneManager.SetActiveScene(stage);
                folder="Assets/Party/Generated/AlarmaPrueba_"+DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");ReviewBuildAssets.PrepareOutput(folder);
                var characters=ReviewBuildAssets.Characters();assetFolder=folder;
                ReviewBuildAssets.Copy(folder);
                ReviewBuildAssets.ConfigureModels(folder,characters);ReviewBuildAssets.Materials(folder);
                ReviewCharacterAssets.Prepare(folder,folder,characters);
                var worldData=ReviewBuildWorld.Prepare(folder,assetFolder,world);
                var actors=ReviewBuildAssets.Actors(folder,folder,characters);
                EditorUtility.DisplayProgressBar("Preparar Alarma","Jugador, NPC, puertas, interiores y catálogo",.85f);ReviewBuildScene.Populate(folder,assetFolder,world,worldData,characters,actors);
                string path=folder+"/Scenes/Alarma_Prueba_Completa.unity";
                if(!EditorSceneManager.SaveScene(stage,path))throw new InvalidOperationException("No se pudo guardar la preparación.");
                ReviewPhysicalAcceptance.Validate(stage,folder,world,worldData);
                ReviewBuildAcceptance.Validate(stage,folder);
                ReviewSpatialImport.Save(folder);
                if(!EditorSceneManager.SaveScene(stage,path))throw new InvalidOperationException("No se pudo guardar la escena completa.");
                AssetDatabase.SaveAssets();var record=new ReviewBuildRecord{complete=true,version=Version,scene=path,folder=folder,assetFolder=assetFolder,worldParts=world.cells.Length,characters=characters.characters.Length,shops=world.shops.Length,models=AssetDatabase.LoadAssetAtPath<ReviewCatalog>(folder+"/Data/ReviewCatalog.asset").Models.Length};
                File.WriteAllText(folder+"/BuildReport.json",JsonUtility.ToJson(record,true));File.WriteAllText(Latest,JsonUtility.ToJson(record,true));AssetDatabase.Refresh();
                for(int i=SceneManager.sceneCount-1;i>=0;i--){var other=SceneManager.GetSceneAt(i);if(other!=stage)EditorSceneManager.CloseScene(other,true);}
                RemoveOtherBuilds(folder);
                Debug.Log("Alarma R9: inicio en el escondite y cinco comercios preparados. Ciudad 3 × 3 km, jugador, 18 modelos de personaje, interiores y compras de NPC. M: mapa; F6: modelos; V: vuelo. Red y misiones pendientes.");StartPlay();
            }
            catch(Exception error)
            {
                if(stage.IsValid() && stage.isLoaded)EditorSceneManager.CloseScene(stage,true);
                if(previous.IsValid() && previous.isLoaded)SceneManager.SetActiveScene(previous);
                // El informe queda fuera de la carpeta fallida, que se borra para no acumular gigas de importaciones.
                Directory.CreateDirectory(Generated);File.WriteAllText(LastFailure,JsonUtility.ToJson(new ReviewBuildRecord{complete=false,version=Version,error=error.ToString(),folder=folder,assetFolder=assetFolder},true));
                if(folder!=null && AssetDatabase.IsValidFolder(folder))AssetDatabase.DeleteAsset(folder);
                if(!(error is OperationCanceledException)){Debug.LogException(error);EditorUtility.DisplayDialog("Preparación de Alarma interrumpida",error.Message+"\n\nTus escenas anteriores siguen disponibles. Consulta Console y "+LastFailure+".","Cerrar");}
            }
            finally{building=false;EditorUtility.ClearProgressBar();}
        }
        // Solo se conserva la preparación vigente; las anteriores son copias regenerables de varios GB.
        private static void RemoveOtherBuilds(string keep)
        {
            foreach(string old in AssetDatabase.GetSubFolders(Generated))
            {
                string name=Path.GetFileName(old);
                if(old!=keep && (name.StartsWith("AlarmaPrueba_",StringComparison.Ordinal) || name.StartsWith("CityLifeR6_",StringComparison.Ordinal)))AssetDatabase.DeleteAsset(old);
            }
            if(File.Exists(LastFailure) && !AssetDatabase.DeleteAsset(LastFailure))File.Delete(LastFailure);
        }
        [MenuItem("Alarma/Crear y probar juego",true)]
        private static bool CanBuild()=>!building && !EditorApplication.isCompiling && !EditorApplication.isUpdating && !EditorApplication.isPlayingOrWillChangePlaymode;
        private static void StartPlay()
        {
            EditorApplication.delayCall+=()=>
            {
                if(EditorApplication.isCompiling || EditorApplication.isUpdating){StartPlay();return;}
                EditorApplication.ExecuteMenuItem("Window/General/Game");EditorApplication.EnterPlaymode();
            };
        }
    }
}
