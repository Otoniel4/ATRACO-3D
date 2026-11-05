using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Alarma.City.Editor
{
    // Genera en una ruta propia. El informe cambia solo después de guardar la escena nueva.
    internal sealed class City25BuildRecovery
    {
        private const string RecoveryRoot = "Library/Alarma/City25Recovery";
        private readonly string revision = Guid.NewGuid().ToString("N");
        private readonly SceneSetup[] previousScenes;
        private readonly string fallbackScene;
        private readonly bool previousHasContent;
        private bool stageStarted;
        public string Output => City25Paths.Revisions + "/R_" + revision;
        public string ScenePath => Output + City25Paths.SceneSuffix;
        public bool Published { get; private set; }

        public City25BuildRecovery(string lastCity)
        {
            previousScenes = EditorSceneManager.GetSceneManagerSetup();
            previousHasContent = Enumerable.Range(0, SceneManager.sceneCount).Select(SceneManager.GetSceneAt)
                .Any(scene => scene.isLoaded && scene.rootCount > 0);
            fallbackScene = City25Paths.IsCityScene(lastCity) && File.Exists(lastCity) ? lastCity : City25Paths.Scene;
        }

        public Scene OpenStage()
        {
            stageStarted = true;
            // Las colisiones de la ciudad anterior no deben participar en la validación.
            var stage = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            if (!stage.IsValid() || !stage.isLoaded
                || SceneManager.GetActiveScene() != stage && !SceneManager.SetActiveScene(stage))
                throw new IOException("No se pudo activar la escena de preparación.");
            return stage;
        }

        public void Publish(string report)
        {
            if (!stageStarted || !File.Exists(ScenePath) || !File.Exists(ScenePath + ".meta"))
                throw new IOException("La escena nueva debe estar guardada e importada antes de publicar.");
            Directory.CreateDirectory(RecoveryRoot);
            string temporary = Path.Combine(RecoveryRoot, revision + ".json.tmp");
            using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream))
                writer.Write(report);
            if (File.Exists(City25Paths.Report)) File.Replace(temporary, City25Paths.Report, null);
            else File.Move(temporary, City25Paths.Report);
            Published = true;
        }

        public string Restore()
        {
            if (Published) return "La ciudad nueva ya quedó guardada.";
            string result = "La ciudad guardada se conserva en " + fallbackScene + ".";
            if (stageStarted || !previousHasContent && File.Exists(fallbackScene))
            {
                bool validSetup = previousScenes.Any(s => s.isLoaded && s.isActive)
                    && previousScenes.All(s => !string.IsNullOrEmpty(s.path) && File.Exists(s.path));
                if (validSetup && (previousHasContent || !File.Exists(fallbackScene)))
                    EditorSceneManager.RestoreSceneManagerSetup(previousScenes);
                else if (File.Exists(fallbackScene))
                    EditorSceneManager.OpenScene(fallbackScene, OpenSceneMode.Single);
                else
                    return "La preparación incompleta se conserva en " + Output + ".";
                result = "Se volvió a abrir la escena anterior.";
            }

            // El editor puede bloquear la limpieza. Solo se intenta retirar esta revisión fallida.
            string full = Path.GetFullPath(Output);
            if (!string.Equals(Path.GetDirectoryName(full), Path.GetFullPath(City25Paths.Revisions), StringComparison.OrdinalIgnoreCase)
                || Path.GetFileName(full) != "R_" + revision)
                throw new IOException("Ruta de preparación inesperada: " + Output);
            if (Directory.Exists(full) && ((File.GetAttributes(full) & FileAttributes.ReparsePoint) != 0
                || !AssetDatabase.DeleteAsset(Output)))
                Debug.LogWarning("La ciudad anterior está disponible. La preparación incompleta quedó en " + Output + ".");
            return result;
        }
    }
}
