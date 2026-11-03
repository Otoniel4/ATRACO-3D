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
        private const string Version="playtest-r8-1";
        private const string Latest="Assets/Party/Generated/AlarmaPlaytestReady.json";
        private static bool building;
        [MenuItem("Alarma/Crear y probar juego",false,0)]
        public static void BuildAndPlay()
        {
            if(building || EditorApplication.isPlayingOrWillChangePlaymode)return;
            var previous=SceneManager.GetActiveScene();Scene stage=default;string folder=null,assetFolder=null;building=true;
            try
            {
                ReviewSceneProtection.Capture();
                if(File.Exists(Latest))
                {
                    var ready=JsonUtility.FromJson<ReviewBuildRecord>(File.ReadAllText(Latest));
                    if(ready.complete && ready.version==Version && File.Exists(ready.scene)){EditorSceneManager.OpenScene(ready.scene,OpenSceneMode.Single);StartPlay();return;}
                }
                var world=JsonUtility.FromJson<WorldBuildData>(File.ReadAllText(ReviewCharacterAssets.Source+"/world.json"));ReviewBuildAssets.CheckSources(world);
                // Se valida la creación de escena antes del trabajo pesado de importación.
                stage=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);SceneManager.SetActiveScene(stage);
                folder="Assets/Party/Generated/AlarmaPrueba_"+DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");ReviewBuildAssets.PrepareOutput(folder);
                var characters=ReviewBuildAssets.Characters();assetFolder=ReviewPreparedAssets.Find(world);
                if(assetFolder==null)
                {
                    assetFolder=folder;EditorUtility.DisplayProgressBar("Preparar Alarma","Copiando e importando los modelos. La primera preparación tarda.",.02f);
                    ReviewBuildAssets.Copy(folder);ReviewBuildAssets.ConfigureModels(folder,characters);ReviewBuildAssets.Materials(folder);ReviewPreparedAssets.MarkReady(folder);
                }
                else Debug.Log("Alarma: se reutilizan modelos y materiales ya preparados en "+assetFolder);
                ReviewCharacterAssets.Prepare(folder,assetFolder,characters);
                var worldData=ReviewBuildWorld.Prepare(folder,assetFolder,world);
                var actors=ReviewBuildAssets.Actors(folder,folder,characters);
                EditorUtility.DisplayProgressBar("Preparar Alarma","Jugador, NPC, puertas, interiores y catálogo",.85f);ReviewBuildScene.Populate(folder,assetFolder,world,worldData,characters,actors);
                ReviewBuildAcceptance.Validate(stage,folder);
                string path=folder+"/Scenes/Alarma_Prueba_Completa.unity";
                if(!EditorSceneManager.SaveScene(stage,path))throw new InvalidOperationException("No se pudo guardar la escena completa.");
                AssetDatabase.SaveAssets();var record=new ReviewBuildRecord{complete=true,version=Version,scene=path,folder=folder,assetFolder=assetFolder,worldParts=world.cells.Length,characters=characters.characters.Length,shops=world.shops.Length,models=AssetDatabase.LoadAssetAtPath<ReviewCatalog>(folder+"/Data/ReviewCatalog.asset").Models.Length};
                File.WriteAllText(folder+"/BuildReport.json",JsonUtility.ToJson(record,true));File.WriteAllText(Latest,JsonUtility.ToJson(record,true));AssetDatabase.Refresh();
                for(int i=SceneManager.sceneCount-1;i>=0;i--){var other=SceneManager.GetSceneAt(i);if(other!=stage)EditorSceneManager.CloseScene(other,true);}
                Debug.Log("Alarma: prueba local completa preparada. Ciudad 4 × 4 km, jugador, 18 modelos de personaje, interiores y compras de NPC. M: mapa; F6: modelos; V: vuelo. Red y misiones pendientes.");StartPlay();
            }
            catch(Exception error)
            {
                if(stage.IsValid() && stage.isLoaded)EditorSceneManager.CloseScene(stage,true);
                if(previous.IsValid() && previous.isLoaded)SceneManager.SetActiveScene(previous);
                if(folder!=null)File.WriteAllText(folder+"/BuildFailure.json",JsonUtility.ToJson(new ReviewBuildRecord{complete=false,version=Version,error=error.ToString(),folder=folder,assetFolder=assetFolder},true));
                if(!(error is OperationCanceledException)){Debug.LogException(error);EditorUtility.DisplayDialog("Preparación de Alarma interrumpida",error.Message+"\n\nTus escenas anteriores siguen disponibles. Consulta Console y BuildFailure.json.","Cerrar");}
            }
            finally{building=false;EditorUtility.ClearProgressBar();}
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
