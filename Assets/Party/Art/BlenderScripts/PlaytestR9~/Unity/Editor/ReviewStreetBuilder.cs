using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewStreetBuilder
    {
        [Serializable] private sealed class Route{public float[] center;public PointData[] points;}
        [Serializable] private sealed class Routes{public Route[] routes;}
        public static StreetPopulationDirector Create(string folder,PedestrianActor[] civilians,Transform observer,WorldReviewStream stream)
        {
            var source=JsonUtility.FromJson<Routes>(File.ReadAllText(ReviewCharacterAssets.Source+"/street_routes.json"));
            var data=ScriptableObject.CreateInstance<StreetCrowdData>();data.Routes=source.routes.Select(r=>new StreetRoute{Center=ReviewBuildWorld.Vector(r.center),Points=r.points.Select(p=>ReviewBuildWorld.Vector(p.v)).ToArray()}).ToArray();
            AssetDatabase.CreateAsset(data,folder+"/Data/StreetCrowd.asset");var population=new GameObject("Peatones de las aceras").AddComponent<StreetPopulationDirector>();population.Configure(data,civilians,observer,stream);return population;
        }
    }
}
