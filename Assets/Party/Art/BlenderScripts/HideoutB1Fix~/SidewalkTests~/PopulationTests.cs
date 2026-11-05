using System;
using System.Collections.Generic;
using System.Reflection;
using Alarma.AI.CityLife;
using Alarma.AI.Street;
using UnityEngine;

namespace UnityEngine.Pool
{
    // Pool mínimo con el mismo contrato que usa SidewalkPopulation.
    public sealed class ObjectPool<T> where T : class
    {
        private readonly Func<T> create;
        private readonly Action<T> onGet, onRelease;
        private readonly Stack<T> free = new Stack<T>();
        public ObjectPool(Func<T> create, Action<T> onGet, Action<T> onRelease, Action<T> onDestroy, bool collectionCheck, int defaultCapacity, int maxSize)
        { this.create = create; this.onGet = onGet; this.onRelease = onRelease; }
        public T Get() { T item = free.Count > 0 ? free.Pop() : create(); onGet?.Invoke(item); return item; }
        public void Release(T item) { onRelease?.Invoke(item); free.Push(item); }
    }
}

// Revisión 23: llegada con el mapa y clientes que la población envía a los locales cercanos.
internal static class PopulationTests
{
    private const BindingFlags Hidden = BindingFlags.NonPublic | BindingFlags.Instance;
    private static readonly MethodInfo Awake = typeof(SidewalkPopulation).GetMethod("Awake", Hidden);
    private static readonly MethodInfo Update = typeof(SidewalkPopulation).GetMethod("Update", Hidden);
    private static readonly FieldInfo Active = typeof(SidewalkPopulation).GetField("active", Hidden);

    public static void Run(Action<bool,string> check, Action<SidewalkWalker[]> tick)
    {
        // Acera recta de 400 m con un local a 300 m del inicio.
        var nodes = new Vector2[201];
        var edges = new List<(int,int,int,int)>();
        for (int i = 0; i < nodes.Length; i++)
        {
            nodes[i] = new Vector2(i * 2, 0);
            if (i > 0) edges.Add((i - 1, i, SidewalkGraph.Sidewalk, -1));
        }
        var graph = new SidewalkGraph();
        graph.Build(nodes, edges, 50);
        var shop = new SidewalkVisit(new ShopActivity(), 150, 0, new Vector3(300, .175f, 1.7f));
        MonoBehaviour.Factory = original =>
        {
            var copy = new SidewalkWalker { Component = new PedestrianActor() };
            copy.Configure(new Animator());
            return copy;
        };
        var camera = new Camera();
        Camera.main = camera;
        var observer = new Transform { position = new Vector3(0, .175f, 0) };
        var population = new SidewalkPopulation();
        population.Configure(graph, null, new[]{ new SidewalkWalker() }, observer);
        population.ConfigureVisits(new[]{ shop }, new PedestrianSettings());
        typeof(SidewalkPopulation).GetField("budget", Hidden).SetValue(population, 12);
        typeof(SidewalkPopulation).GetField("customersPerShop", Hidden).SetValue(population, 3);
        Awake.Invoke(population, null);

        Step(population);
        var walkers = (List<SidewalkWalker>)Active.GetValue(population);
        check(walkers.Count == 12 && shop.Customers == 0 && AllWithin(walkers, observer.position, 120f),
            "al empezar llena la zona del jugador sin enviar clientes a locales lejanos");

        observer.position = new Vector3(296, .175f, 0); // viaje con M frente al local
        Time.time += .02f;
        Step(population);
        check(walkers.Count == 12 && AllWithin(walkers, observer.position, 120f),
            "al viajar con M repuebla la zona de llegada en el acto");
        var atDoor = walkers.Find(w => (w.transform.position - shop.Approach).sqrMagnitude < .0001f);
        var inside = walkers.Find(w => ((PedestrianActor)w.Component).Insides == 1);
        check(atDoor != null && inside != null && shop.Customers == 3,
            "al llegar ya hay un cliente comprando dentro, otro en la puerta y otro camina hacia el local");
        tick(new[]{ atDoor });
        check(((PedestrianActor)atDoor.Component).Begins == 1, "el cliente de la puerta empieza su rutina dentro");

        // Cuando uno termina, con la cámara mirando a otro lado llega otro cliente aunque el cupo de peatones esté lleno.
        atDoor.End();
        camera.Viewport = p => new Vector3(2f, 2f, 1f);
        Time.time += 11f;
        Step(population);
        check(shop.Customers == 3 && walkers.Count == 12, "con el cupo lleno libera un paseante lejano y envía otro cliente");
        // Aquí los peatones no se mueven: a los 22 s quietos se reciclan fuera de cámara, por eso solo se mide el cupo.
        Time.time += 11f;
        Step(population);
        check(shop.Customers == 3, "no supera la capacidad del local");
        Camera.main = null;
    }

    private static void Step(SidewalkPopulation population) => Update.Invoke(population, null);

    private static bool AllWithin(List<SidewalkWalker> walkers, Vector3 p, float radius)
        => walkers.TrueForAll(w => (w.transform.position - p).sqrMagnitude <= radius * radius);
}
