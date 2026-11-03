using System;
using System.IO;
using System.Linq;
using UnityEngine;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewLobbyBuilder
    {
        [Serializable] private sealed class Manifest{public PointData[] spawns;}
        public static void Create(string folder,Transform player,float[] spawn)
        {
            var root=new GameObject("Escondite · inicio de la banda");var manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText(ReviewCharacterAssets.Source+"/lobby.json"));
            var slots=manifest.spawns.Select((p,i)=>{var t=new GameObject("Compañero "+(i+1)).transform;t.SetParent(root.transform,false);t.position=ReviewBuildWorld.Vector(p.v);return t;}).ToArray();root.AddComponent<ReviewLobby>().Configure(slots);
        }
    }
}
