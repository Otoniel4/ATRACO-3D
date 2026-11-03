using System;
using Alarma.City.Playtest.Editor;
static class ScenePolicyChecks
{
    static void Check(bool value,string message){if(!value)throw new Exception(message);}
    static void Main()
    {
        Check(SceneBackupPolicy.Choose(false,true)==SceneBackupMode.AssignSavedPath,"Untitled con cambios debe recibir una ruta, no continuar después de Don't Save.");
        Check(SceneBackupPolicy.Choose(false,false)==SceneBackupMode.AssignSavedPath,"Una escena limpia pero sin nombre también bloquea Additive.");
        Check(SceneBackupPolicy.Choose(true,true)==SceneBackupMode.PreserveOriginalPath,"Los cambios en una escena existente deben ir a una copia, sin sobrescribir el original.");
        Check(SceneBackupPolicy.Choose(true,false)==SceneBackupMode.None,"Una escena guardada sin cambios no necesita escritura.");
        var paths=new[]{"Assets/SampleScene.unity","",""};var dirty=new[]{false,true,false};int assigned=0;
        for(int i=0;i<paths.Length;i++)if(SceneBackupPolicy.Choose(paths[i].Length>0,dirty[i])==SceneBackupMode.AssignSavedPath){paths[i]="Assets/Party/Scenes/Backups/Scene_"+i+".unity";assigned++;}
        Check(assigned==2 && Array.TrueForAll(paths,p=>p.Length>0),"Todas las escenas abiertas deben tener ruta antes de crear otra aditivamente.");
        Console.WriteLine("SCENE_POLICY_PASS: 5 casos de protección y precondición de escenas.");
    }
}
