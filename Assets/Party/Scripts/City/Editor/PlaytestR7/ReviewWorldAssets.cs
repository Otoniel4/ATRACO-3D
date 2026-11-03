using System;
using System.IO;
using UnityEditor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewWorldAssets
    {
        public const string Legacy="Assets/Party/Art/BlenderScripts/PlaytestR7~";
        public static void Complete(string folder,string prepared,WorldBuildData world)
        {
            if(prepared!=null)return;
            foreach(var cell in world.cells)if(cell.reuse){string destination=folder+"/Art/"+cell.file;Directory.CreateDirectory(Path.GetDirectoryName(destination));File.Copy(Legacy+"/export/"+cell.file,destination);}
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }
    }
}
