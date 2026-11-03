using System;
using System.Collections.Generic;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Movimiento cooperativo: todos reservan un paso antes de interpolar sus posiciones.
    [DefaultExecutionOrder(-200)]
    public sealed class CityTrafficController : MonoBehaviour
    {
        [SerializeField] private TrafficGraph graph;
        [SerializeField,Min(.2f)] private float stepSeconds=.75f;
        [SerializeField] private Transform blocker;
        public void ConfigureBlocker(Transform value){blocker=value;}
        private PedestrianTraffic traffic;private float elapsed;private bool ready;
        private readonly Dictionary<int,PedestrianMovement> motors=new Dictionary<int,PedestrianMovement>();
        private readonly Dictionary<(int,int),bool> passageCache=new Dictionary<(int,int),bool>();
        public TrafficGraph Graph=>graph;
        public void Configure(TrafficGraph value,float seconds){graph=value;stepSeconds=seconds;traffic=new PedestrianTraffic(graph);}
        private void Awake(){if(graph!=null)traffic=new PedestrianTraffic(graph);}
        public bool Register(int id,PedestrianMovement motor,Vector3 position)
        {
            if(traffic==null)return false;
            var candidates=new List<int>();for(int i=0;i<graph.Count;i++)if((graph.Cells[i].Position-position).sqrMagnitude<2.25f)candidates.Add(i);
            candidates.Sort((a,b)=>(graph.Cells[a].Position-position).sqrMagnitude.CompareTo((graph.Cells[b].Position-position).sqrMagnitude));
            foreach(int cell in candidates)
            {
                bool clear=true;foreach(var other in motors.Values)if((other.transform.position-graph.Cells[cell].Position).sqrMagnitude<.49f){clear=false;break;}
                if(clear && traffic.TryAdd(id,cell)){motors.Add(id,motor);motor.Snap(graph.Cells[cell].Position);return true;}
            }
            return false;
        }
        public bool Move(int id,Vector3 target){int cell=graph.Nearest(target,.65f);return cell>=0 && traffic.SetGoal(id,cell);}
        public bool Arrived(int id)=>traffic?.Get(id) is TrafficResident actor && actor.Cell==actor.Goal && motors[id].AtStepEnd;
        public void Pin(int id,bool pinned){var actor=traffic?.Get(id);if(actor!=null)actor.Pinned=pinned;}
        public void Stop(int id){var actor=traffic?.Get(id);if(actor!=null)traffic.SetGoal(id,actor.Cell);}
        public void Release(int id){traffic?.Remove(id);motors.Remove(id);}
        private void Update()
        {
            if(traffic==null)return;
            float proposed=elapsed+Time.deltaTime;bool blocked=false;
            if(blocker!=null)foreach(var motor in motors.Values)if(motor.WouldOverlap(blocker.position,proposed/stepSeconds)){blocked=true;break;}
            if(!blocked)elapsed=proposed;
            ready=elapsed>=stepSeconds;
            foreach(var motor in motors.Values)motor.Interpolate(Mathf.Min(1,elapsed/stepSeconds),Time.deltaTime);
        }
        private bool CanTraverse(int from,int to)
        {
            if(passageCache.TryGetValue((from,to),out bool value))return value;
            value=CheckPassage(from,to);passageCache[(from,to)]=value;return value;
        }
        private bool CheckPassage(int from,int to)
        {
            Vector3 a=graph.Cells[from].Position,b=graph.Cells[to].Position;
            if(blocker!=null && Mathf.Abs(blocker.position.y-a.y)<1.8f){Vector3 p=blocker.position;float t=Vector3.Dot(p-a,b-a)/Mathf.Max(.0001f,(b-a).sqrMagnitude);Vector3 closest=Vector3.Lerp(a,b,Mathf.Clamp01(t));p.y=closest.y;if((p-closest).sqrMagnitude<.58f*.58f)return false;}
            Vector3 direction=b-a;float distance=direction.magnitude;int mask=~((1<<29)|(1<<30)|(1<<31));
            return !Physics.CheckCapsule(b+Vector3.up*.5f,b+Vector3.up*1.45f,.23f,mask,QueryTriggerInteraction.Ignore) &&
                !Physics.CapsuleCast(a+Vector3.up*.5f,a+Vector3.up*1.45f,.23f,direction.normalized,distance,mask,QueryTriggerInteraction.Ignore);
        }
        private void LateUpdate()
        {
            // Las rutinas observan primero la llegada y fijan las interacciones antes de reservar otro paso.
            if(!ready || traffic==null)return;
            elapsed%=stepSeconds;passageCache.Clear();Physics.SyncTransforms();var steps=traffic.Step(CanTraverse);
            foreach(var pair in steps)motors[pair.Key].SetStep(graph.Cells[pair.Value].Position);
        }
    }
}
