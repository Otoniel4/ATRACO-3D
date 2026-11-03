using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Alarma.Core.Editor
{
    [InitializeOnLoad]
    public static class BlenderImportValidator
    {
        private const string Request = "Library/Alarma/ValidateBlenderImports.request";
        private const string Result = "Library/Alarma/BlenderImportResults.json";

        static BlenderImportValidator()
        {
            EditorApplication.delayCall += RunRequested;
            EditorApplication.projectChanged += RunRequested;
        }

        private static void RunRequested()
        {
            if (!File.Exists(Request)) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                EditorApplication.delayCall += RunRequested;
                return;
            }
            File.Delete(Request);
            Validate();
        }

        [MenuItem("Alarma/Validation/Validate Blender Imports")]
        public static void Validate()
        {
            var report = new ImportReport();
            foreach (string path in Directory.GetFiles("Assets/Party/Art", "*.fbx", SearchOption.AllDirectories))
            {
                string normalized = path.Replace('\\', '/');
                GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(normalized);
                var entry = new ImportEntry { path = normalized };
                if (model != null)
                {
                    MeshFilter[] meshes = model.GetComponentsInChildren<MeshFilter>(true);
                    Bounds bounds = new Bounds();
                    bool first = true;
                    foreach (MeshFilter mesh in meshes)
                    {
                        if (mesh.sharedMesh == null) continue;
                        entry.meshes++;
                        entry.vertices += mesh.sharedMesh.vertexCount;
                        Bounds local = mesh.sharedMesh.bounds;
                        for (int corner = 0; corner < 8; corner++)
                        {
                            Vector3 point = local.center + Vector3.Scale(local.extents,
                                new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1));
                            point = model.transform.InverseTransformPoint(mesh.transform.TransformPoint(point));
                            if (first) { bounds = new Bounds(point, Vector3.zero); first = false; }
                            else bounds.Encapsulate(point);
                        }
                    }
                    entry.sizeMeters = bounds.size;
                    entry.valid = entry.meshes > 0;
                    if (normalized.EndsWith("ConnectionCube_1m.fbx", StringComparison.Ordinal))
                    {
                        entry.valid &= Vector3.Distance(bounds.size, Vector3.one) < 0.02f;
                    }
                }
                report.models.Add(entry);
                if (!entry.valid) report.failed++;
            }
            Directory.CreateDirectory("Library/Alarma");
            File.WriteAllText(Result, JsonUtility.ToJson(report, true));
            string message = $"Alarma: {report.models.Count} FBX revisados, {report.failed} fallidos. {Result}";
            if (report.failed > 0 || report.models.Count == 0) Debug.LogError(message);
            else Debug.Log(message);
        }

        [Serializable]
        private sealed class ImportReport
        {
            public int failed;
            public List<ImportEntry> models = new List<ImportEntry>();
        }

        [Serializable]
        private sealed class ImportEntry
        {
            public string path;
            public bool valid;
            public int meshes;
            public int vertices;
            public Vector3 sizeMeters;
        }
    }
}
