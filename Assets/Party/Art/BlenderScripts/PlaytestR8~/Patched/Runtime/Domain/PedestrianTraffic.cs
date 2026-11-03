using System;
using System.Collections.Generic;

namespace Alarma.AI.CityLife
{
    // Grafo de centros transitables. Unity lo obtiene del NavMesh; las pruebas usan el mismo contrato.
    public interface ITrafficMap
    {
        int Count { get; }
        int[] Neighbours(int cell);
        CityPoint Position(int cell);
    }

    public sealed class TrafficResident
    {
        public int Id { get; internal set; }
        public int Cell { get; internal set; }
        public int Goal { get; internal set; }
        public bool Pinned { get; set; }
        public int WaitingSteps { get; internal set; }
        public int TravelSteps { get; internal set; }
    }

    // Herencia de prioridad con backtracking: quien espera más puede pedir al vecino que se aparte.
    // Se reservan destinos y aristas antes de mover a nadie. Nunca se intercambian dos celdas de frente.
    public sealed class PedestrianTraffic
    {
        private readonly ITrafficMap map;
        private readonly Dictionary<int, TrafficResident> residents = new Dictionary<int, TrafficResident>();
        private readonly Dictionary<int, int[]> distances = new Dictionary<int, int[]>();
        private readonly Dictionary<int,int[]> passageDistances=new Dictionary<int,int[]>();
        private Dictionary<int, int> next;
        private Dictionary<int, int> occupied;
        private int searchBudget;
        private Func<int,int,bool> canTraverse;
        public IEnumerable<TrafficResident> Residents => residents.Values;
        public PedestrianTraffic(ITrafficMap map) { this.map = map ?? throw new ArgumentNullException(nameof(map)); }
        public bool TryAdd(int id, int cell)
        {
            if (residents.ContainsKey(id) || cell < 0 || cell >= map.Count) return false;
            foreach (var other in residents.Values) if (other.Cell == cell) return false;
            residents.Add(id, new TrafficResident { Id=id, Cell=cell, Goal=cell }); return true;
        }
        public bool SetGoal(int id, int goal)
        {
            if (!residents.TryGetValue(id, out var actor) || goal < 0 || goal >= map.Count || Distance(goal)[actor.Cell] == int.MaxValue) return false;
            actor.Goal=goal; return true;
        }
        public TrafficResident Get(int id) => residents.TryGetValue(id,out var actor) ? actor : null;
        public void Remove(int id) => residents.Remove(id);
        private int[] Distance(int goal)
        {
            if (distances.TryGetValue(goal,out var result)) return result;
            result=new int[map.Count];for(int i=0;i<result.Length;i++)result[i]=int.MaxValue;
            var queue=new Queue<int>();queue.Enqueue(goal);result[goal]=0;
            while(queue.Count>0) {int cell=queue.Dequeue();foreach(int neighbour in map.Neighbours(cell))
                if(result[neighbour]==int.MaxValue) {result[neighbour]=result[cell]+1;queue.Enqueue(neighbour);} }
            distances.Add(goal,result);return result;
        }
        public Dictionary<int,int> Step(Func<int,int,bool> passage=null)
        {
            canTraverse=passage;passageDistances.Clear();occupied=new Dictionary<int,int>();next=new Dictionary<int,int>();
            var order=new List<TrafficResident>(residents.Values);
            foreach(var actor in order) occupied.Add(actor.Cell,actor.Id);
            order.Sort((a,b)=> {int c=b.WaitingSteps.CompareTo(a.WaitingSteps);return c!=0?c:a.Id.CompareTo(b.Id);});
            foreach(var actor in order) if(!next.ContainsKey(actor.Id))
            { searchBudget=Math.Max(256,residents.Count*32);if(!Plan(actor.Id,-1))next[actor.Id]=actor.Cell; }
            var cells=new HashSet<int>();
            foreach(var actor in order)
            {
                int target=next[actor.Id];if(!cells.Add(target))throw new InvalidOperationException("Reserva de tráfico duplicada.");
                if(target!=actor.Cell)actor.TravelSteps++;
                actor.Cell=target;actor.WaitingSteps=actor.Cell==actor.Goal?0:actor.WaitingSteps+1;
            }
            return new Dictionary<int,int>(next);
        }
        private bool Plan(int id,int requester)
        {
            if(--searchBudget<0)return false;
            var actor=residents[id];var candidates=new List<int>();
            if(!actor.Pinned)candidates.AddRange(map.Neighbours(actor.Cell));candidates.Add(actor.Cell);
            int[] distance=PassageDistance(actor.Goal);
            candidates.Sort((a,b)=> {int c=distance[a].CompareTo(distance[b]);if(c!=0)return c;if(a==actor.Cell)return -1;if(b==actor.Cell)return 1;return a.CompareTo(b);});
            foreach(int cell in candidates)
            {
                if(cell!=actor.Cell && canTraverse!=null && !canTraverse(actor.Cell,cell))continue;
                if(next.ContainsValue(cell))continue;
                if(requester>=0 && cell==residents[requester].Cell)continue;
                if(occupied.TryGetValue(cell,out int other) && other!=id && next.TryGetValue(other,out int destination) && destination==actor.Cell)continue;
                var snapshot=new Dictionary<int,int>(next);next[id]=cell;
                if(!occupied.TryGetValue(cell,out other) || other==id || next.ContainsKey(other) || Plan(other,id))return true;
                next=snapshot;
            }
            return false;
        }
        private int[] PassageDistance(int goal)
        {
            if(canTraverse==null)return Distance(goal);
            if(passageDistances.TryGetValue(goal,out var result))return result;
            result=new int[map.Count];for(int i=0;i<result.Length;i++)result[i]=int.MaxValue;
            var queue=new Queue<int>();queue.Enqueue(goal);result[goal]=0;
            while(queue.Count>0){int cell=queue.Dequeue();foreach(int neighbour in map.Neighbours(cell))
                if(result[neighbour]==int.MaxValue && canTraverse(neighbour,cell)){result[neighbour]=result[cell]+1;queue.Enqueue(neighbour);}}
            passageDistances.Add(goal,result);return result;
        }
    }
}
