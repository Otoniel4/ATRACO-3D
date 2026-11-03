using UnityEngine;

namespace Alarma.AI.CityLife
{
    [ExecuteAlways]
    [RequireComponent(typeof(MeshFilter),typeof(MeshRenderer))]
    public sealed class CityVegetationBounds : MonoBehaviour
    {
        private MeshRenderer target;
        private void OnEnable()
        {
            target=GetComponent<MeshRenderer>();Mesh mesh=GetComponent<MeshFilter>().sharedMesh;if(mesh==null)return;
            Vector3 scale=transform.lossyScale;float minimum=Mathf.Max(.001f,Mathf.Min(Mathf.Abs(scale.x),Mathf.Min(Mathf.Abs(scale.y),Mathf.Abs(scale.z))));
            Bounds bounds=mesh.bounds;bounds.Expand(2f/minimum);target.localBounds=bounds;
        }
        private void OnDisable(){if(target!=null)target.ResetLocalBounds();}
    }
}
