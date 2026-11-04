using System.Collections.Generic;
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

        private readonly List<SidewalkWalker> active = new List<SidewalkWalker>();
        private readonly List<int> candidates = new List<int>();
        private ObjectPool<SidewalkWalker> pool;
        private ITrafficSignals signals;
        private System.Random random;
        private float nextCheck;
        private bool filled;

        public int ActiveCount => active.Count;

        public void Configure(SidewalkGraph network, MonoBehaviour lights, SidewalkWalker[] people, Transform focus)
        {
            graph = network; signalSource = lights; variants = people; observer = focus;
        }

        private void Awake()
        {
            signals = signalSource as ITrafficSignals;
            random = new System.Random(25);
            pool = new ObjectPool<SidewalkWalker>(Create, w => w.gameObject.SetActive(true), w => w.gameObject.SetActive(false), w => Destroy(w.gameObject), false, budget, budget * 2);
        }

        private SidewalkWalker Create() => Instantiate(variants[random.Next(variants.Length)], transform);

        private void Update()
        {
            if (observer == null || Time.time < nextCheck) return;
            nextCheck = Time.time + .5f;
            Vector3 p = observer.position;
            for (int i = active.Count - 1; i >= 0; i--)
                if ((active[i].transform.position - p).sqrMagnitude > releaseDistance * releaseDistance) { pool.Release(active[i]); active.RemoveAt(i); }
            if (active.Count >= budget) return;
            // Al empezar la ciudad ya está poblada; después aparecen pocos por vez y fuera de la vista inmediata.
            float near = filled ? spawnNear : 6f;
            graph.NodesNear(p, spawnFar, candidates);
            int attempts = filled ? 4 : budget * 3;
            for (int i = 0; i < attempts && active.Count < budget && candidates.Count > 0; i++)
            {
                int node = candidates[random.Next(candidates.Count)];
                if ((graph.Position(node) - p).sqrMagnitude < near * near) continue;
                var walker = pool.Get();
                walker.Begin(graph, signals, node, random.Next());
                active.Add(walker);
            }
            filled = true;
        }
    }
}
