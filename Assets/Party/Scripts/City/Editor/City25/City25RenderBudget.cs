using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace Alarma.City.Editor
{
    // Ajustes de dibujo que no cambian la imagen, elegidos con PerformanceProbe (TASKS.md, Optimización): la escena no
    // tiene sondas de luz horneadas, pero cada uno de los ~18.000 objetos calculaba sus sondas en cada cuadro (5,3 ms)
    // para terminar usando la luz ambiente. Con LightProbeUsage.Off Unity entrega al shader esa misma luz ambiente
    // (documentación de LightProbeUsage.Off), así que se ve igual y se ahorra el cálculo. Si algún día se hornean
    // sondas, este paso no hace nada y los objetos las siguen usando.
    internal static class City25RenderBudget
    {
        public static int Apply(Scene scene, string output)
        {
            if (LightmapSettings.lightProbes != null && LightmapSettings.lightProbes.count > 0)
            {
                Debug.Log("La escena tiene sondas de luz horneadas: los objetos las siguen usando.");
                return 0;
            }
            int changed = 0;
            foreach (var root in scene.GetRootGameObjects()) changed += ProbesOff(root);
            // Prefabs que aparecen durante el juego: peatones, clientes, autos y dobles de reacción.
            foreach (string guid in AssetDatabase.FindAssets("t:Prefab", new[] { output + "/Prefabs" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var contents = PrefabUtility.LoadPrefabContents(path);
                try
                {
                    int count = ProbesOff(contents);
                    if (count > 0) { PrefabUtility.SaveAsPrefabAsset(contents, path); changed += count; }
                }
                finally { PrefabUtility.UnloadPrefabContents(contents); }
            }
            Debug.Log($"Dibujo: {changed} objetos dejan de calcular sondas de luz (la escena no tiene sondas horneadas).");
            return changed;
        }

        private static int ProbesOff(GameObject root)
        {
            int count = 0;
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                if (renderer.lightProbeUsage == LightProbeUsage.Off) continue;
                renderer.lightProbeUsage = LightProbeUsage.Off;
                count++;
            }
            return count;
        }
    }
}
