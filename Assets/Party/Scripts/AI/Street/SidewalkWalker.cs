using System;
using System.Collections.Generic;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.AI.CityLife;

namespace Alarma.AI.Street
{
    // Peatón que pasea por la red de aceras: sigue tramos al azar sin volver atrás y, ante un paso con semáforo,
    // espera a que la vía que va a cruzar esté en rojo con tiempo suficiente para llegar al otro lado.
    // Dónde empieza un cliente enviado a un local: caminando por la acera, frente a la puerta o ya dentro comprando.
    internal enum VisitStart { Sidewalk, Door, Inside }

    public sealed class SidewalkWalker : MonoBehaviour
    {
        private static readonly int SpeedParameter = Animator.StringToHash("Speed");
        private const float WalkSpeed = 1.4f, AnimatorWalk = 1.6f, TurnSpeed = 300f, CrossingMargin = 2f;
        private enum VisitPhase { Walking, Approaching, Inside, Returning }

        [SerializeField] private Animator animator;
        private SidewalkGraph graph;
        private ITrafficSignals signals;
        private System.Random random;
        private int previous, current, next, edge, avoided;
        private float blockedFor, retryAt, avoidUntil;
        private bool waiting, retreating, aligning;
        private Vector3 target;
        private SidewalkVisitPlanner planner;
        private SidewalkVisit[] shops;
        private SidewalkVisit visit;
        private PedestrianActor shopper;
        private PedestrianSettings shopSettings;
        private readonly List<int> visitPath = new List<int>();
        private VisitPhase phase;
        private int serial, wallet, visitStep;
        private float reconsiderAt, crossingWaitUntil, lastMovedAt;
        private Vector3 lastProgress;
        private bool triedExit;

        public bool NeedsReplacement => (phase != VisitPhase.Inside || shopper.Failed) && Time.time - lastMovedAt > 22f;
        internal bool Visiting => visit != null;

        public void Configure(Animator body) => animator = body;

        public void Begin(SidewalkGraph network, ITrafficSignals lights, int node, int seed)
            => Begin(network, lights, node, seed, null, Array.Empty<SidewalkVisit>(), null, 0);

        // assigned: local al que la población envía este peatón; start: dónde empieza esa visita.
        internal bool Begin(SidewalkGraph network, ITrafficSignals lights, int node, int seed,
            SidewalkVisitPlanner visitPlanner, SidewalkVisit[] destinations, PedestrianSettings settings, int id,
            SidewalkVisit assigned = null, VisitStart start = VisitStart.Sidewalk)
        {
            graph = network; signals = lights; random = new System.Random(seed);
            previous = -1; current = node; avoided = -1; next = -1;
            planner = visitPlanner; shops = destinations; shopSettings = settings; serial = id;
            shopper = GetComponent<PedestrianActor>();
            phase = VisitPhase.Walking;
            visit = null; visitStep = 0; triedExit = false;
            waiting = retreating = aligning = false; blockedFor = 0f;
            wallet = 200000;
            foreach (var destination in shops)
                wallet = Mathf.Max(wallet, destination.Shop.Tasks.CustomerWalletCents);
            if (shops.Length > 0) wallet = (int)(wallet * (.35 + .65 * random.NextDouble()));
            reconsiderAt = Time.time + .5f + (float)random.NextDouble() * 2.5f;
            if (assigned != null && !Assign(assigned, start)) { graph = null; return false; }
            // Dentro del local ya lo colocó su rutina en el puesto que reservó.
            if (phase != VisitPhase.Inside) transform.position = phase == VisitPhase.Approaching ? assigned.Approach : graph.Position(node);
            lastProgress = transform.position;
            lastMovedAt = Time.time;
            if (phase != VisitPhase.Walking) return true;
            ChooseNext();
            if (next >= 0 && Flat(target - transform.position).sqrMagnitude > .0001f)
                transform.rotation = Quaternion.LookRotation(Flat(target - transform.position));
            return true;
        }

