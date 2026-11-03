using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewWorldCollision
    {
        // Hornea las transformaciones calibradas en la malla física; evita colliders con escala reflejada.
        public static void Build(Transform root,List<MeshFilter> parts,string folder,string id)
        {
            var vertices=new List<Vector3>();var triangles=new List<int>();
            foreach(var part in parts)
            {
                Matrix4x4 transform=root.worldToLocalMatrix*part.transform.localToWorldMatrix;bool reverse=transform.determinant<0;var positions=part.sharedMesh.vertices;var indices=part.sharedMesh.triangles;
                for(int i=0;i<indices.Length;i+=3)
                    Split(transform.MultiplyPoint3x4(positions[indices[i]]),transform.MultiplyPoint3x4(positions[indices[i+(reverse?2:1)]]),transform.MultiplyPoint3x4(positions[indices[i+(reverse?1:2)]]),vertices,triangles);
            }
            if(vertices.Count==0)return;
            var mesh=new Mesh{name="Physics_"+id,indexFormat=vertices.Count>65535?IndexFormat.UInt32:IndexFormat.UInt16};mesh.SetVertices(vertices);mesh.SetTriangles(triangles,0);mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,folder+"/Data/Physics_"+id+".asset");
            var collider=new GameObject("Física de "+id).AddComponent<MeshCollider>();collider.transform.SetParent(root,false);collider.sharedMesh=mesh;
        }
        private static void Split(Vector3 a,Vector3 b,Vector3 c,List<Vector3> vertices,List<int> triangles)
        {
            if(Mathf.Max((a-b).sqrMagnitude,Mathf.Max((b-c).sqrMagnitude,(c-a).sqrMagnitude))>40000)
            {Vector3 ab=(a+b)*.5f,bc=(b+c)*.5f,ca=(c+a)*.5f;Split(a,ab,ca,vertices,triangles);Split(ab,b,bc,vertices,triangles);Split(ca,bc,c,vertices,triangles);Split(ab,bc,ca,vertices,triangles);return;}
            int n=vertices.Count;vertices.Add(a);vertices.Add(b);vertices.Add(c);triangles.Add(n);triangles.Add(n+1);triangles.Add(n+2);
        }
    }
}
