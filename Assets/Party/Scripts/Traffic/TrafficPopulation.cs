using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Pool;
using Alarma.Core.Contracts;

namespace Alarma.Traffic
{
    // Autos solo alrededor del jugador: aparecen en carriles cercanos sin pisar a otro auto y vuelven al pool al quedar lejos.
    // En red lo decidirá el host para todos los jugadores; por ahora es local.
    public sealed class TrafficPopulation : MonoBehaviour
    {
        private const int Vehicles = 1 << 28;

        [SerializeField] private RoadNetwork network;
        [SerializeField] private MonoBehaviour signalSource; // implementa ITrafficSignals
        [SerializeField] private TrafficCar[] variants;
        [SerializeField] private Transform observer;
        [SerializeField, Min(0)] private int budget = 26;
        [SerializeField, Min(0f)] private float spawnNear = 60f, spawnFar = 230f, releaseDistance = 280f;

        private readonly List<TrafficCar> active = new List<TrafficCar>();
        private readonly List<int> candidates = new List<int>();
        private ObjectPool<TrafficCar> pool;
        private ITrafficSignals signals;
        private System.Random random;
        private float nextCheck;
        private bool filled;

        public int ActiveCount => active.Count;

        public void Configure(RoadNetwork roads, MonoBehaviour lights, TrafficCar[] cars, Transform focus)
        {
            network = roads; signalSource = lights; variants = cars; observer = focus;
        }

        private void Awake()
        {
            signals = signalSource as ITrafficSignals;
            random = new System.Random(52);
            pool = new ObjectPool<TrafficCar>(() => Instantiate(variants[random.Next(variants.Length)], transform),
                c => c.gameObject.SetActive(true), c => c.gameObject.SetActive(false), c => Destroy(c.gameObject), false, budget, budget * 2);
        }

        private void Update()
        {
            if (observer == null || Time.time < nextCheck) return;
            nextCheck = Time.time + .5f;
            Vector3 p = observer.position;
            for (int i = active.Count - 1; i >= 0; i--)
                if ((active[i].transform.position - p).sqrMagnitude > releaseDistance * releaseDistance) { pool.Release(active[i]); active.RemoveAt(i); }
            if (active.Count >= budget) return;
            float near = filled ? spawnNear : 25f;
            candidates.Clear();
            for (int l = 0; l < network.LinkCount; l++)
            {
                float d = (network.Point(l, network.PointCount(l) / 2) - p).sqrMagnitude;
                if (d > near * near && d < spawnFar * spawnFar) candidates.Add(l);
            }
            int attempts = filled ? 3 : budget * 2;
            for (int i = 0; i < attempts && active.Count < budget && candidates.Count > 0; i++)
            {
                int link = candidates[random.Next(candidates.Count)];
                if (network.PointCount(link) < 3 || Physics.CheckSphere(network.Point(link, network.PointCount(link) / 2), 9f, Vehicles, QueryTriggerInteraction.Ignore)) continue;
                var car = pool.Get();
                car.Begin(network, signals, link, network.PointCount(link) / 2, random.Next());
                active.Add(car);
                Physics.SyncTransforms(); // el siguiente intento ya ve este auto
            }
            filled = true;
        }
    }
}
