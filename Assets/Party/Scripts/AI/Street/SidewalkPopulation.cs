using System;
using System.Collections.Generic;
using Alarma.AI.CityLife;
using UnityEngine;
using UnityEngine.Pool;
using Alarma.Core.Contracts;

namespace Alarma.AI.Street
{
    // Mantiene peatones solo alrededor del jugador: aparecen en aceras cercanas y vuelven al pool al quedar lejos.
    // Los locales cercanos reciben clientes: unos caminan hacia la puerta y, al llegar el jugador, uno ya está entrando.
    // En red lo decidirá el host para todos los jugadores; por ahora es local.
    public sealed class SidewalkPopulation : MonoBehaviour
    {
        private const float ArrivalWindow = 3f, CheckSeconds = .5f;

        [SerializeField] private SidewalkGraph graph;
        [SerializeField] private MonoBehaviour signalSource; // implementa ITrafficSignals
        [SerializeField] private SidewalkWalker[] variants;
        [SerializeField] private Transform observer;
        [SerializeField, Min(0)] private int budget = 55;
        [SerializeField, Min(0f)] private float spawnNear = 30f, spawnFar = 120f, releaseDistance = 150f;
        [SerializeField] private SidewalkVisit[] visits = Array.Empty<SidewalkVisit>();
        [SerializeField] private PedestrianSettings shopSettings;
        [Header("Clientes de los locales")]
        [SerializeField, Min(1), Tooltip("Tope de clientes por local; cada local lo baja según sus cajas (SidewalkVisit.HasRoom).")] private int customersPerShop = 11;
        [SerializeField, Min(0f)] private float shopFocusRadius = 100f;
        [SerializeField, Min(10f)] private float customerSpawnRadius = 40f;
        [Tooltip("Un salto mayor entre dos cuadros se trata como viaje con el mapa.")]
        [SerializeField, Min(10f)] private float travelJump = 40f;

        private readonly List<SidewalkWalker> active = new List<SidewalkWalker>();
        private readonly List<int> candidates = new List<int>();
        private readonly Dictionary<SidewalkVisit, float> nextCustomer = new Dictionary<SidewalkVisit, float>();
        private ObjectPool<SidewalkWalker> pool;
        private ITrafficSignals signals;
        private System.Random random;
        private SidewalkVisitPlanner planner;
        private float nextCheck, arrivalUntil;
        private bool filled, tracking;
        private Vector3 lastObserver;
        private int serial;

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
            planner = new SidewalkVisitPlanner(customersPerShop);
            pool = new ObjectPool<SidewalkWalker>(Create, w => w.gameObject.SetActive(true), Release, w => Destroy(w.gameObject), false, budget, budget * 2);
        }

        private SidewalkWalker Create() => Instantiate(variants[random.Next(variants.Length)], transform);
        private static void Release(SidewalkWalker walker) { walker.End(); walker.gameObject.SetActive(false); }

        private void Update()
        {
            if (observer == null) return;
            Vector3 p = observer.position;
            // Al empezar o tras un viaje con el mapa, la zona de llegada se puebla en el acto.
            if (!tracking || (p - lastObserver).sqrMagnitude > travelJump * travelJump) Arrive();
            lastObserver = p;
            tracking = true;
            if (Time.time < nextCheck) return;
            nextCheck = Time.time + CheckSeconds;
            ReleaseDistant(p);
            SendCustomers(p, Time.time < arrivalUntil);
            SpawnWalkers(p);
            filled = true;
        }

        private void Arrive()
        {
            filled = false;
            arrivalUntil = Time.time + ArrivalWindow;
            nextCheck = 0f;
        }

        private void ReleaseDistant(Vector3 p)
        {
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
        }

        private void SpawnWalkers(Vector3 p)
        {
            if (active.Count >= budget) return;
            // Al llegar la zona ya está poblada; después aparecen pocos por vez y fuera de la vista inmediata.
            float near = filled ? spawnNear : 6f;
            graph.NodesNear(p, spawnFar, candidates);
            int attempts = filled ? 4 : budget * 3;
            for (int i = 0; i < attempts && active.Count < budget && candidates.Count > 0; i++)
            {
                int node = candidates[random.Next(candidates.Count)];
                if (!graph.CanSpawn(node)) continue;
                Vector3 spawn = graph.Position(node);
                if ((spawn - p).sqrMagnitude < near * near || !CanPlace(spawn, 2.8f)) continue;
                Launch(node, null, VisitStart.Sidewalk);
            }
        }

