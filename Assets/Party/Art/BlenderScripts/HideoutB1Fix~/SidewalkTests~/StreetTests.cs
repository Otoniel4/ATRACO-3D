using System;
using System.Linq;
using System.Reflection;
using Alarma.AI.Street;
using Alarma.Core.Contracts;
using UnityEngine;

internal static class StreetTests
{
    private static readonly MethodInfo Update = typeof(SidewalkWalker).GetMethod("Update", BindingFlags.NonPublic|BindingFlags.Instance);
    private static int passed;
    private static Vector3 At(float x,float z) => new Vector3(x,.175f,z);

    private sealed class Lights : ITrafficSignals
    {
        public SignalLight Current;
        public float Remaining;
        public SignalLight Light(int signal,int axis) => Current;
        public float SecondsUntilGreen(int signal,int axis) => Remaining;
    }

    private static void Check(bool result,string name)
    {
        if (!result) throw new InvalidOperationException(name);
        passed++;
        Console.WriteLine("PASS " + name);
    }

    private static Collider Body(Vector3 p, float radius, int layer, Transform transform = null)
    {
        var body = new Collider { transform=transform ?? new Transform { position=p }, Radius=radius, Layer=layer };
        Physics.Bodies.Add(body);
        return body;
    }

    private static SidewalkGraph Graph(Vector2[] points, params (int,int,int,int)[] edges)
    {
        var graph = new SidewalkGraph();
        graph.Build(points,edges,2f);
        return graph;
    }

    private static SidewalkWalker Walker(SidewalkGraph graph,int node,ITrafficSignals lights=null,int seed=0)
    {
        var walker = new SidewalkWalker();
        walker.Configure(new Animator());
        walker.Begin(graph,lights,node,seed);
        Body(walker.transform.position,.25f,29,walker.transform);
        return walker;
    }

    private static void Tick(params SidewalkWalker[] walkers)
    {
        Time.time += Time.deltaTime;
        foreach (var walker in walkers) Update.Invoke(walker,null);
    }

