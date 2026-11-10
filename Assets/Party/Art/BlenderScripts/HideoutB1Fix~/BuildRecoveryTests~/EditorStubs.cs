// Sustitutos de AssetDatabase/escenas para probar políticas; no ejecutan Unity ni su importador nativo.
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

namespace UnityEngine
{
    public class Camera { }
    public class GameObject
    {
        public T GetComponentInChildren<T>() where T : class => new Camera() as T;
    }
    public static class Debug
    {
        public static void Log(object value) { }
        public static void LogWarning(object value) { }
        public static void LogError(object value) { }
        public static void LogException(Exception value) { }
    }
}
namespace UnityEngine.SceneManagement
{
    public struct Scene : IEquatable<Scene>
    {
        public int handle;
        public bool IsValid() => SceneManager.Records.ContainsKey(handle);
        public bool isLoaded => IsValid() && SceneManager.Records[handle].loaded;
        public int rootCount => IsValid() ? SceneManager.Records[handle].roots : 0;
        public UnityEngine.GameObject[] GetRootGameObjects() => rootCount > 0
            ? new[] { new UnityEngine.GameObject() } : Array.Empty<UnityEngine.GameObject>();
        public string path => IsValid() ? SceneManager.Records[handle].path : "";
        public string name => string.IsNullOrEmpty(path) ? "Untitled" : Path.GetFileNameWithoutExtension(path);
        public bool isDirty => false;
        public bool Equals(Scene other) => handle == other.handle;
        public override bool Equals(object other) => other is Scene scene && Equals(scene);
        public override int GetHashCode() => handle;
        public static bool operator ==(Scene a, Scene b) => a.Equals(b);
        public static bool operator !=(Scene a, Scene b) => !a.Equals(b);
    }
    public static class SceneManager
    {
        public sealed class Record { public string path; public bool loaded = true; public int roots; }
        public static readonly Dictionary<int, Record> Records = new Dictionary<int, Record>();
        public static readonly List<int> Loaded = new List<int>();
        public static readonly List<string> Events = new List<string>();
        private static int next = 1, active;
        public static int sceneCount => Loaded.Count;
        public static Scene GetSceneAt(int index) => new Scene { handle = Loaded[index] };
        public static Scene GetActiveScene() => new Scene { handle = active };
        public static Scene GetSceneByPath(string path) => Loaded.Select(h => new Scene { handle = h }).FirstOrDefault(s => s.path == path);
        public static bool SetActiveScene(Scene scene)
        {
            if (!scene.isLoaded || scene == GetActiveScene()) return false;
            active = scene.handle; Events.Add("Active:" + scene.path); return true;
        }
        public static Scene Add(string path, bool single, int roots = 1)
        {
            if (single)
            {
                foreach (int h in Loaded) Records[h].loaded = false;
                Loaded.Clear();
            }
            int id = next++;
            Records[id] = new Record { path = path, roots = roots };
            Loaded.Add(id); active = id;
            Events.Add("Open:" + path);
            return new Scene { handle = id };
        }
        public static void Close(Scene scene)
        {
            if (sceneCount <= 1) throw new InvalidOperationException("Se intentó cerrar la última escena");
            Records[scene.handle].loaded = false; Loaded.Remove(scene.handle);
            if (active == scene.handle) active = Loaded[0];
            Events.Add("Close:" + scene.path);
        }
        public static void Reset()
        {
            Records.Clear(); Loaded.Clear(); Events.Clear(); active = 0;
        }
    }
}

