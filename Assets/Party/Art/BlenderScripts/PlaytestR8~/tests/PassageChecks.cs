using System;
using System.Linq;
using Alarma.AI.CityLife;
static class PassageChecks
{
    public static void Run()
    {
        var line=Map.Rectangle(7,1);var traffic=new PedestrianTraffic(line);traffic.TryAdd(1,0);traffic.SetGoal(1,6);bool open=false;
        for(int i=0;i<12;i++){traffic.Step((a,b)=>open || b!=3);if(traffic.Get(1).Cell>=3)throw new Exception("El NPC atravesó una puerta cerrada.");}
        open=true;for(int i=0;i<12;i++)traffic.Step((a,b)=>open || b!=3);
        if(traffic.Get(1).Cell!=6)throw new Exception("El NPC no retomó el paso al abrir la puerta.");
        var area=Map.Rectangle(9,3);var walkers=new PedestrianTraffic(area);walkers.TryAdd(1,9);walkers.TryAdd(2,17);walkers.SetGoal(1,17);walkers.SetGoal(2,9);
        for(int i=0;i<80;i++)
        {
            var before=walkers.Residents.ToDictionary(a=>a.Id,a=>a.Cell);walkers.Step((a,b)=>b!=13);
            if(walkers.Residents.Any(a=>a.Cell==13) || walkers.Residents.Select(a=>a.Cell).Distinct().Count()!=2)throw new Exception("El NPC atravesó al jugador o a otro NPC.");
            if(walkers.Get(1).Cell==before[2] && walkers.Get(2).Cell==before[1])throw new Exception("Cruce frontal.");
        }
        if(walkers.Get(1).Cell!=17 || walkers.Get(2).Cell!=9)throw new Exception("El rodeo del jugador no termina.");
        Console.WriteLine("PASS: puerta cerrada/abierta, rodeo del jugador y reservas sin solapamientos.");
    }
}
