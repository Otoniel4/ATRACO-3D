using UnityEngine;
namespace Alarma.City.Playtest
{
    // Abre visualmente el techo al entrar; facilita revisar interiores con cámara en tercera persona.
    public sealed class ReviewRoof:MonoBehaviour
    {
        private Transform observer;private Renderer target;private Collider barrier;private float nextCheck;
        public void Configure(Transform focus){observer=focus;target=GetComponent<Renderer>();barrier=GetComponent<Collider>();}
        private void Update()
        {
            if(observer==null || target==null || Time.unscaledTime<nextCheck)return;nextCheck=Time.unscaledTime+.2f;
            Bounds b=target.bounds;Vector3 p=observer.position;bool inside=Mathf.Abs(p.x-b.center.x)<b.extents.x+.4f && Mathf.Abs(p.z-b.center.z)<b.extents.z+.4f && p.y<b.max.y+2;
            target.enabled=!inside;if(barrier!=null)barrier.enabled=!inside;
        }
    }
}