namespace UnityEditor
{
    public sealed class EditorBuildSettingsScene
    {
        public string path;
        public bool enabled;
        public EditorBuildSettingsScene(string path, bool enabled) { this.path = path; this.enabled = enabled; }
    }
    public static class EditorBuildSettings
    {
        public static EditorBuildSettingsScene[] scenes = Array.Empty<EditorBuildSettingsScene>();
    }
    public static class EditorUtility
    {
        public static string LastDialog;
        public static bool DisplayDialog(string title, string message, string accept) { LastDialog = message; return true; }
    }
    [Flags]
    public enum ImportAssetOptions { Default = 0, ForceUpdate = 1, ForceSynchronousImport = 8, ImportRecursive = 256 }
    public static class AssetDatabase
    {
        public static readonly HashSet<string> Registered = new HashSet<string>(StringComparer.Ordinal);
        public static readonly Dictionary<string, string> Guids = new Dictionary<string, string>();
        public static readonly List<string> Events = new List<string>();
        public static bool FailCreate, FailImport, ReturnWrongPath, PartialDelete;
        public static void Reset()
        {
            Registered.Clear(); Guids.Clear(); Events.Clear();
            FailCreate = FailImport = ReturnWrongPath = PartialDelete = false;
            Directory.CreateDirectory("Assets"); Registered.Add("Assets");
        }
        public static bool IsValidFolder(string path) => Registered.Contains(path) && Directory.Exists(path);
        public static string CreateFolder(string parent, string name)
        {
            Events.Add("Create:" + parent + "/" + name);
            if (!IsValidFolder(parent)) throw new InvalidOperationException("Padre no registrado: " + parent);
            if (FailCreate) return "";
            string path = parent + "/" + name;
            if (Directory.Exists(path) || ReturnWrongPath) path += " 1";
            Directory.CreateDirectory(path); Registered.Add(path);
            string guid = Guid.NewGuid().ToString("N"); Guids[guid] = path;
            return guid;
        }
        public static string GUIDToAssetPath(string guid) => Guids.TryGetValue(guid, out var path) ? path : "";
        public static void ImportAsset(string path, ImportAssetOptions options = ImportAssetOptions.Default)
        {
            Events.Add("Import:" + path);
            if (path.EndsWith(".unity") && UnityEngine.SceneManagement.SceneManager.GetActiveScene().path == path)
                throw new IOException("Importación de la escena abierta");
            if (FailImport) return;
            if (Directory.Exists(path))
            {
                Registered.Add(path);
                if ((options & ImportAssetOptions.ImportRecursive) != 0)
                    foreach (string child in Directory.GetDirectories(path, "*", SearchOption.AllDirectories)) Registered.Add(child.Replace('\\', '/'));
            }
        }
        public static void Refresh(ImportAssetOptions options = ImportAssetOptions.Default)
        {
            Events.Add("Refresh");
            if (FailImport) return;
            if ((options & ImportAssetOptions.ForceSynchronousImport) != 0)
                foreach (string child in Directory.GetDirectories("Assets", "*", SearchOption.AllDirectories)) Registered.Add(child.Replace('\\', '/'));
        }
        public static bool DeleteAsset(string path)
        {
            Events.Add("Delete:" + path);
            if (PartialDelete)
            {
                string first = Directory.GetFiles(path, "*", SearchOption.AllDirectories).FirstOrDefault();
                if (first != null) File.Delete(first);
                return false;
            }
            if (Directory.Exists(path)) Directory.Delete(path, true);
            else if (File.Exists(path)) File.Delete(path);
            else return false;
            if (File.Exists(path + ".meta")) File.Delete(path + ".meta");
            Registered.RemoveWhere(p => p == path || p.StartsWith(path + "/", StringComparison.Ordinal));
            return true;
        }
        public static void SaveAssets() { }
    }
}

namespace UnityEditor.SceneManagement
{
    using UnityEngine.SceneManagement;
    public enum OpenSceneMode { Single, Additive, AdditiveWithoutLoading }
    public enum NewSceneMode { Single, Additive }
    public enum NewSceneSetup { EmptyScene, DefaultGameObjects }
    public sealed class SceneSetup { public string path; public bool isLoaded, isActive; }
    public static class EditorSceneManager
    {
        public static bool FailOpen;
        public static bool SaveScene(Scene scene, string path, bool saveAsCopy = false)
        {
            if (!scene.isLoaded) return false;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllText(path, "Escena guardada");
            File.WriteAllText(path + ".meta", "guid");
            if (!saveAsCopy) SceneManager.Records[scene.handle].path = path;
            return true;
        }
        public static Scene NewScene(NewSceneSetup setup, NewSceneMode mode) => SceneManager.Add("", mode == NewSceneMode.Single, 0);
        public static Scene OpenScene(string path, OpenSceneMode mode = OpenSceneMode.Single)
        {
            if (FailOpen || !File.Exists(path)) throw new IOException("No se pudo abrir: " + path);
            return SceneManager.Add(path, mode == OpenSceneMode.Single);
        }
        public static bool CloseScene(Scene scene, bool removeScene) { SceneManager.Close(scene); return true; }
        public static SceneSetup[] GetSceneManagerSetup() => Enumerable.Range(0, SceneManager.sceneCount).Select(i => SceneManager.GetSceneAt(i)).Select(s => new SceneSetup { path = s.path, isLoaded = true, isActive = s == SceneManager.GetActiveScene() }).ToArray();
        public static void RestoreSceneManagerSetup(SceneSetup[] setup)
        {
            if (!setup.Any(s => s.isLoaded) || !setup.Any(s => s.isActive)) throw new InvalidOperationException("Setup sin escena cargada/activa");
            SceneManager.Events.Add("RestoreSetup");
            bool first = true;
            Scene active = default;
            foreach (var entry in setup.Where(s => s.isLoaded))
            {
                var scene = OpenScene(entry.path, first ? OpenSceneMode.Single : OpenSceneMode.Additive);
                if (entry.isActive) active = scene;
                first = false;
            }
            SceneManager.SetActiveScene(active);
        }
    }
}
