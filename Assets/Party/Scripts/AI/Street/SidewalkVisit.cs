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
        // Reservas de la partida en curso; no se guardan en la escena.
        private List<SidewalkWalker> customers;
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
        internal int Customers => customers?.Count ?? 0;

        internal bool Open => shop != null && shop.isActiveAndEnabled && shop.IsConfigured && shop.Service.Stock > 0;
        internal bool Affords(int wallet) => shop.Tasks.IsWithdrawal || wallet >= shop.Tasks.PriceCents;

        internal bool Available(int wallet, int capacity) => Open && Affords(wallet) && HasRoom(capacity) && Time.time >= availableAt;

        // Nunca más clientes que puestos ni que lugares en las filas de sus cajas (más dos mirando): el resto esperaría
        // afuera sin poder entrar. Con varias cajas entra más gente.
        internal bool HasRoom(int capacity)
            => Customers < Math.Min(capacity, Math.Max(1, Math.Min(shop.StationCount, shop.CheckoutCount * shop.Lanes.Capacity + 2)));

        // Cada reserva separa la siguiente llegada para que los clientes no coincidan en la puerta.
        internal void Reserve(SidewalkWalker visitor, float spacing)
        {
            customers ??= new List<SidewalkWalker>();
            if (!customers.Contains(visitor)) customers.Add(visitor);
            availableAt = Mathf.Max(availableAt, Time.time + spacing);
        }

        internal void Release(SidewalkWalker visitor, float cooldown)
        {
            if (customers == null || !customers.Remove(visitor)) return;
            availableAt = Mathf.Max(availableAt, Time.time + cooldown);
        }
    }

    // Busca locales alcanzables por el mismo lado de la calle. Cada local admite pocos clientes a la vez.
    internal sealed class SidewalkVisitPlanner
    {
        public const float ArrivalSpacing = 2.5f;
        private const int SearchLimit = 240;
        private const float SearchRadius = 55f;
        private readonly Queue<int> pending = new Queue<int>();
        private readonly Dictionary<int, int> cameFrom = new Dictionary<int, int>();
        private readonly List<int> order = new List<int>();

        public SidewalkVisitPlanner(int customersPerShop = 1) => Capacity = Math.Max(1, customersPerShop);

        public int Capacity { get; }

        // El local disponible más cercano por la acera, en orden de recorrido.
        public SidewalkVisit Find(SidewalkGraph graph, int from, SidewalkVisit[] visits, int wallet, List<int> path)
        {
            path.Clear();
            if (visits.Length == 0) return null;
            Explore(graph, from);
            foreach (int current in order)
                foreach (var visit in visits)
                {
                    if (visit.Node != current || !visit.Available(wallet, Capacity)) continue;
                    Trace(from, current, path);
                    return visit;
                }
            return null;
        }

        // Ruta por la misma acera hacia un local concreto: la usan los clientes que envía la población.
        public bool Route(SidewalkGraph graph, int from, SidewalkVisit target, List<int> path)
        {
            path.Clear();
            Explore(graph, from);
            if (!cameFrom.ContainsKey(target.Node)) return false;
            Trace(from, target.Node, path);
            return true;
        }

        private void Explore(SidewalkGraph graph, int from)
        {
            Vector3 origin = graph.Position(from);
            pending.Clear();
            cameFrom.Clear();
            order.Clear();
            cameFrom.Add(from, -1);
            pending.Enqueue(from);
            while (pending.Count > 0)
            {
                int current = pending.Dequeue();
                order.Add(current);
                for (int edge = graph.EdgeStart(current); edge < graph.EdgeEnd(current); edge++)
                {
                    int next = graph.Target(edge);
                    if (cameFrom.Count >= SearchLimit || graph.Signal(edge) != SidewalkGraph.Sidewalk
                        || cameFrom.ContainsKey(next) || (graph.Position(next) - origin).sqrMagnitude > SearchRadius * SearchRadius) continue;
                    cameFrom.Add(next, current);
                    pending.Enqueue(next);
                }
            }
        }

        private void Trace(int from, int to, List<int> path)
        {
            for (int n = to; n != from; n = cameFrom[n]) path.Add(n);
            path.Reverse();
        }
    }
}