        // Reserva el local antes de dar el primer paso: va por su acera, ya está en la entrada o ya está comprando dentro.
        private bool Assign(SidewalkVisit destination, VisitStart start)
        {
            if (shopper == null || planner == null || shopSettings == null) return false;
            if (start == VisitStart.Sidewalk)
            {
                if (!planner.Route(graph, current, destination, visitPath)) return false;
            }
            else
            {
                current = destination.Node;
                visitPath.Clear();
            }
            if (!destination.Affords(wallet)) wallet = Mathf.Max(wallet, destination.Shop.Tasks.CustomerWalletCents);
            var shop = destination.Shop;
            // Parte frente a su local; la rutina interior lo lleva enseguida al puesto que reserva.
            if (start == VisitStart.Inside) transform.position = graph.Position(destination.Node);
            if (start == VisitStart.Inside && !shopper.BeginInside(serial, shop, shopSettings, destination.WalkPoint, shop.Traffic, wallet)) return false;
            visit = destination;
            visit.Reserve(this, SidewalkVisitPlanner.ArrivalSpacing);
            if (start == VisitStart.Door) phase = VisitPhase.Approaching;
            if (start == VisitStart.Inside) phase = VisitPhase.Inside;
            return true;
        }

        private void ChooseNext()
        {
            int start = graph.EdgeStart(current), count = graph.EdgeEnd(current) - start;
            next = -1; retreating = false; blockedFor = 0f;
            if (count == 0) return;
            if (visit == null && shopper != null && planner != null && shopSettings != null && Time.time >= reconsiderAt)
            {
                reconsiderAt = Time.time + 2f + (float)random.NextDouble() * 3f;
                visit = planner.Find(graph, current, shops, wallet, visitPath);
                visit?.Reserve(this, SidewalkVisitPlanner.ArrivalSpacing);
                visitStep = 0;
            }
            if (visit != null)
            {
                if (current == visit.Node) { phase = VisitPhase.Approaching; return; }
                if (visitStep < visitPath.Count)
                    for (int candidate = start; candidate < start + count; candidate++)
                        if (graph.Target(candidate) == visitPath[visitStep]) { Follow(candidate); return; }
                ReleaseVisit(4f);
            }
            // Se evita volver por donde vino salvo en un callejón sin salida.
            int pick = random.Next(count);
            for (int pass = 0; pass < 2 && next < 0; pass++)
            {
                for (int i = 0; i < count; i++)
                {
                    int candidate = start + (pick + i) % count;
                    int destination = graph.Target(candidate);
                    if (destination == avoided && Time.time < avoidUntil) continue;
                    if (pass == 0 && count > 1 && destination == previous) continue;
                    Follow(candidate); return;
                }
            }
            retryAt = Time.time + .3f + (float)random.NextDouble() * .6f;
        }

        private void Follow(int candidate)
        {
            edge = candidate;
            next = graph.Target(edge);
            target = graph.LaneStart(current, next);
            aligning = true;
            waiting = graph.Signal(edge) != SidewalkGraph.Sidewalk;
        }

        private void Update()
        {
            if (graph == null) { Animate(0f); return; }
            if ((lastProgress - transform.position).sqrMagnitude > .045f * .045f)
            {
                lastMovedAt = Time.time;
                lastProgress = transform.position;
            }
            if (phase != VisitPhase.Walking) { VisitShop(); return; }
            if (next < 0)
            {
                if (Time.time >= retryAt) ChooseNext();
                Animate(0f); return;
            }
            Vector3 position = transform.position;
            Vector3 toTarget = Flat(target - position);
            if (waiting && !aligning)
            {
                float crossing = toTarget.magnitude / WalkSpeed + CrossingMargin;
                int s = graph.Signal(edge), a = graph.Axis(edge);
                bool allowed = (s == SidewalkGraph.FreeCrossing
                    || signals != null && signals.Light(s, a) == SignalLight.Red && signals.SecondsUntilGreen(s, a) > crossing)
                    && SidewalkClearance.CrossingClear(position, target, s == SidewalkGraph.FreeCrossing);
                if (!allowed)
                {
                    Turn(toTarget); Animate(0f);
                    if (Time.time >= crossingWaitUntil) Detour();
                    return;
                }
                waiting = false;
            }
            float step = WalkSpeed * Mathf.Min(Time.deltaTime, .1f);
            bool arrived = toTarget.magnitude <= step;
            Vector3 desired = arrived ? target : position + toTarget.normalized * step;
            if (!SidewalkClearance.TryMove(position, desired, transform, out Vector3 moved))
            {
                blockedFor += Time.deltaTime;
                Animate(0f);
                if (blockedFor > 1.6f)
                {
                    if (aligning) Detour();
                    else
                    {
                        blockedFor = 0f;
                        if (retreating && graph.Signal(edge) == SidewalkGraph.Sidewalk
                            && (target - graph.LaneStart(current, next)).sqrMagnitude < .01f)
                            target = graph.LaneTarget(next, current);
                        else
                        {
                            retreating = !retreating;
                            target = retreating ? graph.LaneStart(current, next) : graph.LaneTarget(current, next);
                        }
                    }
                }
                return;
            }
            transform.position = moved;
            blockedFor = 0f;
            Turn(toTarget);
            Animate(AnimatorWalk);
            if (arrived)
            {
                if (aligning)
                {
                    aligning = false;
                    target = graph.LaneTarget(current, next);
                    crossingWaitUntil = Time.time + 5f + (float)random.NextDouble() * 4f;
                    return;
                }
                if (retreating) { Detour(); return; }
                previous = current;
                current = next;
                if (visit != null) visitStep++;
                ChooseNext();
            }
        }

