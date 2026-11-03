using System.Linq;
using UnityEngine;
namespace Alarma.City.Playtest.Editor
{
    public sealed class ReviewTreePlacement
    {
        public int Relocated=>0;
        public Vector3 Place(Transform node,Mesh mesh,Vector3 origin,float height)
        {
            var vertices=mesh.vertices;float floor=vertices.Min(v=>node.TransformPoint(v).y);Vector3 center=Vector3.zero;int count=0;
            foreach(var vertex in vertices){Vector3 p=node.TransformPoint(vertex);if(p.y<floor+.15f){center+=p;count++;}}
            return center/Mathf.Max(1,count)+Vector3.up*(height*.5f);
        }
    }
}
