using System.IO;
using UnityEditor;
using UnityEditor.TestTools.TestRunner.Api;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Alarma.Core.Editor
{
    [InitializeOnLoad]
    public static class ArchitectureTestRunner
    {
        private const string RequestPath = "Library/Alarma/RunTask01Tests.request";
        private const string ResultsPath = "Library/Alarma/Task01Results.xml";

        static ArchitectureTestRunner()
        {
            EditorApplication.delayCall += RunRequestedTests;
        }

        private static void RunRequestedTests()
        {
            if (!File.Exists(RequestPath))
            {
                return;
            }

            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode)
            {
                EditorApplication.delayCall += RunRequestedTests;
                return;
            }

            File.Delete(RequestPath);
            RunTests();
        }

        [MenuItem("Alarma/Validation/Run Architecture Tests")]
        public static void RunTests()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            {
                Debug.LogWarning("Alarma: termina Play Mode o la compilación antes de validar la arquitectura.");
                return;
            }

            Directory.CreateDirectory("Library/Alarma");
            var api = ScriptableObject.CreateInstance<TestRunnerApi>();
            var writer = new ResultWriter();
            api.RegisterCallbacks(writer);
            try
            {
                var filter = new Filter
                {
                    testMode = TestMode.EditMode,
                    assemblyNames = new[] { "Alarma.Core.EditModeTests" }
                };
                api.Execute(new ExecutionSettings(filter) { runSynchronously = true });
            }
            finally
            {
                api.UnregisterCallbacks(writer);
                Object.DestroyImmediate(api);
            }
        }

        private sealed class ResultWriter : ICallbacks
        {
            public void RunStarted(ITestAdaptor testsToRun) { }
            public void TestStarted(ITestAdaptor test) { }
            public void TestFinished(ITestResultAdaptor result) { }

            public void RunFinished(ITestResultAdaptor result)
            {
                TestRunnerApi.SaveResultToFile(result, ResultsPath);
                string message = $"Alarma: {result.PassCount} pruebas correctas, {result.FailCount} fallidas, " +
                    $"{result.SkipCount} omitidas. Resultado: {ResultsPath}";

                if (result.FailCount > 0 || result.PassCount == 0 || result.InconclusiveCount > 0)
                {
                    Debug.LogError(message);
                }
                else
                {
                    Debug.Log(message);
                }
            }
        }
    }
}
