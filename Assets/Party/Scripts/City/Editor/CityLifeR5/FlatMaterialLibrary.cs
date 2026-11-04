using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace Alarma.AI.CityLife.Editor
{
    // Materiales de color plano creados desde manifiestos de color; los modelos importados se reasignan por nombre de material.
    public static class FlatMaterialLibrary
    {
        private const string WindShader = "Assets/Party/Art/Materials/Shaders/TreeWindURP.shader";
        private const string Palettes = "Assets/Party/Art/Materials";

        // Crea o actualiza en folder/Materials los materiales de los manifiestos; con only se limita a esos nombres.
        public static Dictionary<string, Material> Create(string folder, IEnumerable<string> manifests, ICollection<string> only = null)
        {
            // Sin distinguir mayúsculas: en Windows «_Minimarket» y «_minimarket» son el mismo archivo de material.
            var entries = new Dictionary<string, ColorEntry>(StringComparer.OrdinalIgnoreCase);
            foreach (string path in manifests)
                foreach (var entry in JsonUtility.FromJson<ColorManifest>(File.ReadAllText(path)).materials) entries[entry.name] = entry;
            foreach (string path in Directory.GetFiles(Palettes, "*Palette.json"))
            {
                var palette = JsonUtility.FromJson<OriginalPalette>(File.ReadAllText(path)); if (palette?.colors == null) continue;
                foreach (var entry in palette.colors)
                {
                    if (!ColorUtility.TryParseHtmlString("#" + entry.hex, out Color c)) continue;
                    string name = "Alarma_" + entry.name; entries[name] = new ColorEntry { name = name, r = c.r, g = c.g, b = c.b, a = 1, roughness = .88f };
                }
            }
            Shader lit = Shader.Find("Universal Render Pipeline/Lit"); if (lit == null) throw new InvalidOperationException("No se encontró URP/Lit.");
            EnsureFolder(folder + "/Materials");
            // Árboles y plantas se mueven con el viento; un solo shader compartido por todos los materiales.
            Shader wind = AssetDatabase.LoadAssetAtPath<Shader>(WindShader) ?? throw new FileNotFoundException("Falta el shader de viento", WindShader);
            var materials = new Dictionary<string, Material>(StringComparer.OrdinalIgnoreCase);
            foreach (var e in entries.Values)
            {
                if (only != null && !only.Contains(e.name)) continue;
                bool plant = e.name.StartsWith("WindTree_", StringComparison.Ordinal) || e.name.StartsWith("WindPlant_", StringComparison.Ordinal);
                string safe = string.Concat(e.name.Select(c => Path.GetInvalidFileNameChars().Contains(c) ? '_' : c));
                string path = folder + "/Materials/" + safe + ".mat";
                // Se actualiza el material existente para conservar su GUID entre preparaciones.
                var m = AssetDatabase.LoadAssetAtPath<Material>(path); bool created = m == null;
                if (created) m = new Material(plant ? wind : lit) { name = e.name }; else m.shader = plant ? wind : lit;
                m.enableInstancing = true; m.SetColor("_BaseColor", new Color(e.r, e.g, e.b, e.a));
                if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", e.metallic); if (m.HasProperty("_Smoothness")) m.SetFloat("_Smoothness", 1 - e.roughness);
                // Luces de autos y carteles: brillan solas y el juego puede cambiar su intensidad.
                if (e.emission > 0f) { m.EnableKeyword("_EMISSION"); m.SetColor("_EmissionColor", new Color(e.r, e.g, e.b) * e.emission); m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None; }
                else m.DisableKeyword("_EMISSION");
                if (e.a < .99f && !plant)
                {
                    m.SetFloat("_Surface", 1); m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha); m.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha); m.SetFloat("_ZWrite", 0); m.SetFloat("_Cull", 0);
                    m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); m.SetOverrideTag("RenderType", "Transparent"); m.SetShaderPassEnabled("ShadowCaster", false); m.renderQueue = (int)RenderQueue.Transparent;
                    // Sin brillos ni reflejo del cielo: mirado desde arriba el vidrio se veía blanco y tapaba el interior.
                    m.SetFloat("_Smoothness", 0f); m.SetFloat("_SpecularHighlights", 0f); m.SetFloat("_EnvironmentReflections", 0f);
                    m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF"); m.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
                }
                if (created) AssetDatabase.CreateAsset(m, path); else EditorUtility.SetDirty(m);
                materials[e.name] = m;
            }
            AssetDatabase.SaveAssets();
            return materials;
        }

        // Nombres de material que traen los modelos, para crear solo los necesarios.
        public static HashSet<string> UsedNames(IEnumerable<string> models)
        {
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string path in models)
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path.Replace('\\', '/')) ?? throw new InvalidOperationException("Modelo no disponible: " + path);
                foreach (var m in model.GetComponentsInChildren<Renderer>(true).SelectMany(r => r.sharedMaterials).Where(m => m != null)) names.Add(m.name);
            }
            return names;
        }

        public static void Remap(IReadOnlyList<string> models, IReadOnlyDictionary<string, Material> materials, string title)
        {
            for (int i = 0; i < models.Count; i++)
            {
                if (EditorUtility.DisplayCancelableProgressBar(title, "Materiales: " + Path.GetFileName(models[i]), .2f + .25f * i / models.Count)) throw new OperationCanceledException();
                string path = models[i].Replace('\\', '/'); var importer = (ModelImporter)AssetImporter.GetAtPath(path); var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (model == null || importer == null) throw new InvalidOperationException("Modelo no disponible: " + path);
                // Solo se reimporta si falta alguna reasignación: las preparaciones repetidas son rápidas.
                var current = importer.GetExternalObjectMap(); bool changed = false;
                foreach (var original in model.GetComponentsInChildren<Renderer>(true).SelectMany(r => r.sharedMaterials).Where(m => m != null).Distinct())
                {
                    if (!materials.TryGetValue(original.name, out var target)) continue;
                    var id = new AssetImporter.SourceAssetIdentifier(typeof(Material), original.name);
                    if (current.TryGetValue(id, out var mapped) && mapped == target) continue;
                    importer.AddRemap(id, target); changed = true;
                }
                if (changed) importer.SaveAndReimport();
            }
        }

        public static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            Directory.CreateDirectory(path); AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        [Serializable] private sealed class OriginalPalette { public OriginalColor[] colors = Array.Empty<OriginalColor>(); }
        [Serializable] private sealed class OriginalColor { public string name, hex; }
    }
}
