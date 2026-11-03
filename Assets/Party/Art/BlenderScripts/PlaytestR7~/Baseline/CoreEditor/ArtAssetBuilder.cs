using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Alarma.Core.Editor
{
    [InitializeOnLoad]
    public static class ArtAssetBuilder
    {
        private const string Root = "Assets/Party/Art";
        private const string RequestPath = "Library/Alarma/BuildArtPrefabs.request";
        private static bool isRunning;

        static ArtAssetBuilder()
        {
            EditorApplication.delayCall += RunRequested;
            EditorApplication.projectChanged += RunRequested;
        }

        private static void RunRequested()
        {
            if (isRunning || !File.Exists(RequestPath)) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                EditorApplication.delayCall += RunRequested;
                return;
            }
            File.Delete(RequestPath);
            Build();
        }

        [MenuItem("Alarma/Art/Apply Palette and Build Art Prefabs")]
        public static void Build()
        {
            if (isRunning || EditorApplication.isPlayingOrWillChangePlaymode) return;
            isRunning = true;
            var summary = new BuildSummary();
            var previewScene = EditorSceneManager.NewPreviewScene();
            try
            {
                Shader shader = Shader.Find("Universal Render Pipeline/Lit");
                if (shader == null) throw new InvalidOperationException("No se encontró el shader URP/Lit instalado.");
                var palette = new Palette { colors = Array.Empty<ColorEntry>() };
                var colors = new List<ColorEntry>();
                foreach (string palettePath in Directory.GetFiles(Root + "/Materials", "*Palette.json"))
                {
                    Palette loaded = JsonUtility.FromJson<Palette>(File.ReadAllText(palettePath));
                    if (loaded?.colors != null) colors.AddRange(loaded.colors);
                }
                palette.colors = colors.ToArray();
                var materials = new Dictionary<string, Material>();
                foreach (ColorEntry entry in palette.colors)
                {
                    string path = Root + "/Materials/Alarma_" + entry.name + ".mat";
                    Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (material == null)
                    {
                        if (!ColorUtility.TryParseHtmlString("#" + entry.hex, out Color color))
                            throw new InvalidOperationException("Color no válido: " + entry.name);
                        material = new Material(shader) { name = "Alarma_" + entry.name };
                        material.SetColor("_BaseColor", color);
                        material.SetFloat("_Smoothness", 0.12f);
                        AssetDatabase.CreateAsset(material, path);
                    }
                    materials[material.name] = material;
                }
                summary.materials = materials.Count;
                string[] files = Directory.GetFiles(Root, "*.fbx", SearchOption.AllDirectories);
                Array.Sort(files, StringComparer.Ordinal);
                foreach (string file in files)
                {
                    string path = file.Replace('\\', '/');
                    if (path.Contains("/Validation/") || path.Contains("/Characters/ReferenceV2/")) continue;
                    GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                    var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                    if (model == null || importer == null)
                    {
                        summary.failed.Add(path + ": modelo no disponible");
                        continue;
                    }
                    var processed = new HashSet<string>();
                    bool changed = false;
                    var remaps = importer.GetExternalObjectMap();
                    foreach (Renderer renderer in model.GetComponentsInChildren<Renderer>(true))
                    {
                        foreach (Material source in renderer.sharedMaterials)
                        {
                            if (source == null || !processed.Add(source.name)) continue;
                            if (!materials.TryGetValue(source.name, out Material target))
                            {
                                summary.unmapped.Add(path + ": " + source.name);
                                continue;
                            }
                            var identifier = new AssetImporter.SourceAssetIdentifier(typeof(Material), source.name);
                            if (!remaps.TryGetValue(identifier, out Object previous) || previous != target)
                            {
                                importer.AddRemap(identifier, target);
                                changed = true;
                            }
                            summary.materialAssignments++;
                        }
                    }
                    if (changed)
                    {
                        importer.SaveAndReimport();
                        model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                    }
                    string relative = path.Substring(Root.Length + 1);
                    string destination = "Assets/Party/Prefabs/Art/" + Path.ChangeExtension(relative, ".prefab").Replace('\\', '/');
                    EnsureFolder(Path.GetDirectoryName(destination).Replace('\\', '/'));
                    GameObject instance = PrefabUtility.InstantiatePrefab(model, previewScene) as GameObject;
                    try
                    {
                        if (instance == null || PrefabUtility.SaveAsPrefabAsset(instance, destination) == null)
                            summary.failed.Add(destination + ": no se pudo guardar el prefab");
                        else summary.prefabs++;
                    }
                    finally
                    {
                        if (instance != null) Object.DestroyImmediate(instance);
                    }
                }
                AssetDatabase.SaveAssets();
            }
            catch (Exception exception)
            {
                summary.failed.Add(exception.Message);
                Debug.LogException(exception);
            }
            finally
            {
                EditorSceneManager.ClosePreviewScene(previewScene);
                Directory.CreateDirectory("Library/Alarma");
                File.WriteAllText("Library/Alarma/ArtBuildResults.json", JsonUtility.ToJson(summary, true));
                isRunning = false;
            }
            BlenderImportValidator.Validate();
            string message = $"Alarma: {summary.prefabs} prefabs de arte, {summary.materials} materiales, " +
                $"{summary.failed.Count} fallos y {summary.unmapped.Count} materiales sin asignar.";
            if (summary.failed.Count > 0) Debug.LogError(message);
            else Debug.Log(message);
        }

        private static void EnsureFolder(string folder)
        {
            if (AssetDatabase.IsValidFolder(folder)) return;
            string parent = Path.GetDirectoryName(folder).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(folder));
        }

        [Serializable] private sealed class Palette { public ColorEntry[] colors; }
        [Serializable] private sealed class ColorEntry { public string name; public string hex; }
        [Serializable] private sealed class BuildSummary
        {
            public int materials;
            public int prefabs;
            public int materialAssignments;
            public List<string> failed = new List<string>();
            public List<string> unmapped = new List<string>();
        }
    }
}
