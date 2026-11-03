using System;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using System.IO;
using Alarma.AI.CityLife;
sealed class Map:ITrafficMap
{
    public CityPoint[] P;public int[][] Links;public int Count=>P.Length;
    public int[] Neighbours(int i)=>Links[i];public CityPoint Position(int i)=>P[i];
    public int Near(CityPoint p)=>Enumerable.Range(0,Count).OrderBy(i=>Math.Pow(P[i].X-p.X,2)+Math.Pow(P[i].Z-p.Z,2)).First();
    public static Map Rectangle(int width,int height,Func<int,int,bool> free=null)
    {
        var ids=new Dictionary<(int,int),int>();var points=new List<CityPoint>();
        for(int y=0;y<height;y++)for(int x=0;x<width;x++)if(free==null || free(x,y)){ids[(x,y)]=points.Count;points.Add(new CityPoint(x*.7f,0,y*.7f));}
        var links=new int[points.Count][];foreach(var pair in ids){var list=new List<int>();foreach(var d in new[]{(1,0),(-1,0),(0,1),(0,-1)})if(ids.TryGetValue((pair.Key.Item1+d.Item1,pair.Key.Item2+d.Item2),out int n))list.Add(n);links[pair.Value]=list.ToArray();}
        return new Map{P=points.ToArray(),Links=links};
    }
}
sealed class Motor:IPedestrianMotor
{
    public PedestrianTraffic Traffic;public Map Map;public int Id;public CityPoint Start,End,Position;
    public bool HasArrived=>Traffic.Get(Id).Cell==Traffic.Get(Id).Goal && Math.Abs(Position.X-End.X)+Math.Abs(Position.Z-End.Z)<.001;
    public bool MoveTo(CityPoint p)=>Traffic.SetGoal(Id,Map.Near(p));
    public void Stop()=>Traffic.SetGoal(Id,Traffic.Get(Id).Cell);
    public void Blend(float t){Position=new CityPoint(Start.X+(End.X-Start.X)*t,.16f,Start.Z+(End.Z-Start.Z)*t);}
}
static class Program
{
    static int assertions;
    static void Check(bool condition,string message){assertions++;if(!condition)throw new Exception(message);}
    static float F(JsonElement p,int index)=>p[index].GetSingle();
    static CityPoint Point(JsonElement p,float x=0)=>new CityPoint(F(p,0)+x,F(p,2),-F(p,1));
    static CityPoint[] Points(JsonElement shop,string name,float x)=>shop.GetProperty(name).EnumerateArray().Select(p=>Point(p,x)).ToArray();
    static void Invariants(Map map,PedestrianTraffic traffic,Dictionary<int,int> before)
    {
        var all=traffic.Residents.ToArray();Check(all.Select(a=>a.Cell).Distinct().Count()==all.Length,"Dos NPC reservan la misma posiciÃ³n.");
        foreach(var a in all)foreach(var b in all)if(a.Id<b.Id)Check(!(a.Cell==before[b.Id] && b.Cell==before[a.Id]),"Intercambio frontal de posiciones.");
    }
    static void Stress(string name,Map map,int[] starts,int[] goals,int steps)
    {
        var traffic=new PedestrianTraffic(map);for(int i=0;i<starts.Length;i++){Check(traffic.TryAdd(i,starts[i]),name+" alta");Check(traffic.SetGoal(i,goals[i]),name+" destino");}
        var reached=new HashSet<int>();int maxWait=0;
        for(int t=0;t<steps;t++){var before=traffic.Residents.ToDictionary(a=>a.Id,a=>a.Cell);traffic.Step();Invariants(map,traffic,before);foreach(var actor in traffic.Residents){if(actor.Cell==actor.Goal)reached.Add(actor.Id);maxWait=Math.Max(maxWait,actor.WaitingSteps);}}
        Check(reached.Count==starts.Length,name+" bloqueo persistente: "+string.Join(",",traffic.Residents.Where(a=>!reached.Contains(a.Id)).Select(a=>a.Id)));
        Check(traffic.Residents.All(a=>a.Cell==a.Goal),name+" sin convergencia final");
        Console.WriteLine(name+": "+reached.Count+" destinos alcanzados; espera mÃ¡xima "+maxWait+" pasos");
    }
    static void Commerce()
    {
        var q=new ShopQueue(3);var s=new ShopService("TEST",q,3,2,750);ShoppingSession a,b,c;
        Check(!s.TryBegin(0,749,out a),"Saldo insuficiente");Check(s.TryBegin(1,1000,out a),"Reserva A");Check(s.TryBegin(2,1000,out b),"Reserva B");Check(!s.TryBegin(3,1000,out c),"Sobreventa");
        Check(q.TryJoin(1)&&q.TryJoin(2),"Fila FIFO");Check(s.PickUp(1)&&s.PickUp(2),"Tomar productos");Check(!s.Place(2),"AtenciÃ³n fuera de turno");
        Check(s.Place(1)&&s.Scan(1)&&s.Pay(1),"Cobro A");Check(a.WalletCents==250 && s.TillCents==750 && s.Stock==1,"Contabilidad A");
        Check(!s.Pay(1) && s.PurchaseCount==1,"Cobro duplicado");Check(!s.Collect(2),"Entrega sin pago");Check(s.Collect(1),"Entrega pagada");
        Check(q.IndexOf(2)==1,"El siguiente espera hasta que el primero despeja la caja");q.Release(1);s.Release(1);Check(q.IndexOf(2)==0,"Avance de fila");
        s.Release(2);q.Release(2);Check(s.Stock==1 && s.TillCents==750,"Cancelar no descuenta stock ni dinero");Check(s.TryBegin(3,1000,out c),"Reserva recuperada");s.Clear();Check(s.TryBegin(4,1000,out c),"Limpieza al volver al pool");
    }
    static void Main(string[] args)
    {
        string root=Path.GetFullPath(args[0]);WorldChecks.Run(args[1],args.Length>2?args[2]:null);Commerce();PassageChecks.Run();WorldCrowdChecks.Run(args[1]);
        var wide=Map.Rectangle(25,5);Stress("Cruce frontal 20 NPC",wide,Enumerable.Range(0,10).Concat(Enumerable.Range(115,10)).ToArray(),Enumerable.Range(115,10).Concat(Enumerable.Range(0,10)).ToArray(),220);
        var doorway=Map.Rectangle(21,9,(x,y)=>x!=10 || y==4 || y==5);
        var left=Enumerable.Range(0,12).Select(i=>doorway.Near(new CityPoint((i%3)*.7f,0,(i/3+2)*.7f))).ToArray();
        var right=Enumerable.Range(0,12).Select(i=>doorway.Near(new CityPoint((18+i%3)*.7f,0,(i/3+2)*.7f))).ToArray();Stress("Puerta con flujo opuesto 24 NPC",doorway,left.Concat(right).ToArray(),right.Concat(left).ToArray(),300);
        var disconnected=Map.Rectangle(5,3,(x,y)=>x!=2);var noRoute=new PedestrianTraffic(disconnected);Check(noRoute.TryAdd(1,0),"Alta aislada");Check(!noRoute.SetGoal(1,3),"Se rechaza destino sin conexiÃ³n");
        var nav=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"traffic_graph.json"))).RootElement.GetProperty("nodes");
        var map=new Map{P=nav.EnumerateArray().Select(n=>new CityPoint(F(n.GetProperty("v"),0),.16f,F(n.GetProperty("v"),2))).ToArray(),Links=nav.EnumerateArray().Select(n=>n.GetProperty("links").EnumerateArray().Select(v=>v.GetInt32()).ToArray()).ToArray()};
        var graph=new PedestrianTraffic(map);var motors=new List<Motor>();var routines=new List<PedestrianRoutine>();var rows=new List<List<object>>();var events=new List<object>();var services=new List<ShopService>();
        float now=0;var district=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"district.json"))).RootElement;int id=0;
        foreach(var shop in district.GetProperty("shops").EnumerateArray())
        {
            float x=F(shop.GetProperty("center"),0);var queue=new ShopQueue(3);var service=new ShopService(shop.GetProperty("id").GetString(),queue,3,80,shop.GetProperty("priceCents").GetInt32());services.Add(service);
            service.Changed+=(session,action)=>events.Add(new{time=now,actor=session.Customer,action=action.ToString(),receipt=session.ReceiptId,station=session.Station});
            for(int i=0;i<8;i++)
            {
                int actor=id++;var walk=Points(shop,"walk",x);int start=map.Near(new CityPoint(x-4.5f+i*.7f,.16f,9.1f));Check(graph.TryAdd(actor,start),"Spawn libre");
                var motor=new Motor{Traffic=graph,Map=map,Id=actor,Start=map.P[start],End=map.P[start],Position=map.P[start]};motors.Add(motor);
                // Cuatro compradores llegan directamente desde la acera; cuatro paseantes recorren ambos carriles.
                var plan=new PedestrianPlan{Walk=i<4?new[]{walk[3]}:walk.Skip(i%4).Concat(walk.Take(i%4)).ToArray(),Entry=Points(shop,"entry",x),BrowseStations=Points(shop,"browseStations",x),Queue=Points(shop,"queue",x),Exit=Points(shop,"exit",x),VisitsShop=i<4,BrowseSeconds=1.5f,PaySeconds=.9f,RestSeconds=4,TravelTimeout=100,QueueTimeout=100};
                var routine=new PedestrianRoutine(actor,motor,queue,plan,service);routine.Start();routines.Add(routine);rows.Add(new List<object>());
            }
        }
        float minimum=float.MaxValue;int failures=0;var bought=new HashSet<int>();float[] lastYaw=new float[24];var lastPositions=motors.Select(m=>m.Position).ToArray();var failedOnce=new HashSet<int>();
        for(int frame=1;frame<=4320;frame++)
        {
            now=(frame-1)/24f;int phase=(frame-1)%18;float blend=(phase+1)/18f;
            foreach(var motor in motors)motor.Blend(blend);
            for(int i=0;i<routines.Count;i++)
            {
                var routine=routines[i];var beforeState=routine.State;routine.Tick(1/24f);graph.Get(i).Pinned=routine.Interaction;
                if(routine.State==PedestrianState.Failed && failedOnce.Add(i))Console.WriteLine("FAIL actor "+i+" at "+now+" from "+beforeState+" cell "+graph.Get(i).Cell+" goal "+graph.Get(i).Goal);
                var p=motors[i].Position;var previous=lastPositions[i];float dx=p.X-previous.X,dz=p.Z-previous.Z;float speed=(float)Math.Sqrt(dx*dx+dz*dz)*24;
                if(speed>.01f)lastYaw[i]=(float)Math.Atan2(dx,dz);
                if(routine.Interaction && routine.Session!=null || routine.State==PedestrianState.Browsing && motors[i].HasArrived)
                {
                    var shop=district.GetProperty("shops")[i/8];var target=routine.State==PedestrianState.Browsing || routine.State==PedestrianState.PickingUp?shop.GetProperty("products")[routine.Session.Station]:shop.GetProperty("counter");var world=Point(target,F(shop.GetProperty("center"),0));lastYaw[i]=(float)Math.Atan2(world.X-p.X,world.Z-p.Z);
                }
                string mode=speed>.08f?(routine.Carrying?"CarryWalk":"Walk"):routine.Interaction? (routine.State==PedestrianState.PickingUp?"Browse":"Pay"):routine.State==PedestrianState.Browsing && motors[i].HasArrived?"Browse":"Idle";
                rows[i].Add(new{frame,position=new[]{p.X,-p.Z,.16f},yaw=lastYaw[i],mode,state=routine.State.ToString(),stateSeconds=routine.StateSeconds,stage=routine.Session?.Stage.ToString()??"None",station=routine.Session?.Station??-1,carrying=routine.HoldingBag,speed});lastPositions[i]=p;
                if(routine.State==PedestrianState.Failed)failures++;
                if(routine.Session!=null && routine.Session.Stage>=ShoppingStage.Paid && routine.Session.Stage!=ShoppingStage.Cancelled)bought.Add(i);
            }
            for(int a=0;a<24;a++)for(int b=a+1;b<24;b++){var p=motors[a].Position;var q=motors[b].Position;float distance=(float)Math.Sqrt(Math.Pow(p.X-q.X,2)+Math.Pow(p.Z-q.Z,2));minimum=Math.Min(minimum,distance);}
            if(phase==17)
            {
                foreach(var m in motors)m.Blend(1);
                var before=graph.Residents.ToDictionary(a=>a.Id,a=>a.Cell);var steps=graph.Step();Invariants(map,graph,before);
                foreach(var m in motors){m.Start=m.End;m.End=map.P[steps[m.Id]];}
            }
        }
        File.WriteAllText(Path.Combine(root,"debug_traces.json"),JsonSerializer.Serialize(new{actors=rows,events}));
        Check(failures==0,"Rutinas fallidas: "+failures);Check(bought.Count==12,"No todos los compradores llegaron a pagar: "+bought.Count);Check(minimum>.44f,"SeparaciÃ³n insuficiente: "+minimum);
        Check(services.All(s=>s.PurchaseCount>=4),"Cada local debe cobrar a cuatro clientes");
        File.WriteAllText(Path.Combine(root,"preview_traces.json"),JsonSerializer.Serialize(new{fps=24,duration=180,actors=rows,events,minimum_distance=minimum}));
        File.WriteAllText(Path.Combine(root,"domain_validation.json"),JsonSerializer.Serialize(new{passed=true,assertions,minimum_distance=minimum,failures,buyers=bought.Count,purchases=services.Select(s=>s.PurchaseCount).ToArray(),stress_cases=2,unity_play_tested=false},new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine("PASS "+assertions+" comprobaciones; separaciÃ³n "+minimum+" m; 12 compradores atendidos; "+string.Join("/",services.Select(s=>s.PurchaseCount))+" compras.");
    }
}
