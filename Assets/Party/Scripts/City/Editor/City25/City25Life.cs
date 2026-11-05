using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;
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

        public static SidewalkPopulation Pedestrians(string folder, CityLife life, TrafficSignalNetwork signals, SidewalkWalker[] walkers,
            Transform observer, ShopActivity[] shops, PedestrianSettings settings)
        {
            var nodes = new Vector2[life.nodes.Length / 2];
            for (int i = 0; i < nodes.Length; i++) nodes[i] = new Vector2(life.nodes[2 * i], life.nodes[2 * i + 1]);
            var links = new List<(int, int, int, int)>(life.edges.Length / 4);
            for (int i = 0; i < life.edges.Length; i += 4) links.Add((life.edges[i], life.edges[i + 1], life.edges[i + 2], life.edges[i + 3]));
            if (links.Any(l => l.Item3 >= signals.Count)) throw new InvalidOperationException("Un paso de cebra apunta a un semáforo que no existe.");
            var walkability = new City25Walkability();
            var heights = new float[nodes.Length];
            var supported = new bool[nodes.Length];
            Physics.SyncTransforms();
            for (int i = 0; i < nodes.Length; i++) supported[i] = walkability.HasSidewalk(nodes[i], out heights[i]);
            var safe = new List<(int, int, int, int)>(links.Count);
            for (int i = 0; i < links.Count; i++)
            {
                if (i % 1500 == 0 && EditorUtility.DisplayCancelableProgressBar("Ciudad 2 km", $"Verificando aceras {i}/{links.Count}", .92f))
                    throw new OperationCanceledException();
                var (a,b,signal,_) = links[i];
                if (a < 0 || b < 0 || a >= nodes.Length || b >= nodes.Length)
                    throw new InvalidOperationException("La red peatonal tiene un índice de nodo inválido.");
                if (supported[a] && supported[b] && walkability.ClearSegment(nodes[a], heights[a], nodes[b], heights[b], signal != SidewalkGraph.Sidewalk))
                    safe.Add(links[i]);
            }
            if (safe.Count == 0) throw new InvalidOperationException("Ningún tramo peatonal coincide con la geometría de las aceras.");
            var graph = ScriptableObject.CreateInstance<SidewalkGraph>();
            graph.Build(nodes, safe, 50f, heights);
            AssetDatabase.CreateAsset(graph, folder + "/Data/SidewalkGraph.asset");
            var population = new GameObject("Peatones").AddComponent<SidewalkPopulation>();
            population.Configure(graph, signals, walkers, observer);
            var approaches = ShopApproaches(shops, graph, walkability);
            population.ConfigureVisits(approaches, settings);
            Debug.Log($"Vida de calle: {approaches.Length}/{shops.Length} comercios conectados a la acera.");
            Debug.Log($"Aceras: {safe.Count} tramos verificados sobre el suelo y sus colliders; {links.Count - safe.Count} descartados.");
            return population;
        }

        private static SidewalkVisit[] ShopApproaches(ShopActivity[] shops, SidewalkGraph graph, City25Walkability walkability)
        {
            var visits = new List<SidewalkVisit>();
            var nearby = new List<int>();
            foreach (var shop in shops)
            {
                SidewalkVisit best = null;
                float nearest = 18f * 18f;
                for (int marker = 0; marker < shop.WalkRoute.Length; marker++)
                {
                    Vector3 point = shop.WalkRoute[marker].position;
                    graph.NodesNear(point, 18f, nearby);
                    foreach (int node in nearby)
                    {
                        if (!graph.CanSpawn(node)) continue;
                        Vector3 start = graph.Position(node);
                        Vector3 difference = start - point;
                        float length = difference.sqrMagnitude;
                        if (length >= nearest || Vector3.Dot(difference, shop.transform.forward) < -.7f
                            || !walkability.ClearApproach(start, point, out Vector3 approach)) continue;
                        best = new SidewalkVisit(shop, node, marker, approach);
                        nearest = length;
                    }
                }
                if (best != null) visits.Add(best);
                else Debug.LogWarning($"No se encontró un acceso peatonal libre para {shop.transform.parent.name}.", shop);
            }
            return visits.ToArray();
        }
    }
}
