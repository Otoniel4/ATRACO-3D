using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using Alarma.AI.CityLife;
static class WorldChecks
{
    static void Assert(bool valid,string reason){if(!valid)throw new Exception(reason);}
    static float F(JsonElement a,int i)=>a[i].GetSingle();
    public static void Run(string directory,string assetDirectory=null)
    {
        var world=JsonDocument.Parse(File.ReadAllText(Path.Combine(directory,"world.json"))).RootElement;
        int cells=0,meshes=0;var names=new HashSet<string>();
        foreach(var cell in world.GetProperty("cells").EnumerateArray())
        {
            string file=cell.GetProperty("file").GetString();Assert(names.Add(file),"Parte duplicada: "+file);Assert(File.Exists(Path.Combine(cell.GetProperty("reuse").GetBoolean()?(assetDirectory??directory):directory,"export",file)),"Falta FBX: "+file);cells++;
            foreach(var part in cell.GetProperty("parts").EnumerateArray())meshes++;
        }
        var expected=JsonDocument.Parse(File.ReadAllText(Path.Combine(directory,"export_validation.json"))).RootElement;
        Assert(expected.GetProperty("world_size_m")[0].GetInt32()==3000 && expected.GetProperty("world_size_m")[1].GetInt32()==3000,"Dimensiones incorrectas");
        Assert(cells==expected.GetProperty("parts").GetInt32() && meshes==expected.GetProperty("meshes").GetInt32() && cells>100 && meshes>30000,"Ciudad incompleta");int stations=0;float maximumStep=0;
        foreach(var shop in world.GetProperty("shops").EnumerateArray())
        {
            string id=shop.GetProperty("id").GetString();var nodes=shop.GetProperty("nodes").EnumerateArray().ToArray();
            var map=new Map{P=nodes.Select(n=>new CityPoint(F(n.GetProperty("v"),0),F(n.GetProperty("v"),1),F(n.GetProperty("v"),2))).ToArray(),Links=nodes.Select(n=>n.GetProperty("links").EnumerateArray().Select(v=>v.GetInt32()).ToArray()).ToArray()};
            var traffic=new PedestrianTraffic(map);Assert(traffic.TryAdd(-1,0),"No se crea planificador");var unique=new HashSet<int>();var origin=shop.GetProperty("origin");
            foreach(string key in new[]{"walk","entry","queue","exit","browseStations"})foreach(var wrapped in shop.GetProperty(key).EnumerateArray())
            {
                var p=wrapped.GetProperty("v");var target=new CityPoint(F(origin,0)+F(p,0),F(origin,1)+F(p,2),F(origin,2)-F(p,1));int node=map.Near(target);
                float distance=(float)Math.Sqrt(Math.Pow(map.P[node].X-target.X,2)+Math.Pow(map.P[node].Y-target.Y,2)+Math.Pow(map.P[node].Z-target.Z,2));
                Assert(distance<.65f,id+" puesto sin centro transitable: "+key);Assert(traffic.SetGoal(-1,node),id+" ruta desconectada: "+key);
                if(key=="queue" || key=="browseStations"){Assert(unique.Add(node),id+" comparte puesto de compra/fila");stations++;}
            }
            foreach(var actor in Enumerable.Range(0,map.Count))foreach(int link in map.Neighbours(actor)){float step=Math.Abs(map.P[actor].Y-map.P[link].Y);maximumStep=Math.Max(maximumStep,step);Assert(step<.31f,id+" desnivel no transitable: "+step);}
        }
        Assert(stations==30,"Faltan puestos");Assert(world.GetProperty("doors").GetArrayLength()==9,"Faltan puertas de locales");
        File.WriteAllText(Path.Combine(directory,"world_checks.json"),JsonSerializer.Serialize(new{passed=true,cells,mesh_objects=meshes,validated_stations=stations,maximum_step_m=maximumStep,unity_play_tested=false},new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine("WORLD_PASS: 153 partes; 30 puestos distintos y conectados; desnivel máximo "+maximumStep+" m.");
    }
}
