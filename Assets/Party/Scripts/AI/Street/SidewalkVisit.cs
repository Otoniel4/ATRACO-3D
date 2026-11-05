using System;
using System.Collections.Generic;
using Alarma.AI.CityLife;
using UnityEngine;

namespace Alarma.AI.Street
{
    [Serializable]
    public sealed class SidewalkVisit
    {
        [SerializeField] private ShopActivity shop;
        [SerializeField] private int node, walkPoint;
        [SerializeField] private Vector3 approach;
        private SidewalkWalker customer;
        private float availableAt;

        public SidewalkVisit(ShopActivity activity, int streetNode, int marker, Vector3 feet)
        {
            shop = activity;
            node = streetNode;
            walkPoint = marker;
            approach = feet;
        }

        public ShopActivity Shop => shop;
        public int Node => node;
        public int WalkPoint => walkPoint;
        public Vector3 Approach => approach;

        internal bool Available(int wallet) => shop != null && shop.isActiveAndEnabled && shop.IsConfigured
            && shop.Service.Stock > 0 && (shop.Tasks.IsWithdrawal || wallet >= shop.Tasks.PriceCents)
            && customer == null && Time.time >= availableAt;

        internal void Reserve(SidewalkWalker visitor) => customer = visitor;

        internal void Release(SidewalkWalker visitor, float cooldown)
        {
            if (customer != visitor) return;
            customer = null;
            availableAt = Time.time + cooldown;
        }
    }

    // Busca locales alcanzables por el mismo lado de la calle. Cada reserva admite un cliente.
    internal sealed class SidewalkVisitPlanner
    {
        private const int SearchLimit = 160;
        private const float SearchRadius = 32f;
        private readonly Queue<int> pending = new Queue<int>();
        private readonly Dictionary<int, int> cameFrom = new Dictionary<int, int>();

        public SidewalkVisit Find(SidewalkGraph graph, int from, SidewalkVisit[] visits, int wallet, List<int> path)
        {
            path.Clear();
            if (visits.Length == 0) return null;
            Vector3 origin = graph.Position(from);
            pending.Clear();
            cameFrom.Clear();
            cameFrom.Add(from, -1);
            pending.Enqueue(from);
            while (pending.Count > 0)
            {
                int current = pending.Dequeue();
                foreach (var visit in visits)
                {
                    if (visit.Node != current || !visit.Available(wallet)) continue;
                    for (int n = current; n != from; n = cameFrom[n]) path.Add(n);
                    path.Reverse();
                    return visit;
                }
                for (int edge = graph.EdgeStart(current); edge < graph.EdgeEnd(current); edge++)
                {
                    int next = graph.Target(edge);
                    if (cameFrom.Count >= SearchLimit || graph.Signal(edge) != SidewalkGraph.Sidewalk
                        || cameFrom.ContainsKey(next) || (graph.Position(next) - origin).sqrMagnitude > SearchRadius * SearchRadius) continue;
                    cameFrom.Add(next, current);
                    pending.Enqueue(next);
                }
            }
            return null;
        }
    }
}
