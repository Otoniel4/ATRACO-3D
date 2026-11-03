using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest.Editor
{
    // Se ejecuta al pulsar Crear y probar: usa las mismas mallas y colliders que cargará la partida.
    public static class ReviewPhysicalAcceptance
    {
        [Serializable] private sealed class Result{public bool passed;public int doors,stores,lobbySlots;public StoreResult[] commerce;}
        [Serializable] private sealed class StoreResult{public string id;public int nodes,purchases,tillCents;}
        private static readonly Collider[] overlaps=new Collider[32];
        public static void Validate(Scene main,string folder,WorldBuildData source,WorldReviewData world)
        {
            Scene audit=SceneManager.CreateScene("Alarma · comprobación física",new CreateSceneParameters(LocalPhysicsMode.Physics3D));var results=new List<StoreResult>();
            try
            {
                foreach(var cell in world.Cells.Where(c=>c.Always))
                {
                    var model=AssetDatabase.LoadAssetAtPath<GameObject>(folder+"/Resources/"+cell.Resource+".prefab");var instance=(GameObject)PrefabUtility.InstantiatePrefab(model,audit);instance.transform.position=cell.Origin;
                }
                var actualDoors=main.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<AutomaticShopDoor>()).ToArray();var doors=new List<AutomaticShopDoor>();
                foreach(var original in actualDoors){var copy=UnityEngine.Object.Instantiate(original.gameObject);SceneManager.MoveGameObjectToScene(copy,audit);doors.Add(copy.GetComponent<AutomaticShopDoor>());}
                PhysicsScene physics=audit.GetPhysicsScene();Physics.SyncTransforms();physics.Simulate(.02f);
                foreach(var door in doors)
                {
                    Vector3 p=door.Gateway.position;door.PreviewOpen(false);Physics.SyncTransforms();physics.Simulate(.02f);
                    if(!Blocked(physics,p-Vector3.forward*.9f,p+Vector3.forward*.9f))throw new InvalidOperationException("La hoja cerrada no bloquea su propio acceso: "+door.name);
                    door.PreviewOpen(true);
                }
                Physics.SyncTransforms();physics.Simulate(.02f);
                foreach(var d in source.doors.Where(d=>source.pois.Take(6).Any(p=>p.id==d.id)))
                {
                    Vector3 p=ReviewBuildWorld.Vector(d.threshold);if(Blocked(physics,p-Vector3.forward*.9f,p+Vector3.forward*.9f))throw new InvalidOperationException("El hueco de entrada sigue bloqueado al abrir: "+d.id);
                }
                var lobby=main.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<ReviewLobby>()).Single();
                foreach(var slot in lobby.SpawnSlots)if(!Clear(physics,slot.position))throw new InvalidOperationException("Un puesto del escondite está ocupado: "+slot.name);
                Vector3 spawn=ReviewBuildWorld.Vector(source.spawn);if(!Clear(physics,spawn))throw new InvalidOperationException("El punto inicial del escondite tiene un obstáculo.");
                var hideout=source.doors.Single(d=>d.id=="Hideout");if(Blocked(physics,spawn,ReviewBuildWorld.Vector(hideout.threshold)+Vector3.forward*1.2f))throw new InvalidOperationException("No se puede salir del escondite por su puerta abierta.");
                foreach(var shop in main.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<ShopActivity>()))
                {
                    RepairGraph(physics,shop);results.Add(ReviewCommerceTrial.Run(shop));
                }
                File.WriteAllText(folder+"/PhysicalAcceptance.json",JsonUtility.ToJson(new Result{passed=true,doors=doors.Count,stores=results.Count,lobbySlots=lobby.SpawnSlots.Length,commerce=results.ToArray()},true));
            }
            finally{EditorSceneManager.CloseScene(audit,true);SceneManager.SetActiveScene(main);}
        }
        private static bool Clear(PhysicsScene physics,Vector3 p)=>physics.OverlapCapsule(p+Vector3.up*.5f,p+Vector3.up*1.45f,.24f,overlaps,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore)==0;
        private static bool Blocked(PhysicsScene physics,Vector3 a,Vector3 b)
        {
            Vector3 delta=b-a;return physics.CapsuleCast(a+Vector3.up*.5f,a+Vector3.up*1.45f,.24f,delta.normalized,out _,delta.magnitude,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore);
        }
        private static void RepairGraph(PhysicsScene physics,ShopActivity shop)
        {
            var graph=shop.Traffic.Graph;var cells=graph.Cells;var free=new HashSet<int>(Enumerable.Range(0,cells.Length).Where(i=>Clear(physics,cells[i].Position)));var links=new Dictionary<int,int[]>();
            foreach(int i in free)links[i]=cells[i].Links.Where(j=>free.Contains(j) && !Blocked(physics,cells[i].Position,cells[j].Position)).ToArray();
            var remaining=new HashSet<int>(free);var largest=new HashSet<int>();
            while(remaining.Count>0){var component=new HashSet<int>();var stack=new Stack<int>();int start=remaining.First();remaining.Remove(start);stack.Push(start);
                while(stack.Count>0){int i=stack.Pop();component.Add(i);foreach(int j in links[i])if(remaining.Remove(j))stack.Push(j);}if(component.Count>largest.Count)largest=component;}
            if(largest.Count<100)throw new InvalidOperationException("No hay recorrido físico suficiente en "+shop.name);
            int[] old=largest.OrderBy(i=>i).ToArray();var map=old.Select((id,index)=>new{id,index}).ToDictionary(p=>p.id,p=>p.index);
            graph.Cells=old.Select(i=>new TrafficCell{Position=cells[i].Position,Links=links[i].Where(j=>map.ContainsKey(j)).Select(j=>map[j]).ToArray()}).ToArray();
            var unique=new HashSet<int>();
            foreach(var marker in shop.GetComponentsInChildren<Transform>())if(new[]{"Walk_","Entry_","Browse_","Queue_","Exit_"}.Any(prefix=>marker.name.StartsWith(prefix,StringComparison.Ordinal)))
            {
                int node=graph.Nearest(marker.position,.8f);if(node<0)throw new InvalidOperationException("Puesto bloqueado al importar: "+shop.name+"/"+marker.name);
                if((marker.name.StartsWith("Queue_",StringComparison.Ordinal)||marker.name.StartsWith("Browse_",StringComparison.Ordinal)) && !unique.Add(node))throw new InvalidOperationException("Puestos solapados: "+shop.name);
                marker.position=graph.Cells[node].Position;
            }
            EditorUtility.SetDirty(graph);shop.Traffic.Configure(graph,.75f);
        }
        private static class ReviewCommerceTrial
        {
            private sealed class Motor:IPedestrianMotor
            {
                public PedestrianTraffic Traffic;public TrafficGraph Map;public int Id;public Vector3 Position,Start,End;
                public bool HasArrived=>Traffic.Get(Id).Cell==Traffic.Get(Id).Goal && (Position-End).sqrMagnitude<.0001f;
                public bool MoveTo(CityPoint p){int n=Map.Nearest(new Vector3(p.X,p.Y,p.Z),.8f);return n>=0 && Traffic.SetGoal(Id,n);}
                public void Stop()=>Traffic.SetGoal(Id,Traffic.Get(Id).Cell);
            }
            public static StoreResult Run(ShopActivity shop)
            {
                var graph=shop.Traffic.Graph;var traffic=new PedestrianTraffic(graph);var queue=new ShopQueue(3);var service=new ShopService(shop.Tasks.ShopId,queue,shop.StationCount,100,shop.Tasks.PriceCents);var settings=ScriptableObject.CreateInstance<PedestrianSettings>();settings.TravelTimeout=120;settings.QueueTimeout=120;var motors=new List<Motor>();var routines=new List<PedestrianRoutine>();
                try
                {
                    for(int i=0;i<4;i++)
                    {
                        int node=graph.Nearest(shop.WalkRoute[i%shop.WalkRoute.Length].position,.8f);if(!traffic.TryAdd(i,node))throw new InvalidOperationException("No se separan los compradores de "+shop.name);
                        var motor=new Motor{Traffic=traffic,Map=graph,Id=i,Position=graph.Cells[node].Position,Start=graph.Cells[node].Position,End=graph.Cells[node].Position};motors.Add(motor);var plan=shop.CreatePlan(settings,true,i%shop.WalkRoute.Length);plan.WalletCents=shop.Tasks.CustomerWalletCents;
                        var routine=new PedestrianRoutine(i,motor,queue,plan,service);routine.Start();routines.Add(routine);
                    }
                    for(int frame=0;frame<4320;frame++)
                    {
                        int phase=frame%18;foreach(var motor in motors)motor.Position=Vector3.Lerp(motor.Start,motor.End,(phase+1)/18f);
                        for(int i=0;i<routines.Count;i++){routines[i].Tick(1/24f);traffic.Get(i).Pinned=routines[i].Interaction;if(routines[i].State==PedestrianState.Failed)throw new InvalidOperationException("Compra fallida sobre la geometría real: "+shop.name+" cliente "+i);}
                        if(phase==17){var moves=traffic.Step();foreach(var motor in motors){motor.Start=motor.End;motor.End=graph.Cells[moves[motor.Id]].Position;}}
                    }
                    if(service.PurchaseCount<4 || service.TillCents!=service.PurchaseCount*shop.Tasks.PriceCents)throw new InvalidOperationException("No se completan compras y cobros en "+shop.name);
                    return new StoreResult{id=shop.Tasks.ShopId,nodes=graph.Count,purchases=service.PurchaseCount,tillCents=service.TillCents};
                }
                finally{UnityEngine.Object.DestroyImmediate(settings);}
            }
        }
    }
}
