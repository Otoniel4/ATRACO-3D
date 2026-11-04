using System;
using System.Collections.Generic;
using UnityEngine;

namespace Alarma.AI.Street
{
    // Red peatonal de la ciudad: nodos en las aceras y tramos que los unen (aceras, esquinas y pasos de cebra).
    // Cada tramo guarda si es un cruce: -1 acera, -2 paso sin semáforo, 0 o más el semáforo que lo controla.
    public sealed class SidewalkGraph : ScriptableObject
    {
        public const int Sidewalk = -1, FreeCrossing = -2;
        public const float Height = .1f;

        [SerializeField] private Vector2[] nodes = Array.Empty<Vector2>();
        [SerializeField] private int[] first = Array.Empty<int>();
        [SerializeField] private int[] target = Array.Empty<int>(), signal = Array.Empty<int>(), axis = Array.Empty<int>();
        [SerializeField] private float cellSize = 50f;
        [SerializeField] private Vector2 origin;
        [SerializeField] private int columns;
        [SerializeField] private int[] cellFirst = Array.Empty<int>(), cellNodes = Array.Empty<int>();

        public int NodeCount => nodes.Length;
        public Vector3 Position(int node) => new Vector3(nodes[node].x, Height, nodes[node].y);
        public int EdgeStart(int node) => first[node];
        public int EdgeEnd(int node) => first[node + 1];
        public int Target(int edge) => target[edge];
        public int Signal(int edge) => signal[edge];
        public int Axis(int edge) => axis[edge];

        // Se llama al preparar la ciudad: tramos en ambos sentidos y una rejilla para buscar nodos cercanos rápido.
        public void Build(Vector2[] positions, IReadOnlyList<(int a, int b, int signal, int axis)> links, float cell)
        {
            nodes = positions;
            var lists = new List<(int to, int s, int ax)>[positions.Length];
            for (int i = 0; i < lists.Length; i++) lists[i] = new List<(int, int, int)>(3);
            foreach (var l in links) { lists[l.a].Add((l.b, l.signal, l.axis)); lists[l.b].Add((l.a, l.signal, l.axis)); }
            first = new int[positions.Length + 1];
            var to = new List<int>(); var s = new List<int>(); var ax = new List<int>();
            for (int i = 0; i < lists.Length; i++)
            {
                first[i] = to.Count;
                foreach (var e in lists[i]) { to.Add(e.to); s.Add(e.s); ax.Add(e.ax); }
            }
            first[positions.Length] = to.Count;
            target = to.ToArray(); signal = s.ToArray(); axis = ax.ToArray();
            var min = new Vector2(float.MaxValue, float.MaxValue); var max = new Vector2(float.MinValue, float.MinValue);
            foreach (var p in positions) { min = Vector2.Min(min, p); max = Vector2.Max(max, p); }
            cellSize = cell; origin = min; columns = Mathf.CeilToInt((max.x - min.x) / cell) + 1;
            int rows = Mathf.CeilToInt((max.y - min.y) / cell) + 1;
            var cells = new List<int>[columns * rows];
            for (int i = 0; i < cells.Length; i++) cells[i] = new List<int>();
            for (int i = 0; i < positions.Length; i++) cells[Cell(positions[i])].Add(i);
            cellFirst = new int[cells.Length + 1]; var flat = new List<int>(positions.Length);
            for (int i = 0; i < cells.Length; i++) { cellFirst[i] = flat.Count; flat.AddRange(cells[i]); }
            cellFirst[cells.Length] = flat.Count; cellNodes = flat.ToArray();
        }

        public void NodesNear(Vector3 position, float radius, List<int> result)
        {
            result.Clear();
            int rows = (cellFirst.Length - 1) / Mathf.Max(1, columns);
            int span = Mathf.CeilToInt(radius / cellSize);
            int cx = Mathf.FloorToInt((position.x - origin.x) / cellSize), cy = Mathf.FloorToInt((position.z - origin.y) / cellSize);
            float limit = radius * radius;
            for (int y = Mathf.Max(0, cy - span); y <= Mathf.Min(rows - 1, cy + span); y++)
                for (int x = Mathf.Max(0, cx - span); x <= Mathf.Min(columns - 1, cx + span); x++)
                {
                    int c = y * columns + x;
                    for (int k = cellFirst[c]; k < cellFirst[c + 1]; k++)
                    {
                        Vector2 p = nodes[cellNodes[k]];
                        float dx = p.x - position.x, dz = p.y - position.z;
                        if (dx * dx + dz * dz <= limit) result.Add(cellNodes[k]);
                    }
                }
        }

        private int Cell(Vector2 p) => Mathf.FloorToInt((p.y - origin.y) / cellSize) * columns + Mathf.FloorToInt((p.x - origin.x) / cellSize);
    }
}