        private void SendCustomers(Vector3 p, bool arriving)
        {
            if (shopSettings == null) return;
            float limit = shopFocusRadius * shopFocusRadius;
            foreach (var visit in visits)
            {
                if (visit == null || !visit.Open || !visit.HasRoom(planner.Capacity)
                    || (visit.Approach - p).sqrMagnitude > limit
                    || nextCustomer.TryGetValue(visit, out float at) && Time.time < at) continue;
                int before = visit.Customers;
                // Al llegar el local ya está en marcha: algunos comprando dentro, uno entrando y otro en camino.
                if (arriving && before == 0)
                {
                    for (int k = 0; k < planner.Capacity - 2 && visit.HasRoom(planner.Capacity) && (active.Count < budget || MakeRoom(p)); k++)
                        Launch(visit.Node, visit, VisitStart.Inside);
                    if (visit.HasRoom(planner.Capacity) && (active.Count < budget || MakeRoom(p))) SpawnAtDoor(visit);
                }
                if (visit.HasRoom(planner.Capacity) && (active.Count < budget || MakeRoom(p))) SpawnTowards(visit, p, arriving);
                // Cada local recibe clientes con pausas; si no hubo sitio libre se reintenta pronto.
                nextCustomer[visit] = Time.time + (visit.Customers > before ? 2f + (float)random.NextDouble() * 3f : 1f);
            }
        }

        // Cliente que empieza frente a la entrada y ya entra: solo al llegar, cuando la cámara acaba de cambiar.
        private void SpawnAtDoor(SidewalkVisit visit)
        {
            Vector3 spawn = visit.Approach;
            if (SidewalkClearance.TryGround(spawn, out _) && !Crowded(spawn, 1.2f) && SidewalkClearance.IsFree(spawn, null, .04f))
                Launch(visit.Node, visit, VisitStart.Door);
        }

        // Cliente que aparece en la misma acera, a unos metros, y camina hasta el local.
        private void SpawnTowards(SidewalkVisit visit, Vector3 p, bool arriving)
        {
            Vector3 door = graph.Position(visit.Node);
            graph.NodesNear(door, customerSpawnRadius, candidates);
            for (int i = 0; i < 6 && candidates.Count > 0; i++)
            {
                int node = candidates[random.Next(candidates.Count)];
                Vector3 spawn = graph.Position(node);
                if (node == visit.Node || !graph.CanSpawn(node) || (spawn - door).sqrMagnitude < 8f * 8f) continue;
                // En plena partida aparece fuera de cámara; al llegar basta con no aparecer encima del jugador.
                float distance = (spawn - p).sqrMagnitude;
                if (arriving ? distance < 6f * 6f : distance < 12f * 12f || !OutsideView(spawn)) continue;
                if (CanPlace(spawn, 2.8f) && Launch(node, visit, VisitStart.Sidewalk)) return;
            }
        }

        // Libera un paseante sin visita, fuera de cámara y lejos, para dar su lugar a un cliente.
        private bool MakeRoom(Vector3 p)
        {
            int chosen = -1;
            float farthest = spawnNear * spawnNear;
            for (int i = 0; i < active.Count; i++)
            {
                var walker = active[i];
                float distance = (walker.transform.position - p).sqrMagnitude;
                if (walker.Visiting || distance <= farthest || !OutsideView(walker.transform.position)) continue;
                chosen = i;
                farthest = distance;
            }
            if (chosen < 0) return false;
            pool.Release(active[chosen]);
            active.RemoveAt(chosen);
            return true;
        }

        private bool Launch(int node, SidewalkVisit visit, VisitStart start)
        {
            var walker = pool.Get();
            if (!walker.Begin(graph, signals, node, random.Next(), planner, visits, shopSettings, ++serial, visit, start))
            {
                pool.Release(walker);
                return false;
            }
            active.Add(walker);
            return true;
        }

        private bool CanPlace(Vector3 spawn, float spacing)
            => !Crowded(spawn, spacing) && SidewalkClearance.TryGround(spawn, out _) && SidewalkClearance.IsFree(spawn, null, .04f);

        private bool Crowded(Vector3 spawn, float spacing)
        {
            foreach (var walker in active)
                if ((walker.transform.position - spawn).sqrMagnitude < spacing * spacing) return true;
            return false;
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
            nextCustomer.Clear();
            filled = tracking = false;
        }
    }
}
