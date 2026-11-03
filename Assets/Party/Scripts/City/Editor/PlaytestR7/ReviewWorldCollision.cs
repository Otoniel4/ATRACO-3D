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
            var vertices=new List<Vector3>();var triangles=new List<int>();var shared=new Dictionary<Vector3,int>();
            foreach(var part in parts)
            {
                Matrix4x4 transform=root.worldToLocalMatrix*part.transform.localToWorldMatrix;bool reverse=transform.determinant<0;var positions=part.sharedMesh.vertices;var indices=part.sharedMesh.triangles;
                for(int i=0;i<indices.Length;i+=3)
                    Split(transform.MultiplyPoint3x4(positions[indices[i]]),transform.MultiplyPoint3x4(positions[indices[i+(reverse?2:1)]]),transform.MultiplyPoint3x4(positions[indices[i+(reverse?1:2)]]),vertices,triangles,shared);
            }
            if(vertices.Count==0)return;
            var mesh=new Mesh{name="Physics_"+id,indexFormat=vertices.Count>65535?IndexFormat.UInt32:IndexFormat.UInt16};mesh.SetVertices(vertices);mesh.SetTriangles(triangles,0);mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,folder+"/Data/Physics_"+id+".asset");
            var collider=new GameObject("Física de "+id).AddComponent<MeshCollider>();collider.transform.SetParent(root,false);collider.sharedMesh=mesh;
        }
        private static void Split(Vector3 a,Vector3 b,Vector3 c,List<Vector3> vertices,List<int> triangles,Dictionary<Vector3,int> shared)
        {
            if(Mathf.Max((a-b).sqrMagnitude,Mathf.Max((b-c).sqrMagnitude,(c-a).sqrMagnitude))>40000)
            {Vector3 ab=(a+b)*.5f,bc=(b+c)*.5f,ca=(c+a)*.5f;Split(a,ab,ca,vertices,triangles,shared);Split(ab,b,bc,vertices,triangles,shared);Split(ca,bc,c,vertices,triangles,shared);Split(ab,bc,ca,vertices,triangles,shared);return;}
            triangles.Add(Index(a,vertices,shared));triangles.Add(Index(b,vertices,shared));triangles.Add(Index(c,vertices,shared));
        }
        // Los triángulos vecinos reutilizan el mismo vértice: la malla física ocupa varias veces menos en disco y al cocinarse.
        private static int Index(Vector3 p,List<Vector3> vertices,Dictionary<Vector3,int> shared)
        {
            if(!shared.TryGetValue(p,out int index)){index=vertices.Count;vertices.Add(p);shared.Add(p,index);}
            return index;
        }
    }
}
