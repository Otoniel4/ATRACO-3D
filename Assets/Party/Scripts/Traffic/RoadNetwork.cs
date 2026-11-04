using System;
using System.Collections.Generic;
using UnityEngine;

namespace Alarma.Traffic
{
    // Qué hay al final de un carril: nada, semáforo, pare o ceda el paso (rotonda).
    public enum LinkControl { Free, Signal, Stop, Yield }

    // Carriles de la ciudad: cada enlace es un carril de un tramo, en un sentido, que termina en una línea de parada.
    // Guarda qué controla ese final (semáforo con su eje, pare, ceda en rotonda o nada) y a qué enlaces puede seguir.
    public sealed class RoadNetwork : ScriptableObject
    {
        public const float Height = .04f; // nivel del asfalto

        [SerializeField] private Vector2[] points = Array.Empty<Vector2>();
        [SerializeField] private int[] pointStart = Array.Empty<int>();
        [SerializeField] private int[] nextStart = Array.Empty<int>(), next = Array.Empty<int>();
        [SerializeField] private int[] control = Array.Empty<int>(), signal = Array.Empty<int>(), axis = Array.Empty<int>();
        [SerializeField] private float[] speed = Array.Empty<float>();

        public int LinkCount => control.Length;
        public int PointCount(int link) => pointStart[link + 1] - pointStart[link];
        public Vector3 Point(int link, int index) { var p = points[pointStart[link] + index]; return new Vector3(p.x, Height, p.y); }
        public int NextCount(int link) => nextStart[link + 1] - nextStart[link];
        public int Next(int link, int index) => next[nextStart[link] + index];
        public LinkControl Control(int link) => (LinkControl)control[link];
        public int Signal(int link) => signal[link];
        public int Axis(int link) => axis[link];
        public float Speed(int link) => speed[link];

        // Se llama al preparar la ciudad, con los enlaces de city_traffic.json.
        public void Build(IReadOnlyList<(Vector2[] path, int[] successors, int control, int signal, int axis, float speed)> links)
        {
            var p = new List<Vector2>(); var n = new List<int>();
            pointStart = new int[links.Count + 1]; nextStart = new int[links.Count + 1];
            control = new int[links.Count]; signal = new int[links.Count]; axis = new int[links.Count]; speed = new float[links.Count];
            for (int i = 0; i < links.Count; i++)
            {
                pointStart[i] = p.Count; nextStart[i] = n.Count;
                p.AddRange(links[i].path); n.AddRange(links[i].successors);
                control[i] = links[i].control; signal[i] = links[i].signal; axis[i] = links[i].axis; speed[i] = links[i].speed;
            }
            pointStart[links.Count] = p.Count; nextStart[links.Count] = n.Count;
            points = p.ToArray(); next = n.ToArray();
        }
    }
}
