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
        private readonly Dictionary<int, Vector3> doorOrigins = new Dictionary<int, Vector3>();
        private readonly Collider[] visitorsAtEnd = new Collider[16];
        private readonly RaycastHit[] visitorsInPath = new RaycastHit[16];
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
            Vector3 a = doorOrigins.TryGetValue(from, out var actual) ? actual : graph.Cells[from].Position;
            Vector3 b = graph.Cells[to].Position;
            foreach (var other in doorOrigins)
                if (other.Key != from && CloseToSegment(other.Value, a, b, .49f)) return false;
            if(blocker!=null && Mathf.Abs(blocker.position.y-a.y)<1.8f){Vector3 p=blocker.position;float t=Vector3.Dot(p-a,b-a)/Mathf.Max(.0001f,(b-a).sqrMagnitude);Vector3 closest=Vector3.Lerp(a,b,Mathf.Clamp01(t));p.y=closest.y;if((p-closest).sqrMagnitude<.58f*.58f)return false;}
            Vector3 direction=b-a;float distance=direction.magnitude;int mask=~((1<<29)|(1<<30)|(1<<31));
            return !Physics.CheckCapsule(b+Vector3.up*.5f,b+Vector3.up*1.45f,.23f,mask,QueryTriggerInteraction.Ignore) &&
                !Physics.CapsuleCast(a+Vector3.up*.5f,a+Vector3.up*1.45f,.23f,direction.normalized,distance,mask,QueryTriggerInteraction.Ignore)
                && VisitorsClear(a, b, direction, distance);
        }

        private bool VisitorsClear(Vector3 a, Vector3 b, Vector3 direction, float distance)
        {
            const int pedestrianLayer = 1 << 29;
            int count = Physics.OverlapCapsuleNonAlloc(b + Vector3.up * .5f, b + Vector3.up * 1.45f, .23f,
                visitorsAtEnd, pedestrianLayer, QueryTriggerInteraction.Ignore);
            bool clear = count < visitorsAtEnd.Length;
            for (int i = 0; i < count; i++)
            {
                if (OutsideTraffic(visitorsAtEnd[i])) clear = false;
                visitorsAtEnd[i] = null;
            }
            if (!clear) return false;
            count = Physics.CapsuleCastNonAlloc(a + Vector3.up * .5f, a + Vector3.up * 1.45f, .23f,
                direction.normalized, visitorsInPath, distance, pedestrianLayer, QueryTriggerInteraction.Ignore);
            clear = count < visitorsInPath.Length;
            for (int i = 0; i < count; i++)
                if (OutsideTraffic(visitorsInPath[i].collider)) clear = false;
            return clear;
        }

        private bool OutsideTraffic(Collider body)
        {
            if (body == null) return false;
            var movement = body.GetComponentInParent<PedestrianMovement>();
            // Los residentes de este local ya están cubiertos por las reservas del grafo.
            return movement == null || !movement.UsesTraffic(this);
        }

        private static bool CloseToSegment(Vector3 point, Vector3 start, Vector3 end, float radius)
        {
            if (Mathf.Abs(point.y - start.y) > 1.8f) return false;
            point.y = start.y;
            end.y = start.y;
            Vector3 line = end - start;
            float fraction = Mathf.Clamp01(Vector3.Dot(point - start, line) / Mathf.Max(.0001f, line.sqrMagnitude));
            return (point - start - line * fraction).sqrMagnitude < radius * radius;
        }
        private void LateUpdate()
        {
            // Las rutinas observan primero la llegada y fijan las interacciones antes de reservar otro paso.
            if(!ready || traffic==null)return;
            elapsed%=stepSeconds;passageCache.Clear();doorOrigins.Clear();
            foreach (var pair in motors)
                if (pair.Value.HasDoorOffset && traffic.Get(pair.Key) is TrafficResident actor)
                    doorOrigins[actor.Cell] = pair.Value.transform.position;
            Physics.SyncTransforms();var steps=traffic.Step(CanTraverse);
            foreach(var pair in steps)motors[pair.Key].SetStep(graph.Cells[pair.Value].Position);
        }
    }
}
