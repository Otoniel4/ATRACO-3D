using UnityEngine;
using UnityEngine.AI;
namespace Alarma.AI.CityLife
{
    [RequireComponent(typeof(NavMeshAgent))]
    public sealed class PedestrianMovement : MonoBehaviour,IPedestrianMotor
    {
        private CityTrafficController traffic;private int id;private bool registered;private Vector3 start,end,last;
        private Vector3 doorOffset;
        private CapsuleCollider capsule;
        private readonly RaycastHit[] approachHits = new RaycastHit[12];
        private readonly Collider[] approachOverlaps = new Collider[12];
        public float Speed{get;private set;}
        public bool AtStepEnd => (transform.position - end - doorOffset).sqrMagnitude < .0001f;
        public bool HasDoorOffset => doorOffset.sqrMagnitude > .000001f;
        internal bool UsesTraffic(CityTrafficController controller) => registered && traffic == controller;
        public bool HasArrived=>registered && traffic.Arrived(id);
        public bool Place(int actorId,Vector3 position,CityTrafficController controller)
        {
            Suspend();GetComponent<NavMeshAgent>().enabled=false;id=actorId;traffic=controller;
            capsule = GetComponent<CapsuleCollider>();
            registered=traffic!=null && traffic.Register(id,this,position);return registered;
        }
        public void Snap(Vector3 point){transform.position=point;start=end=last=point;doorOffset=Vector3.zero;Speed=0;}
        public void SetStep(Vector3 point)
        {
            // La reserva de la misma celda no devuelve los pies al centro mientras la mano empuja.
            if (HasDoorOffset && (point - end).sqrMagnitude < .0001f) { start = end; return; }
            start = transform.position;
            end = point;
            doorOffset = Vector3.zero;
        }
        public bool WouldOverlap(Vector3 point,float fraction)
        {
            Vector3 next=Vector3.Lerp(start,end,Mathf.Clamp01(fraction))+doorOffset;if(Mathf.Abs(point.y-next.y)>1.8f)return false;point.y=next.y;
            return (next-point).sqrMagnitude<.56f*.56f && (next-point).sqrMagnitude<(transform.position-point).sqrMagnitude;
        }
        public void Interpolate(float fraction,float deltaTime)
        {
            transform.position=Vector3.Lerp(start,end,Mathf.Clamp01(fraction))+doorOffset;Vector3 movement=transform.position-last;
            Speed=deltaTime>.00001f?movement.magnitude/deltaTime:0;last=transform.position;
            if(movement.sqrMagnitude>.000001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(movement),360f*deltaTime);
        }
        public bool MoveTo(CityPoint p)=>registered && traffic.Move(id,new Vector3(p.X,p.Y,p.Z));
        public void Pin(bool value){if(registered)traffic.Pin(id,value);}
        public void Face(Vector3 target){Vector3 d=target-transform.position;d.y=0;if(d.sqrMagnitude>.0001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(d),300f*Time.deltaTime);}
        public bool ApproachDoor(Vector3 stand)
        {
            if (!registered || !AtStepEnd || capsule == null || Time.deltaTime <= 0) return false;
            Vector3 wanted = stand - end;
            wanted.y = 0;
            // Una celda mide 50 cm. El ajuste conserva la reserva y comprueba todo el barrido físico.
            wanted = Vector3.ClampMagnitude(wanted, .48f);
            Vector3 step = Vector3.ClampMagnitude(wanted - doorOffset, .75f * Time.deltaTime);
            if (step.sqrMagnitude < .000001f) return false;
            Vector3 center = transform.TransformPoint(capsule.center);
            float radius = capsule.radius;
            float axis = Mathf.Max(0, capsule.height * .5f - radius);
            Vector3 lower = center - Vector3.up * Mathf.Max(0, axis - .025f);
            Vector3 upper = center + Vector3.up * axis;
            int mask = ~(1 << 31);
            Physics.SyncTransforms();
            int hits = Physics.CapsuleCastNonAlloc(lower, upper, radius, step.normalized, approachHits,
                step.magnitude, mask, QueryTriggerInteraction.Ignore);
            if (hits == approachHits.Length) return false;
            for (int i = 0; i < hits; i++)
                if (approachHits[i].collider != null && !approachHits[i].collider.transform.IsChildOf(transform)) return false;
            int count = Physics.OverlapCapsuleNonAlloc(lower + step, upper + step, radius,
                approachOverlaps, mask, QueryTriggerInteraction.Ignore);
            if (count == approachOverlaps.Length) return false;
            for (int i = 0; i < count; i++)
                if (approachOverlaps[i] != null && !approachOverlaps[i].transform.IsChildOf(transform)) return false;
            doorOffset += step;
            start = end;
            transform.position = last = end + doorOffset;
            Speed = step.magnitude / Time.deltaTime;
            Physics.SyncTransforms();
            return true;
        }
        public void Stop(){if(registered)traffic.Stop(id);}
        public void Suspend(){if(registered)traffic.Release(id);registered=false;doorOffset=Vector3.zero;Speed=0;}
    }
}