        private void Detour()
        {
            avoided = next;
            avoidUntil = Time.time + 6f + (float)random.NextDouble() * 4f;
            ReleaseVisit(4f);
            ChooseNext();
        }

        private void VisitShop()
        {
            if (phase == VisitPhase.Inside)
            {
                if (shopper.Failed)
                {
                    if (!triedExit) { triedExit = true; shopper.TryLeaveVisit(); }
                    return;
                }
                if (shopper.CurrentState != PedestrianState.Completed) return;
                wallet = shopper.WalletCents;
                shopper.Suspend();
                phase = VisitPhase.Returning;
                blockedFor = 0f;
                ReleaseVisit(1.5f); // ya salió: libera su lugar para que entre el siguiente cliente
            }

            Vector3 destination = phase == VisitPhase.Approaching ? visit.Approach : graph.Position(current);
            Vector3 position = transform.position;
            Vector3 direction = Flat(destination - position);
            float step = WalkSpeed * Mathf.Min(Time.deltaTime, .1f);
            bool arrived = direction.sqrMagnitude <= step * step;
            Vector3 proposed = arrived ? destination : position + direction.normalized * step;
            if (!SidewalkClearance.TryMove(position, proposed, transform, out Vector3 moved) && !Sidestep(position, direction, step, out moved))
            {
                blockedFor += Time.deltaTime;
                Animate(0f);
                if (phase == VisitPhase.Approaching && blockedFor > 2.5f) { phase = VisitPhase.Returning; blockedFor = 0f; }
                // De vuelta a la acera y bloqueado (otra persona de frente, un árbol): sigue su camino por otro nodo.
                if (phase == VisitPhase.Returning && blockedFor > 2f) { blockedFor = 0f; phase = VisitPhase.Walking; ReleaseVisit(3f); ChooseNext(); }
                return;
            }
            transform.position = moved;
            Turn(direction);
            Animate(AnimatorWalk);
            blockedFor = 0f;
            if (!arrived) return;
            if (phase == VisitPhase.Approaching)
            {
                var shop = visit.Shop;
                if (shop != null && shop.isActiveAndEnabled && shopper.Begin(serial, moved, shop, shopSettings, true,
                    visit.WalkPoint, shop.Traffic, true, wallet))
                {
                    triedExit = false;
                    phase = VisitPhase.Inside;
                    return;
                }
                shopper.Suspend();
                phase = VisitPhase.Returning;
                return;
            }
            phase = VisitPhase.Walking;
            ReleaseVisit(5f);
            ChooseNext();
        }

        // Esquiva como una persona: si el paso recto está ocupado, prueba un poco hacia los costados.
        private bool Sidestep(Vector3 position, Vector3 direction, float step, out Vector3 moved)
        {
            moved = position;
            if (direction.sqrMagnitude < .0001f) return false;
            foreach (float angle in SidestepAngles)
            {
                Vector3 proposed = position + Quaternion.AngleAxis(angle, Vector3.up) * direction.normalized * step;
                if (SidewalkClearance.TryMove(position, proposed, transform, out moved)) return true;
            }
            return false;
        }

        private void ReleaseVisit(float cooldown)
        {
            if (visit == null) return;
            visit.Release(this, cooldown);
            visit = null;
            reconsiderAt = Time.time + 8f + (float)random.NextDouble() * 8f;
        }

        internal void End()
        {
            if (shopper != null) shopper.Suspend();
            ReleaseVisit(4f);
            graph = null;
        }

        private static readonly float[] SidestepAngles = { 35f, -35f, 70f, -70f };

        private void Animate(float speed) { if (animator != null) animator.SetFloat(SpeedParameter, speed); }
        private void Turn(Vector3 direction)
        {
            if (direction.sqrMagnitude < .0001f) return;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(direction), TurnSpeed * Time.deltaTime);
        }

        private static Vector3 Flat(Vector3 v) { v.y = 0f; return v; }
    }
}
