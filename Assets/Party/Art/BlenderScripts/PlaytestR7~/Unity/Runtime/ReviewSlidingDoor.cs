using UnityEngine;
namespace Alarma.City.Playtest
{
    public sealed class ReviewSlidingDoor:MonoBehaviour
    {
        [SerializeField] private Transform leaf,threshold;
        private Vector3 closed;private float until,amount;
        public void Configure(Transform panel,Transform gateway){leaf=panel;threshold=gateway;closed=leaf.localPosition;}
        private void Awake(){if(leaf!=null)closed=leaf.localPosition;}
        public void RequestNear(Vector3 position){if(threshold==null)return;Vector3 d=position-threshold.position;d.y=0;if(d.sqrMagnitude<12.25f)until=Time.time+1.5f;}
        private void Update(){if(leaf==null)return;amount=Mathf.MoveTowards(amount,Time.time<until?3.2f:0,2*Time.deltaTime);leaf.localPosition=closed+Vector3.up*amount;}
    }
}
