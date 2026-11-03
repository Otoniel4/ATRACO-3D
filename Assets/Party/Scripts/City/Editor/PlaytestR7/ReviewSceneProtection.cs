using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewSceneProtection
    {
        [Serializable] private sealed class Entry{public string originalName,originalPath,backup;public bool assignedPath;}
        [Serializable] private sealed class Snapshot{public Entry[] scenes;}
        public static string Capture()
        {
            string folder=null;var entries=new List<Entry>();
            for(int i=0;i<SceneManager.sceneCount;i++)
            {
                Scene scene=SceneManager.GetSceneAt(i);if(!scene.isLoaded)continue;
                var mode=SceneBackupPolicy.Choose(!string.IsNullOrEmpty(scene.path),scene.isDirty);if(mode==SceneBackupMode.None)continue;
                if(folder==null){folder="Assets/Party/Scenes/Backups/BeforePlaytest_"+DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");Directory.CreateDirectory(folder);AssetDatabase.Refresh();}
                string original=scene.path;string label=scene.name;string path=AssetDatabase.GenerateUniqueAssetPath(folder+"/Scene_"+i+".unity");
                bool copy=mode==SceneBackupMode.PreserveOriginalPath;
                if(!EditorSceneManager.SaveScene(scene,path,copy))throw new IOException("No se pudo respaldar la escena "+label+". La preparación se detuvo antes de importar modelos.");
                entries.Add(new Entry{originalName=label,originalPath=original,backup=path,assignedPath=!copy});
            }
            for(int i=0;i<SceneManager.sceneCount;i++)
            {
                var scene=SceneManager.GetSceneAt(i);if(scene.isLoaded && string.IsNullOrEmpty(scene.path))throw new InvalidOperationException("La escena "+scene.name+" sigue sin ruta guardada. No se inició la importación.");
            }
            if(folder!=null)
            {
                File.WriteAllText(folder+"/OpenScenes.json",JsonUtility.ToJson(new Snapshot{scenes=entries.ToArray()},true));AssetDatabase.Refresh();Debug.Log("Alarma: escenas abiertas respaldadas en "+folder);
            }
            return folder;
        }
    }
}