    public static void Main()
    {
        var line = Graph(new[]{new Vector2(0,0),new Vector2(0,6)},(0,1,-1,-1));
        Check(Math.Abs(line.LaneStart(0,1).x-.28f)<.0001f && Math.Abs(line.LaneTarget(0,1).x-.28f)<.0001f,"desvío constante en tramo de 6 m");
        Check(Math.Abs(line.LaneStart(1,0).x+.28f)<.0001f,"carriles de sentidos opuestos");
        var a = Walker(line,0); var b = Walker(line,1);
        float separation = float.PositiveInfinity;
        for (int i=0;i<42;i++)
        {
            Tick(a,b);
            separation = Math.Min(separation,(a.transform.position-b.transform.position).magnitude);
        }
        Check(separation>=.499f && a.transform.position.z>4f && b.transform.position.z<2f,"dos peatones cruzan en sentido contrario sin solaparse");
        Physics.Bodies.Clear();

        foreach (int layer in new[]{0,28,29,30})
        {
            Body(At(0,1),.35f,layer);
            Check(!SidewalkClearance.TryMove(At(0,0),At(0,2),null,out _),"la cápsula detecta obstáculo intermedio de capa " + layer);
            Check(!SidewalkClearance.IsFree(At(0,1),null),"no permite aparición ocupada en capa " + layer);
            Physics.Bodies.Clear();
        }
        var trigger = Body(At(0,1),.35f,0); trigger.Trigger=true;
        Check(SidewalkClearance.TryMove(At(0,0),At(0,2),null,out _),"ignora trigger sin bloquear acera");
        Physics.Bodies.Clear();
        Physics.Ground=false;
        Check(!SidewalkClearance.TryMove(At(0,0),At(0,2),null,out _),"rechaza destino sin apoyo");
        Physics.Ground=true;

        Physics.CurbHeight=.095f;
        Vector3 curb = new Vector3(0,.27f,-.02f);
        Check(SidewalkClearance.TryMove(curb,new Vector3(0,.27f,.02f),null,out Vector3 ledge)
              && Math.Abs(ledge.y-.27f)<.0001f,"desciende el bordillo manteniendo el apoyo trasero");
        Check(SidewalkClearance.TryMove(ledge,new Vector3(0,.27f,.28f),null,out Vector3 lower)
              && Math.Abs(lower.y-.175f)<.0001f,"baja al suelo al liberar la parte trasera");
        Body(new Vector3(0,.27f,.4f),.25f,0);
        Check(!SidewalkClearance.TryMove(curb,new Vector3(0,.27f,.02f),null,out _),"el apoyo trasero no permite atravesar un obstáculo");
        Physics.Bodies.Clear();
        Physics.CurbHeight=.24f;
        Check(!SidewalkClearance.TryMove(new Vector3(0,.415f,-.02f),new Vector3(0,.415f,.02f),null,out _),"el apoyo trasero no salva desniveles grandes");
        Physics.CurbHeight=0f;

        int seed = Enumerable.Range(0,100).First(s=>new Random(s).Next(2)==0);
        var fork = Graph(new[]{new Vector2(0,0),new Vector2(0,3),new Vector2(4,0)},(0,1,-1,-1),(0,2,-1,-1));
        a = Walker(fork,0,seed:seed);
        Body(At(.28f,1.6f),.35f,0);
        float farthest = 0f;
        for (int i=0;i<65;i++) { Tick(a); farthest=Math.Max(farthest,a.transform.position.z); }
        Check(farthest<1.02f && a.transform.position.x>2f,"retrocede por el carril y elige la otra acera");
        Physics.Bodies.Clear();

        var crossing = Graph(new[]{new Vector2(0,0),new Vector2(0,15)},(0,1,0,0));
        var lights = new Lights { Current = SignalLight.Green, Remaining = 30 };
        a=Walker(crossing,0,lights);
        for(int i=0;i<12;i++) Tick(a);
        Check(a.transform.position.z<.001f,"espera el rojo del eje de vehículos");
        lights.Current=SignalLight.Red; lights.Remaining=3;
        for(int i=0;i<12;i++) Tick(a);
        Check(a.transform.position.z<.001f,"rechaza rojo insuficiente para atravesar");
        lights.Remaining=22;
        for(int i=0;i<12;i++) Tick(a);
        Check(a.transform.position.z>1f,"cruza con ventana roja suficiente");
        Physics.Bodies.Clear();

        var freeCross = Graph(new[]{new Vector2(0,0),new Vector2(0,15)},(0,1,-2,-1));
        a=Walker(freeCross,0);
        var car=Body(At(5,8),1f,28);
        for(int i=0;i<12;i++) Tick(a);
        Check(a.transform.position.z<.001f,"espera un auto cerca del paso sin semáforo");
        Physics.Bodies.Remove(car);
        for(int i=0;i<12;i++) Tick(a);
        Check(a.transform.position.z>1f,"reanuda el cruce cuando el auto se aleja");
        Physics.Bodies.Clear();

        var junction = Graph(new[]{new Vector2(0,0),new Vector2(0,15),new Vector2(9,0)},(0,1,-2,-1),(0,2,-1,-1));
        a=Walker(junction,0,seed:seed);
        Body(At(.28f,7),1f,28);
        farthest = 0;
        for (int i=0;i<135;i++) { Tick(a); farthest=Math.Max(farthest,a.transform.position.z); }
        Check(farthest<.5f && a.transform.position.x>2f,"abandona un cruce ocupado y continúa por la acera");
        Physics.Bodies.Clear();
        Body(At(10,0),1f,28);
        Check(SidewalkClearance.CrossingClear(At(0,0),At(0,15)),"un auto al costado de la esquina no bloquea todo el paso");
        Physics.Bodies.Clear();
        VisitTests.Run(Check, Tick);
        Physics.Bodies.Clear();
        PopulationTests.Run(Check, Tick);
        CounterTests.Run(Check);
        Console.WriteLine("STREET_TESTS_PASSED " + passed);
    }
}
