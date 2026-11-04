using UnityEngine;
namespace Alarma.City.Playtest
{
    // Hoja corrediza: una persiana que sube o un portón que se corre de lado. Se abre cuando alguien la empuja
    // y vuelve sola cuando nadie la sostiene.
    public sealed class ReviewSlidingDoor:MonoBehaviour
    {
        private const float Lift=3.2f,HoldSeconds=4f,ReachDistance=2.2f,Speed=2f;
        [SerializeField] private Transform leaf,threshold;
        [SerializeField] private Vector3 travel=Vector3.up*Lift; // recorrido en el espacio del padre de la hoja
        private Vector3 closed;private float until,amount;
        public bool IsOpen=>amount>.05f;
        public void Configure(Transform panel,Transform gateway){Configure(panel,gateway,Vector3.up*Lift);}
        public void Configure(Transform panel,Transform gateway,Vector3 localTravel){leaf=panel;threshold=gateway;travel=localTravel;closed=leaf.localPosition;}
        private void Awake(){if(leaf!=null)closed=leaf.localPosition;}
        public bool InReach(Vector3 position){if(threshold==null)return false;Vector3 d=position-threshold.position;d.y=0;return d.sqrMagnitude<ReachDistance*ReachDistance;}
        public void Push()=>until=Time.time+HoldSeconds;
        private void Update(){if(leaf==null)return;float length=Mathf.Max(travel.magnitude,.01f);amount=Mathf.MoveTowards(amount,Time.time<until?length:0,Speed*Time.deltaTime);leaf.localPosition=closed+travel*(amount/length);}
    }
}
