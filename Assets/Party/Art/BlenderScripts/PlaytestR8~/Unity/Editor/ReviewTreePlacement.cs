using System;
using System.IO;
using System.Linq;
using UnityEngine;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    // Comprueba la geometría importada en sus coordenadas mundiales, incluidas las superficies de estacionamiento.
    public sealed class ReviewTreePlacement
    {
        [Serializable] private sealed class Polygon{public PointData[] points;}
        [Serializable] private sealed class Roads{public Polygon[] polygons;}
        private readonly Polygon[] polygons;
        public int Relocated{get;private set;}
        public ReviewTreePlacement(){polygons=JsonUtility.FromJson<Roads>(File.ReadAllText(ReviewCharacterAssets.Source+"/road_areas.json")).polygons;}
        private static bool Inside(Polygon polygon,Vector3 p)
        {
            bool inside=false;for(int i=0,j=polygon.points.Length-1;i<polygon.points.Length;j=i++)
            {var a=polygon.points[i].v;var b=polygon.points[j].v;if((a[2]>p.z)!=(b[2]>p.z) && p.x<(b[0]-a[0])*(p.z-a[2])/(b[2]-a[2])+a[0])inside=!inside;}
            return inside;
        }
        private bool IsRoad(Vector3 p)=>polygons.Any(polygon=>Inside(polygon,p));
        public Vector3 Place(Transform node,Mesh mesh,Vector3 origin,float height)
        {
            var vertices=mesh.vertices;float floor=vertices.Min(v=>node.TransformPoint(v).y);Vector3 center=Vector3.zero;int count=0;
            foreach(var vertex in vertices){Vector3 p=node.TransformPoint(vertex);if(p.y<floor+.15f){center+=p;count++;}}
            center/=Mathf.Max(1,count);Vector3 global=center+origin;
            if(IsRoad(global))
            {
                bool found=false;Vector3 destination=global;
                for(float radius=2;radius<=40 && !found;radius+=2)for(int i=0;i<32;i++)
                {
                    Vector3 candidate=global+new Vector3(Mathf.Cos(i*Mathf.PI/16),0,Mathf.Sin(i*Mathf.PI/16))*radius;
                    if(IsRoad(candidate) || IsRoad(candidate+Vector3.right) || IsRoad(candidate-Vector3.right) || IsRoad(candidate+Vector3.forward) || IsRoad(candidate-Vector3.forward))continue;
                    destination=candidate;found=true;break;
                }
                if(!found)throw new InvalidOperationException("No se encontró un borde libre para el árbol "+node.name);
                Vector3 delta=destination-global;node.position+=delta;center+=delta;Relocated++;
            }
            return center+Vector3.up*(height*.5f);
        }
    }
}
