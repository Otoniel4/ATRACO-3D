using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewWorldCollision
    {
        public static void Attach(GameObject target,Mesh source,string folder,string id)
        {
            Vector3[] positions=source.vertices;int[] indices=source.triangles;bool large=false;
            for(int i=0;i<indices.Length;i+=3)
                if(MaximumEdge(positions[indices[i]],positions[indices[i+1]],positions[indices[i+2]])>200){large=true;break;}
            Mesh mesh=source;
            if(large)
            {
                var vertices=new List<Vector3>();var triangles=new List<int>();
                for(int i=0;i<indices.Length;i+=3)Split(positions[indices[i]],positions[indices[i+1]],positions[indices[i+2]],vertices,triangles);
                mesh=new Mesh{name="Physics_"+id,indexFormat=vertices.Count>65535?IndexFormat.UInt32:IndexFormat.UInt16};mesh.SetVertices(vertices);mesh.SetTriangles(triangles,0);mesh.RecalculateBounds();
                AssetDatabase.CreateAsset(mesh,folder+"/Data/Physics_"+id+".asset");
            }
            var collider=target.AddComponent<MeshCollider>();collider.sharedMesh=mesh;
        }
        private static float MaximumEdge(Vector3 a,Vector3 b,Vector3 c)=>Mathf.Sqrt(Mathf.Max((a-b).sqrMagnitude,Mathf.Max((b-c).sqrMagnitude,(c-a).sqrMagnitude)));
        private static void Split(Vector3 a,Vector3 b,Vector3 c,List<Vector3> vertices,List<int> triangles)
        {
            if(MaximumEdge(a,b,c)>200){Vector3 ab=(a+b)*.5f,bc=(b+c)*.5f,ca=(c+a)*.5f;Split(a,ab,ca,vertices,triangles);Split(ab,b,bc,vertices,triangles);Split(ca,bc,c,vertices,triangles);Split(ab,bc,ca,vertices,triangles);return;}
            int offset=vertices.Count;vertices.Add(a);vertices.Add(b);vertices.Add(c);triangles.Add(offset);triangles.Add(offset+1);triangles.Add(offset+2);
        }
    }
}
