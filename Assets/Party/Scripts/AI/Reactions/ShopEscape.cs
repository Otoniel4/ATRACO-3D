using System.Collections.Generic;
using UnityEngine;
using Alarma.AI.CityLife;

namespace Alarma.AI.Reactions
{
    // Por dónde se escapa de un local. Si el civil está dentro de uno (pisa su suelo o está bajo su techo), busca un
    // camino por la red de pasillos que el local ya usa para sus clientes (TrafficGraph, casillas de medio metro) desde
    // donde está hasta la acera, pasando por la puerta y rodeando a la amenaza. Si la amenaza tapa todos los caminos,
    // no hay salida y el civil se aleja por dentro. No busca locales por la escena: se lo pregunta al suelo que pisa.
    internal static class ShopEscape
    {
        private const int Structure = ~((1 << 28) | (1 << 29) | (1 << 30) | (1 << 31)); // sin autos, personajes ni interfaz
        private const float JoinDistance = 2.5f; // hasta dónde busca la casilla de pasillo más cercana
        private const float ThreatClearance = 3f; // casillas que evita alrededor de la amenaza

        public static bool TryFind(Vector3 position, Vector3 threat, out Vector3[] route, out ShopDoor door)
        {
            route = null; door = null;
            Vector3 chest = position + Vector3.up;
            var shop = Physics.Raycast(chest, Vector3.down, out var floor, 2.5f, Structure, QueryTriggerInteraction.Ignore) ? ShopOf(floor.collider) : null;
            if (shop == null && Physics.Raycast(chest, Vector3.up, out var roof, 6f, Structure, QueryTriggerInteraction.Ignore)) shop = ShopOf(roof.collider);
            if (shop == null || shop.ExitRoute.Length == 0) return false;
            var graph = shop.TryGetComponent<CityTrafficController>(out var traffic) ? traffic.Graph : null;
            if (graph == null) return false;
            int start = graph.Nearest(position, JoinDistance);
            int goal = graph.Nearest(shop.ExitRoute[shop.ExitRoute.Length - 1].position, JoinDistance);
            if (start < 0 || goal < 0) return false;
            route = Path(graph, start, goal, threat);
            door = shop.Entrance;
            return route != null;
        }

        // El local al que pertenece una pieza: su rutina de compra cuelga directamente del local.
        private static ShopActivity ShopOf(Collider piece)
        {
            for (var t = piece.transform; t != null; t = t.parent)
                foreach (Transform child in t)
                    if (child.TryGetComponent<ShopActivity>(out var shop)) return shop;
            return null;
        }

        // Camino más corto en casillas (búsqueda en anchura) sin pisar las que rodean a la amenaza.
        private static Vector3[] Path(TrafficGraph graph, int start, int goal, Vector3 threat)
        {
            var cameFrom = new int[graph.Count];
            for (int i = 0; i < cameFrom.Length; i++) cameFrom[i] = -1;
            cameFrom[start] = start;
            var pending = new Queue<int>();
            pending.Enqueue(start);
            while (pending.Count > 0 && cameFrom[goal] < 0)
            {
                int cell = pending.Dequeue();
                foreach (int next in graph.Neighbours(cell))
                {
                    if (cameFrom[next] >= 0) continue;
                    Vector3 away = graph.Cells[next].Position - threat;
                    away.y = 0f;
                    if (away.sqrMagnitude < ThreatClearance * ThreatClearance) continue;
                    cameFrom[next] = cell;
                    pending.Enqueue(next);
                }
            }
            if (cameFrom[goal] < 0) return null;
            var steps = new List<Vector3>();
            for (int cell = goal; cell != start; cell = cameFrom[cell]) steps.Add(graph.Cells[cell].Position);
            steps.Add(graph.Cells[start].Position); // primero se mete al pasillo más cercano
            steps.Reverse();
            return steps.ToArray();
        }
    }
}
