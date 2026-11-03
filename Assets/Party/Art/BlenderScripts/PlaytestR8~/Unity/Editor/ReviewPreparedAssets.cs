using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewPreparedAssets
    {
        private const string Schema="playtest-assets-r7-1";
        [Serializable] private sealed class Ready{public string version;public bool complete;}
        public static void MarkReady(string folder)=>File.WriteAllText(folder+"/AssetsReady.json",JsonUtility.ToJson(new Ready{version=Schema,complete=true},true));
        public static string Find(WorldBuildData world)
        {
            const string root="Assets/Party/Generated";if(!Directory.Exists(root))return null;
            foreach(string folder in Directory.GetDirectories(root,"AlarmaPrueba_*").OrderByDescending(p=>p,StringComparer.Ordinal))
            {
                bool prepared=false;string checkpoint=folder+"/AssetsReady.json",failure=folder+"/BuildFailure.json",report=folder+"/BuildReport.json";
                if(File.Exists(report)){var state=JsonUtility.FromJson<ReviewBuildRecord>(File.ReadAllText(report));prepared=state!=null && state.complete && state.version!=null && (state.version.StartsWith("playtest-r7-",StringComparison.Ordinal) || state.version.StartsWith("playtest-r8-",StringComparison.Ordinal));}
                if(File.Exists(checkpoint)){var state=JsonUtility.FromJson<Ready>(File.ReadAllText(checkpoint));prepared=state!=null && state.complete && state.version==Schema;}
                if(!prepared && File.Exists(failure))
                {
                    var state=JsonUtility.FromJson<ReviewBuildRecord>(File.ReadAllText(failure));
                    prepared=state!=null && state.version=="playtest-r7-1" && !state.complete && state.error!=null && state.error.Contains("Cannot create a new scene additively with an untitled scene unsaved");
                }
                if(!prepared || !Directory.Exists(folder+"/Materials") || Directory.GetFiles(folder+"/Materials","*.mat").Length==0)continue;
                bool valid=world.cells.All(c=>Exists(folder+"/Art/"+c.file)) && world.doors.All(d=>Exists(folder+"/Art/"+d.file));
                if(!valid)continue;
                var cast=ReviewBuildAssets.Characters();if(cast.characters.Any(c=>!Exists(folder+"/Art/Characters/"+c.id+".fbx")))continue;
                if(world.shops.Any(s=>!Exists(folder+"/Art/Props/"+s.product+".fbx")) || !Exists(folder+"/Art/Props/CashNote.fbx") || !Exists(folder+"/Art/Props/Receipt.fbx"))continue;
                return folder.Replace('\\','/');
            }
            return null;
        }
        private static bool Exists(string path)=>File.Exists(path) && !string.IsNullOrEmpty(AssetDatabase.AssetPathToGUID(path.Replace('\\','/')));
    }
}
