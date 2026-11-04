using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.Street;
using Alarma.Traffic;

namespace Alarma.City.Editor
{
    // Ciudad viva: reloj de semáforos con sus luces y peatones que pasean por la red de aceras.
    internal static class City25Life
    {
        private const string Timing = "Assets/Party/Data/TrafficSignalTiming.asset";

        public static TrafficSignalNetwork Signals(CityLife life, IReadOnlyList<(CityObject data, GameObject instance)> placed)
        {
            // Los tiempos viven en Party/Data para ajustarlos sin regenerar la ciudad.
            var timing = AssetDatabase.LoadAssetAtPath<TrafficSignalTiming>(Timing);
            if (timing == null) { timing = ScriptableObject.CreateInstance<TrafficSignalTiming>(); AssetDatabase.CreateAsset(timing, Timing); }
            int[] axes = life.signals.Select(s => s.axes.Length / 2).ToArray();
            if (axes.Any(a => a < 1)) throw new InvalidOperationException("Hay un semáforo sin ejes en city_life.json.");
            // Cruces desfasados para que no cambien todos a la vez.
            float[] offsets = axes.Select((a, i) => Mathf.Repeat(i * 7.3f, timing.Slot * a)).ToArray();
            var heads = new List<TrafficLightHead>();
            foreach (var (data, instance) in placed)
            {
                var head = instance.GetComponent<TrafficLightHead>() ?? throw new InvalidOperationException("El semáforo no tiene luces: " + instance.name);
                if (data.signal >= axes.Length || data.axis >= axes[data.signal]) throw new InvalidOperationException("Semáforo con cruce o eje fuera de rango: " + instance.name);
                head.Assign(data.signal, data.axis);
                PrefabUtility.RecordPrefabInstancePropertyModifications(head);
                heads.Add(head);
            }
            var network = new GameObject("Semáforos").AddComponent<TrafficSignalNetwork>();
            network.Configure(timing, axes, offsets, heads.ToArray());
            return network;
        }

        public static SidewalkPopulation Pedestrians(string folder, CityLife life, TrafficSignalNetwork signals, SidewalkWalker[] walkers, Transform observer)
        {
            var nodes = new Vector2[life.nodes.Length / 2];
            for (int i = 0; i < nodes.Length; i++) nodes[i] = new Vector2(life.nodes[2 * i], life.nodes[2 * i + 1]);
            var links = new List<(int, int, int, int)>(life.edges.Length / 4);
            for (int i = 0; i < life.edges.Length; i += 4) links.Add((life.edges[i], life.edges[i + 1], life.edges[i + 2], life.edges[i + 3]));
            if (links.Any(l => l.Item3 >= signals.Count)) throw new InvalidOperationException("Un paso de cebra apunta a un semáforo que no existe.");
            var graph = ScriptableObject.CreateInstance<SidewalkGraph>();
            graph.Build(nodes, links, 50f);
            AssetDatabase.CreateAsset(graph, folder + "/Data/SidewalkGraph.asset");
            var population = new GameObject("Peatones").AddComponent<SidewalkPopulation>();
            population.Configure(graph, signals, walkers, observer);
            return population;
        }
    }
}
