#if UNITY_EDITOR || DEVELOPMENT_BUILD
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Unity.Profiling;
using Unity.Profiling.LowLevel.Unsafe;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Alarma.City.Playtest
{
    // Medición de rendimiento para optimizar con datos (CLAUDE.md: medir antes de optimizar). Con F9 mide 15 s y guarda
    // en Logs/Rendimiento_<fecha>.txt: tiempo por cuadro, lo que más cuesta (cada script, física, animación, dibujo),
    // contadores de dibujo y memoria, y cuántos objetos activos hay. Solo existe en el editor y en builds de desarrollo.
    public sealed class PerformanceProbe : MonoBehaviour
    {
        private const float Seconds = 15f, SpikeMs = 33.3f;
        private static readonly string[] Counters =
        {
            "Draw Calls Count", "Batches Count", "SetPass Calls Count", "Triangles Count", "Vertices Count",
            "Shadow Casters Count", "Visible Skinned Meshes Count", "GC Allocated In Frame", "Total Used Memory",
        };
        // Marcadores que solo envuelven a otros o suman esperas de varios hilos: en un tirón siempre son los más altos y
        // tapan la causa real (la medición anterior solo mostró estos), así que no cuentan como causa.
        private static readonly HashSet<string> Containers = new HashSet<string>
        {
            "Idle", "Semaphore.WaitForSignal", "UpdateScene", "Main Thread", "Application.Tick", "Application.UpdateScene",
            "UpdateSceneIfNeeded", "PlayerLoop", "CPU Total Frame Time", "CPU Main Thread Frame Time",
            "CPU Render Thread Frame Time", "GPU Frame Time", "Profiler.Default", "EditorLoop", "GfxTask_ReadValue",
            "Gfx.WaitForGfxCommandsFromMainThread", "Gfx.WaitForPresentOnGfxThread", "Gfx.PresentFrame",
        };
        private static readonly string[] Threads = { "CPU Main Thread Frame Time", "CPU Render Thread Frame Time", "GPU Frame Time" };

        private readonly List<(string name, ProfilerRecorder recorder, bool time)> recorders = new List<(string, ProfilerRecorder, bool)>();
        private readonly Dictionary<string, double> totals = new Dictionary<string, double>();
        private readonly List<float> frames = new List<float>();
        private readonly List<(string name, long value)> spikeFrame = new List<(string, long)>();
        private readonly Dictionary<string, (int count, double ms)> spikes = new Dictionary<string, (int, double)>();
        private readonly double[] spikeThreads = new double[3];
        private int spikeCount;
        private float until = -1f;
        private string notice = "";
        private float noticeUntil;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Install()
        {
            var probe = new GameObject("Medidor de rendimiento (F9)") { hideFlags = HideFlags.DontSave };
            DontDestroyOnLoad(probe);
            probe.AddComponent<PerformanceProbe>();
        }

        private void Update()
        {
            if (until < 0f && Keyboard.current != null && Keyboard.current.f9Key.wasPressedThisFrame) Begin();
            if (until < 0f) return;
            float ms = Time.unscaledDeltaTime * 1000f;
            frames.Add(ms);
            spikeFrame.Clear();
            foreach (var (name, recorder, time) in recorders)
            {
                if (!recorder.Valid) continue;
                long value = recorder.LastValue;
                totals[name] = (totals.TryGetValue(name, out double sum) ? sum : 0d) + value;
                if (!time || ms <= SpikeMs) continue;
                int thread = Array.IndexOf(Threads, name);
                if (thread >= 0) spikeThreads[thread] += value / 1e6;
                if (value > 1_000_000 && !Containers.Contains(name)) spikeFrame.Add((name, value)); // más de 1 ms en un cuadro lento
            }
            if (ms > SpikeMs) spikeCount++;
            // En cada tirón se anotan los marcadores que más costaron en ese cuadro (dicen qué lo causó).
            foreach (var (name, value) in spikeFrame.OrderByDescending(v => v.value).Take(15))
            {
                spikes.TryGetValue(name, out var seen);
                spikes[name] = (seen.count + 1, seen.ms + value / 1e6);
            }
            if (Time.unscaledTime >= until) Finish();
        }

        private void Begin()
        {
            frames.Clear(); totals.Clear(); Stop();
            var handles = new List<ProfilerRecorderHandle>();
            ProfilerRecorderHandle.GetAvailable(handles);
            spikes.Clear();
            Array.Clear(spikeThreads, 0, spikeThreads.Length);
            spikeCount = 0;
            var seen = new HashSet<string>();
            foreach (var handle in handles)
            {
                var description = ProfilerRecorderHandle.GetDescription(handle);
                string name = description.Name;
                bool time = description.UnitType == ProfilerMarkerDataUnit.TimeNanoseconds;
                // Todos los marcadores de tiempo (motor y scripts) y los contadores de dibujo y memoria.
                if ((!time && !Counters.Contains(name)) || !seen.Add(name)) continue;
                // Encendido desde ya: sin StartImmediately el registro no mide nada (la primera medición dio ceros).
                recorders.Add((name, new ProfilerRecorder(handle, 1, ProfilerRecorderOptions.Default | ProfilerRecorderOptions.StartImmediately), time));
            }
            until = Time.unscaledTime + Seconds;
            Show($"Midiendo rendimiento {Seconds:0} s… juega normal", Seconds);
        }

        private void Finish()
        {
            until = -1f;
            int count = Mathf.Max(1, frames.Count);
            var sorted = frames.OrderBy(f => f).ToList();
            var text = new StringBuilder();
            text.AppendLine($"Rendimiento — {DateTime.Now:yyyy-MM-dd HH:mm:ss} — escena {UnityEngine.SceneManagement.SceneManager.GetActiveScene().name} — editor {Application.isEditor}");
            text.AppendLine($"Cuadros {frames.Count}: promedio {frames.Average():F1} ms ({1000f / frames.Average():F0} fps), p95 {sorted[(int)(sorted.Count * .95f)]:F1} ms, máximo {sorted[sorted.Count - 1]:F1} ms, cuadros > 33 ms {frames.Count(f => f > 33.3f)}");
            text.AppendLine();
            text.AppendLine("Lo que más tiempo cuesta (ms por cuadro, promedio; los marcadores se anidan, el padre incluye a sus hijos):");
            foreach (var (name, recorder, time) in recorders.Where(r => r.time).OrderByDescending(r => Total(r.name)).Take(60))
                text.AppendLine($"  {Total(name) / count / 1e6,8:F3}  {name}");
            text.AppendLine();
            text.AppendLine($"Tirones (cuadros de más de {SpikeMs:0} ms): {spikeCount}. En ellos, promedio por hilo: principal {Per(0)} ms, render {Per(1)} ms, GPU {Per(2)} ms.");
            text.AppendLine("Lo que más se disparó en ellos, sin contar marcadores contenedores (veces, ms en total):");
            foreach (var pair in spikes.OrderByDescending(p => p.Value.ms).Take(40))
                text.AppendLine($"  {pair.Value.count,5}  {pair.Value.ms,9:F1} ms  {pair.Key}");
            text.AppendLine();
            text.AppendLine("Scripts (ms por cuadro, promedio):");
            foreach (var (name, recorder, time) in recorders.Where(r => r.time && r.name.Contains("Update()")).OrderByDescending(r => Total(r.name)).Take(25))
                text.AppendLine($"  {Total(name) / count / 1e6,8:F3}  {name}");
            text.AppendLine();
            DrawBreakdown(text);
            text.AppendLine();
            text.AppendLine("Contadores (promedio por cuadro):");
            foreach (var (name, recorder, time) in recorders.Where(r => !r.time && Counters.Contains(r.name)))
                text.AppendLine($"  {Total(name) / count,14:N0}  {name}");
            text.AppendLine();
            text.AppendLine("Objetos activos:");
            Count<Animator>(text, a => a.isActiveAndEnabled);
            Count<SkinnedMeshRenderer>(text, r => r.enabled);
            Count<MeshRenderer>(text, r => r.enabled);
            Count<Collider>(text, c => c.enabled);
            Count<Rigidbody>(text, r => !r.IsSleeping());
            Count<Light>(text, l => l.enabled);
            text.AppendLine($"  {FindObjectsByType<Light>(FindObjectsInactive.Exclude, FindObjectsSortMode.None).Count(l => l.enabled && l.shadows != LightShadows.None),8}  Light con sombras");
            text.AppendLine($"  {FindObjectsByType<MonoBehaviour>(FindObjectsInactive.Exclude, FindObjectsSortMode.None).Length,8}  MonoBehaviour activos");
            foreach (var group in FindObjectsByType<MonoBehaviour>(FindObjectsInactive.Exclude, FindObjectsSortMode.None)
                         .GroupBy(b => b.GetType().Name).OrderByDescending(g => g.Count()).Take(20))
                text.AppendLine($"  {group.Count(),8}  {group.Key}");
            text.AppendLine($"  QualitySettings: nivel {QualitySettings.names[QualitySettings.GetQualityLevel()]}, sombras {QualitySettings.shadows}, distancia de sombras {QualitySettings.shadowDistance}, vSync {QualitySettings.vSyncCount}");
            string folder = Path.Combine(Application.dataPath, "..", "Logs");
            Directory.CreateDirectory(folder);
            string path = Path.GetFullPath(Path.Combine(folder, $"Rendimiento_{DateTime.Now:yyyyMMdd_HHmmss}.txt"));
            File.WriteAllText(path, text.ToString(), Encoding.UTF8);
            Debug.Log("Informe de rendimiento guardado en " + path);
            Show("Informe guardado en Logs/" + Path.GetFileName(path), 6f);
            Stop();
        }

        private double Total(string name) => totals.TryGetValue(name, out double sum) ? sum : 0d;

        private string Per(int thread) => (spikeThreads[thread] / Mathf.Max(1, spikeCount)).ToString("F1");

        // Por qué no se agrupan los dibujos: el agrupador de URP (GPU Resident Drawer) junta en una orden los objetos con
        // la misma malla y material, salvo los que tienen MaterialPropertyBlock, son transparentes o no son MeshRenderer.
        private static void DrawBreakdown(StringBuilder text)
        {
            int visible = 0, block = 0, clear = 0, mirrored = 0, batched = 0;
            var combos = new Dictionary<(Mesh, Material), int>();
            var shaders = new Dictionary<string, int>();
            foreach (var renderer in FindObjectsByType<MeshRenderer>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
            {
                if (!renderer.enabled || !renderer.isVisible) continue;
                visible++;
                if (renderer.HasPropertyBlock()) block++;
                if (renderer.isPartOfStaticBatch) batched++;
                Vector3 s = renderer.transform.lossyScale;
                if (s.x * s.y * s.z < 0f) mirrored++;
                var filter = renderer.GetComponent<MeshFilter>();
                Mesh mesh = filter != null ? filter.sharedMesh : null;
                bool transparent = false;
                foreach (var material in renderer.sharedMaterials)
                {
                    if (material == null) continue;
                    transparent |= material.renderQueue > 2500;
                    combos[(mesh, material)] = (combos.TryGetValue((mesh, material), out int n) ? n : 0) + 1;
                    string shader = material.shader != null ? material.shader.name : "(sin shader)";
                    shaders[shader] = (shaders.TryGetValue(shader, out int k) ? k : 0) + 1;
                }
                if (transparent) clear++;
            }
            text.AppendLine($"Dibujo: {visible} MeshRenderer visibles (alguna cámara o sombra). Con MaterialPropertyBlock {block}, transparentes {clear}, escala invertida {mirrored}, en lote estático {batched}.");
            text.AppendLine($"  Combinaciones malla+material visibles: {combos.Count}; usadas por un solo objeto: {combos.Count(c => c.Value == 1)}.");
            text.AppendLine("  Más repetidas (objetos, malla / material):");
            foreach (var pair in combos.OrderByDescending(c => c.Value).Take(12))
                text.AppendLine($"  {pair.Value,8}  {(pair.Key.Item1 != null ? pair.Key.Item1.name : "(sin malla)")} / {pair.Key.Item2.name}");
            text.AppendLine("  Shaders (submallas visibles):");
            foreach (var pair in shaders.OrderByDescending(p => p.Value).Take(8))
                text.AppendLine($"  {pair.Value,8}  {pair.Key}");
        }

        private static void Count<T>(StringBuilder text, Func<T, bool> active) where T : Component
            => text.AppendLine($"  {FindObjectsByType<T>(FindObjectsInactive.Exclude, FindObjectsSortMode.None).Count(active),8}  {typeof(T).Name}");

        private void Stop()
        {
            foreach (var (_, recorder, _) in recorders) recorder.Dispose();
            recorders.Clear();
        }

        private void Show(string message, float seconds) { notice = message; noticeUntil = Time.unscaledTime + seconds; }

        private void OnGUI()
        {
            if (Time.unscaledTime > noticeUntil) return;
            GUI.Label(new Rect(12, 12, 700, 24), notice);
        }

        private void OnDestroy() => Stop();
    }
}
#endif
