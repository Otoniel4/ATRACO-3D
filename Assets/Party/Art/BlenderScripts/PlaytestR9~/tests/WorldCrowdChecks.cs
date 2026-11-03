using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using Alarma.AI.CityLife;
static class WorldCrowdChecks
{
    static float F(JsonElement p,int i)=>p[i].GetSingle();
    public static void Run(string folder)
    {
        var world=JsonDocument.Parse(File.ReadAllText(Path.Combine(folder,"world.json"))).RootElement;var results=new List<object>();
        foreach(var shop in world.GetProperty("shops").EnumerateArray())
        {
            var origin=shop.GetProperty("origin");CityPoint Point(JsonElement p)=>new CityPoint(F(origin,0)+F(p,0),F(origin,1)+F(p,2),F(origin,2)-F(p,1));
            CityPoint[] Points(string key)=>shop.GetProperty(key).EnumerateArray().Select(p=>Point(p.GetProperty("v"))).ToArray();
            var nodes=shop.GetProperty("nodes").EnumerateArray().ToArray();var map=new Map{P=nodes.Select(n=>new CityPoint(F(n.GetProperty("v"),0),F(n.GetProperty("v"),1),F(n.GetProperty("v"),2))).ToArray(),Links=nodes.Select(n=>n.GetProperty("links").EnumerateArray().Select(v=>v.GetInt32()).ToArray()).ToArray()};
            var graph=new PedestrianTraffic(map);var queue=new ShopQueue(3);var service=new ShopService(shop.GetProperty("id").GetString(),queue,3,80,shop.GetProperty("priceCents").GetInt32());var motors=new List<Motor>();var routines=new List<PedestrianRoutine>();
            var walk=Points("walk");var used=new HashSet<int>();
            for(int i=0;i<8;i++)
            {
                var w=walk[i%walk.Length];int start=Enumerable.Range(0,map.Count).Where(n=>!used.Contains(n)).OrderBy(n=>Math.Pow(map.P[n].X-w.X,2)+Math.Pow(map.P[n].Z-w.Z,2)).First();used.Add(start);graph.TryAdd(i,start);
                var motor=new Motor{Traffic=graph,Map=map,Id=i,Start=map.P[start],End=map.P[start],Position=map.P[start]};motors.Add(motor);
                var plan=new PedestrianPlan{Walk=i<4?new[]{walk[3]}:walk.Skip(i%walk.Length).Concat(walk.Take(i%walk.Length)).ToArray(),Entry=Points("entry"),BrowseStations=Points("browseStations"),Queue=Points("queue"),Exit=Points("exit"),VisitsShop=i<4,WalletCents=200000,BrowseSeconds=1.5f,PaySeconds=.9f,RestSeconds=4,TravelTimeout=100,QueueTimeout=100};
                var routine=new PedestrianRoutine(i,motor,queue,plan,service);routine.Start();routines.Add(routine);
            }
            for(int frame=0;frame<4320;frame++)
            {
                int phase=frame%18;foreach(var motor in motors)motor.Blend((phase+1)/18f);
                for(int i=0;i<routines.Count;i++){routines[i].Tick(1/24f);graph.Get(i).Pinned=routines[i].Interaction;if(routines[i].State==PedestrianState.Failed)throw new Exception(shop.GetProperty("id").GetString()+" rutina fallida "+i+" a "+frame/24f);}
                if(phase==17){var steps=graph.Step();foreach(var m in motors){m.Start=m.End;m.End=map.P[steps[m.Id]];}}
            }
            if(service.PurchaseCount<4)throw new Exception("Compras insuficientes en el grafo corregido: "+shop.GetProperty("id").GetString());
            results.Add(new{shop=shop.GetProperty("id").GetString(),purchases=service.PurchaseCount,nodes=map.Count});
        }
        File.WriteAllText(Path.Combine(folder,"world_crowd_validation.json"),JsonSerializer.Serialize(new{passed=true,seconds=180,shops=results,unity_play_tested=false},new JsonSerializerOptions{WriteIndented=true}));Console.WriteLine("PASS: 180 segundos de compras en "+results.Count+" comercios.");
    }
}
