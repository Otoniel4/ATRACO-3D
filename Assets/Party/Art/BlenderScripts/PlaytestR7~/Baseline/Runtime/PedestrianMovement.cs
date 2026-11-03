using UnityEngine;
using UnityEngine.AI;
namespace Alarma.AI.CityLife
{
    [RequireComponent(typeof(NavMeshAgent))]
    public sealed class PedestrianMovement : MonoBehaviour,IPedestrianMotor
    {
        private CityTrafficController traffic;private int id;private bool registered;private Vector3 start,end,last;
        public float Speed{get;private set;}
        public bool AtStepEnd=>(transform.position-end).sqrMagnitude<.0001f;
        public bool HasArrived=>registered && traffic.Arrived(id);
        public bool Place(int actorId,Vector3 position,CityTrafficController controller)
        {
            Suspend();GetComponent<NavMeshAgent>().enabled=false;id=actorId;traffic=controller;
            registered=traffic!=null && traffic.Register(id,this,position);return registered;
        }
        public void Snap(Vector3 point){transform.position=point;start=end=last=point;Speed=0;}
        public void SetStep(Vector3 point){start=transform.position;end=point;}
        public void Interpolate(float fraction,float deltaTime)
        {
            transform.position=Vector3.Lerp(start,end,Mathf.Clamp01(fraction));Vector3 movement=transform.position-last;
            Speed=deltaTime>.00001f?movement.magnitude/deltaTime:0;last=transform.position;
            if(movement.sqrMagnitude>.000001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(movement),360f*deltaTime);
        }
        public bool MoveTo(CityPoint p)=>registered && traffic.Move(id,new Vector3(p.X,p.Y,p.Z));
        public void Pin(bool value){if(registered)traffic.Pin(id,value);}
        public void Face(Vector3 target){Vector3 d=target-transform.position;d.y=0;if(d.sqrMagnitude>.0001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(d),300f*Time.deltaTime);}
        public void Stop(){if(registered)traffic.Stop(id);}
        public void Suspend(){if(registered)traffic.Release(id);registered=false;Speed=0;}
    }
}
