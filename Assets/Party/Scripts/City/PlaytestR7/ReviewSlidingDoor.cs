using UnityEngine;
namespace Alarma.City.Playtest
{
    // Persiana de una hoja: sube cuando alguien la abre y baja sola cuando nadie la sostiene.
    public sealed class ReviewSlidingDoor:MonoBehaviour
    {
        private const float Lift=3.2f,HoldSeconds=2.5f,ReachDistance=2.2f;
        [SerializeField] private Transform leaf,threshold;
        private Vector3 closed;private float until,amount;
        public bool IsOpen=>amount>.05f;
        public void Configure(Transform panel,Transform gateway){leaf=panel;threshold=gateway;closed=leaf.localPosition;}
        private void Awake(){if(leaf!=null)closed=leaf.localPosition;}
        public bool InReach(Vector3 position){if(threshold==null)return false;Vector3 d=position-threshold.position;d.y=0;return d.sqrMagnitude<ReachDistance*ReachDistance;}
        public void Push()=>until=Time.time+HoldSeconds;
        private void Update(){if(leaf==null)return;amount=Mathf.MoveTowards(amount,Time.time<until?Lift:0,2*Time.deltaTime);leaf.localPosition=closed+Vector3.up*amount;}
    }
}
