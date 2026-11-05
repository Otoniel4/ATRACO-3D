using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Alarma.AI.CityLife.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace Alarma.City.Editor
{
    internal static class RecoveryTests
    {
        private const string External = "Assets/Party/Scenes/External.unity";
        private const string Empty = "Assets/Party/Scenes/Backups/Scene_0.unity";
        private static string sandbox;
        private static int passed;

        private static void Check(bool value, string reason)
        {
            if (!value) throw new InvalidOperationException(reason);
        }

        private static void Throws<T>(Action action) where T : Exception
        {
            try { action(); }
            catch (T) { return; }
            throw new InvalidOperationException("Se esperaba " + typeof(T).Name);
        }

        private static void Test(string name, Action action)
        {
            Directory.SetCurrentDirectory(Directory.CreateDirectory(Path.Combine(sandbox, (passed + 1).ToString())).FullName);
            AssetDatabase.Reset();
            SceneManager.Reset();
            EditorBuildSettings.scenes = Array.Empty<EditorBuildSettingsScene>();
            EditorSceneManager.FailOpen = false;
            EditorUtility.LastDialog = null;
            action();
            passed++;
            Console.WriteLine("PASS " + name);
        }

        private static void Write(string path, string value)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllText(path, value);
        }

        private static Dictionary<string, byte[]> OldOutput(bool open = true)
        {
            Write(City25Paths.Scene, "Ciudad anterior con cámara");
            Write(City25Paths.Scene + ".meta", "guid de escena");
            Write(City25Paths.Report, "Informe anterior");
            Write(City25Paths.Output + ".meta", "guid de carpeta");
            Write(City25Paths.Output + "/Prefabs/Puerta.prefab", "Prefab anterior");
            Write(City25Paths.Output + "/Prefabs/Puerta.prefab.meta", "guid de puerta");
            if (open) EditorSceneManager.OpenScene(City25Paths.Scene);
            return Directory.GetFiles(City25Paths.Output, "*", SearchOption.AllDirectories)
                .Append(City25Paths.Output + ".meta").ToDictionary(path => path.Replace('\\', '/'), File.ReadAllBytes);
        }

        private static void Same(Dictionary<string, byte[]> expected)
        {
            foreach (var pair in expected)
                Check(File.Exists(pair.Key) && File.ReadAllBytes(pair.Key).SequenceEqual(pair.Value), "Archivo anterior alterado: " + pair.Key);
        }

        private static void NewOutput(City25BuildRecovery attempt, bool meta = true)
        {
            attempt.OpenStage();
            Write(attempt.ScenePath, "Ciudad nueva");
            if (meta) Write(attempt.ScenePath + ".meta", "guid nuevo");
            Write(attempt.Output + "/Prefabs/Porton.prefab", "Prefab nuevo");
        }

        public static int Main(string[] args)
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            sandbox = Directory.CreateDirectory(Path.GetFullPath(args[0])).FullName;
            Test("carpetas registradas por la ruta exacta", () =>
            {
                var attempt = new City25BuildRecovery(null);
                BuildPolicy.PrepareOutput(attempt.Output);
                foreach (string child in new[]{"Art", "Materials", "Data", "Scenes", "Prefabs", "Controllers"})
                    Check(AssetDatabase.IsValidFolder(attempt.Output + "/" + child), "Falta " + child);
            });
            Test("una carpeta con sufijo no satisface el constructor", () =>
            {
                AssetDatabase.ReturnWrongPath = true;
                Throws<IOException>(() => FlatMaterialLibrary.EnsureFolder("Assets/Exacta"));
            });
            Test("dos intentos preparan rutas distintas", () =>
            {
                var a = new City25BuildRecovery(null);
                var b = new City25BuildRecovery(null);
                Check(a.Output != b.Output && City25Paths.IsCityScene(a.ScenePath), "Preparación ambigua");
                Check(!City25Paths.IsCityScene(City25Paths.Revisions + "/R_../Scenes/Ciudad_2km.unity"), "Aceptó ruta extraña");
            });
            Test("una etapa con prefabs no modifica la ciudad anterior", () =>
            {
                var expected = OldOutput();
                var attempt = new City25BuildRecovery(City25Paths.Scene);
                NewOutput(attempt);
                Same(expected);
                Check(SceneManager.sceneCount == 1 && SceneManager.GetActiveScene().path == "", "La etapa incluye otras escenas");
            });
            Test("acepta una etapa que Unity ya dejó activa", () =>
            {
                OldOutput();
                var attempt = new City25BuildRecovery(City25Paths.Scene);
                var stage = attempt.OpenStage();
                Check(stage == SceneManager.GetActiveScene() && stage.isLoaded, "La etapa no quedó activa");
                Check(!SceneManager.SetActiveScene(stage), "El sustituto debe rechazar la activación redundante");
            });
            Test("borrado parcial de la etapa preserva la ciudad y vuelve a abrirla", () =>
            {
                var expected = OldOutput();
                var attempt = new City25BuildRecovery(City25Paths.Scene);
                NewOutput(attempt);
                AssetDatabase.PartialDelete = true;
                BuildPolicy.Handle(attempt, new IOException("Fallo al generar"));
                Same(expected);
                Check(AssetDatabase.Events.Where(e => e.StartsWith("Delete:")).SequenceEqual(new[]{"Delete:" + attempt.Output}), "Se borró fuera de la etapa");
                Check(SceneManager.GetActiveScene().path == City25Paths.Scene && EditorUtility.LastDialog.Contains("Se volvió a abrir"), "No reabrió la ciudad");
            });
            Test("el fallo anterior a la etapa conserva el montaje abierto", () =>
            {
                var expected = OldOutput();
                Write(External, "Escena del usuario");
                var external = EditorSceneManager.OpenScene(External, OpenSceneMode.Additive);
                var attempt = new City25BuildRecovery(City25Paths.Scene);
                AssetDatabase.FailCreate = true;
                Throws<IOException>(() => BuildPolicy.PrepareOutput(attempt.Output));
                attempt.Restore();
                Same(expected);
                Check(SceneManager.GetActiveScene() == external && SceneManager.sceneCount == 2, "Montaje alterado");
            });
            Test("restaura dos escenas del usuario y la activa", () =>
            {
                var expected = OldOutput();
                Write(External, "Escena del usuario");
                EditorSceneManager.OpenScene(External, OpenSceneMode.Additive);
                var attempt = new City25BuildRecovery(City25Paths.Scene);
                NewOutput(attempt);
                attempt.Restore();
                Same(expected);
                Check(SceneManager.GetActiveScene().path == External && SceneManager.sceneCount == 2, "Montaje perdido");
                Check(!Directory.Exists(attempt.Output), "Etapa descartable sobrevivió");
            });
            Test("ante escenas vacías abre la última ciudad publicada", () =>
            {
                OldOutput(false);
                var older = new City25BuildRecovery(null);
                NewOutput(older);
                older.Publish("Publicación anterior");
                Write(Empty, "Escena vacía");
                SceneManager.Add(Empty, true, 0);
                var attempt = new City25BuildRecovery(older.ScenePath);
                NewOutput(attempt);
                attempt.Restore();
                Check(SceneManager.GetActiveScene().path == older.ScenePath, "Abrió una escena vacía o anticuada");
            });
            Test("sin ciudad anterior conserva una etapa que no puede cerrar", () =>
            {
                var attempt = new City25BuildRecovery(null);
                NewOutput(attempt);
                Check(attempt.Restore().Contains(attempt.Output) && Directory.Exists(attempt.Output) && SceneManager.sceneCount == 1, "Etapa eliminada");
            });
            Test("rechaza publicar una escena sin metadatos", () =>
            {
                var expected = OldOutput();
                var attempt = new City25BuildRecovery(null);
                NewOutput(attempt, false);
                Throws<IOException>(() => attempt.Publish("Informe nuevo"));
                Check(!attempt.Published, "Publicación prematura");
                Same(expected);
            });
            Test("informe bloqueado deja intactos el puntero y la ciudad anterior", () =>
            {
                var expected = OldOutput();
                var attempt = new City25BuildRecovery(null);
                NewOutput(attempt);
                using (File.Open(City25Paths.Report, FileMode.Open, FileAccess.Read, FileShare.None))
                    Throws<IOException>(() => attempt.Publish("Informe nuevo"));
                Check(!attempt.Published, "Publicación fallida marcada lista");
                attempt.Restore();
                Same(expected);
            });
            Test("publica la escena nueva y conserva todos los archivos anteriores salvo el puntero", () =>
            {
                var expected = OldOutput();
                var attempt = new City25BuildRecovery(null);
                NewOutput(attempt);
                attempt.Publish("Informe nuevo");
                expected.Remove(City25Paths.Report);
                Same(expected);
                Check(attempt.Published && File.ReadAllText(City25Paths.Report) == "Informe nuevo", "Puntero sin publicar");
                BuildPolicy.Handle(attempt, new IOException("Fallo de interfaz"));
                Check(File.Exists(attempt.ScenePath) && !AssetDatabase.Events.Any(e => e.StartsWith("Delete:")), "Revirtió la publicación");
            });
            Test("la primera publicación funciona sin informe previo", () =>
            {
                var attempt = new City25BuildRecovery(null);
                NewOutput(attempt);
                attempt.Publish("Primer informe");
                Check(attempt.Published && File.ReadAllText(City25Paths.Report) == "Primer informe", "No creó el informe");
            });
            Test("la compilación apunta a la nueva escena y conserva otros ajustes", () =>
            {
                var attempt = new City25BuildRecovery(null);
                EditorBuildSettings.scenes = new[] {new EditorBuildSettingsScene(External, true), new EditorBuildSettingsScene(City25Paths.Scene, false)};
                BuildPolicy.SelectBuildScene(attempt.ScenePath);
                BuildPolicy.SelectBuildScene(attempt.ScenePath);
                var scenes = EditorBuildSettings.scenes;
                Check(scenes.Length == 2 && scenes[0].path == External && scenes[0].enabled
                    && scenes[1].path == attempt.ScenePath && !scenes[1].enabled, "Cambió otra escena o perdió su ajuste");
            });
            Console.WriteLine("PUBLICATION_TESTS_PASSED " + passed);
            return 0;
        }
    }
}
