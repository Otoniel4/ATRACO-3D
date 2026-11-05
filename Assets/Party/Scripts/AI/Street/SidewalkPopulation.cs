using System;
using System.Collections.Generic;
using Alarma.AI.CityLife;
using UnityEngine;
using UnityEngine.Pool;
using Alarma.Core.Contracts;

namespace Alarma.AI.Street
{
    // Mantiene peatones solo alrededor del jugador: aparecen en aceras cercanas y vuelven al pool al quedar lejos.
    // En red lo decidirá el host para todos los jugadores; por ahora es local.
    public sealed class SidewalkPopulation : MonoBehaviour
    {
        [SerializeField] private SidewalkGraph graph;
        [SerializeField] private MonoBehaviour signalSource; // implementa ITrafficSignals
        [SerializeField] private SidewalkWalker[] variants;
        [SerializeField] private Transform observer;
        [SerializeField, Min(0)] private int budget = 45;
        [SerializeField, Min(0f)] private float spawnNear = 30f, spawnFar = 120f, releaseDistance = 150f;
        [SerializeField] private SidewalkVisit[] visits = Array.Empty<SidewalkVisit>();
        [SerializeField] private PedestrianSettings shopSettings;

        private readonly List<SidewalkWalker> active = new List<SidewalkWalker>();
        private readonly List<int> candidates = new List<int>();
        private ObjectPool<SidewalkWalker> pool;
        private ITrafficSignals signals;
        private System.Random random;
        private float nextCheck;
        private bool filled;
        private int serial;
        private readonly SidewalkVisitPlanner planner = new SidewalkVisitPlanner();

        public int ActiveCount => active.Count;

        public void Configure(SidewalkGraph network, MonoBehaviour lights, SidewalkWalker[] people, Transform focus)
        {
            graph = network; signalSource = lights; variants = people; observer = focus;
        }

        public void ConfigureVisits(SidewalkVisit[] destinations, PedestrianSettings settings)
        {
            visits = destinations;
            shopSettings = settings;
        }

        private void Awake()
        {
            signals = signalSource as ITrafficSignals;
            random = new System.Random(25);
            pool = new ObjectPool<SidewalkWalker>(Create, w => w.gameObject.SetActive(true), Release, w => Destroy(w.gameObject), false, budget, budget * 2);
        }

        private SidewalkWalker Create() => Instantiate(variants[random.Next(variants.Length)], transform);
        private static void Release(SidewalkWalker walker) { walker.End(); walker.gameObject.SetActive(false); }

        private void Update()
        {
            if (observer == null || Time.time < nextCheck) return;
            nextCheck = Time.time + .5f;
            Vector3 p = observer.position;
            for (int i = active.Count - 1; i >= 0; i--)
            {
                var walker = active[i];
                float distance = (walker.transform.position - p).sqrMagnitude;
                if (distance > releaseDistance * releaseDistance
                    || walker.NeedsReplacement && distance > 38f * 38f && OutsideView(walker.transform.position))
                {
                    pool.Release(walker);
                    active.RemoveAt(i);
                }
            }
            if (active.Count >= budget) return;
            // Al empezar la ciudad ya está poblada; después aparecen pocos por vez y fuera de la vista inmediata.
            float near = filled ? spawnNear : 6f;
            graph.NodesNear(p, spawnFar, candidates);
            int attempts = filled ? 4 : budget * 3;
            for (int i = 0; i < attempts && active.Count < budget && candidates.Count > 0; i++)
            {
                int node = candidates[random.Next(candidates.Count)];
                if (!graph.CanSpawn(node)) continue;
                if ((graph.Position(node) - p).sqrMagnitude < near * near) continue;
                Vector3 spawn = graph.Position(node);
                if (active.Exists(w => (w.transform.position - spawn).sqrMagnitude < 2.8f * 2.8f)) continue;
                if (!SidewalkClearance.TryGround(spawn, out _) || !SidewalkClearance.IsFree(spawn, null, .04f)) continue;
                var walker = pool.Get();
                walker.Begin(graph, signals, node, random.Next(), planner, visits, shopSettings, ++serial);
                active.Add(walker);
            }
            filled = true;
        }

        private static bool OutsideView(Vector3 position)
        {
            var camera = Camera.main;
            if (camera == null) return false;
            Vector3 viewport = camera.WorldToViewportPoint(position + Vector3.up * .85f);
            return viewport.z < 0f || viewport.x < -.12f || viewport.x > 1.12f || viewport.y < -.12f || viewport.y > 1.12f;
        }

        private void OnDisable()
        {
            if (pool == null) return;
            foreach (var walker in active)
                if (walker != null) pool.Release(walker);
            active.Clear();
            filled = false;
        }
    }
}
