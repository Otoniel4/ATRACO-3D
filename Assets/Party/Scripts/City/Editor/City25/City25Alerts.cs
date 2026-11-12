using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Editor;
using Alarma.Heist.Alert;

namespace Alarma.City.Editor
{
    // Alerta de cada local vigilado (Task 15): le pone un ShopAlert a los locales que tienen algo que acumula sospecha
    // (las cámaras), con el radio que sale del tamaño del local.
    internal static class City25Alerts
    {
        private const string SettingsPath = "Assets/Party/Data/Heist/Alerta.asset";

        public static int Place(City25World.Result world)
        {
            var settings = LoadOrCreateSettings();
            int placed = 0;
            foreach (var (data, instance) in world.Places)
            {
                if (data.size.Length < 2 || instance.GetComponentInChildren<ISuspicionSource>(true) == null) continue;
                float radius = new Vector2(data.size[0], data.size[1]).magnitude / 2f;
                instance.AddComponent<ShopAlert>().Configure(settings, EventAssets.CrimeReports(), EventAssets.PoliceResponse(), EventAssets.Alerts(), radius);
                placed++;
            }
            return placed;
        }

        private static AlertSettings LoadOrCreateSettings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<AlertSettings>(SettingsPath);
            if (settings != null) return settings;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath));
            settings = ScriptableObject.CreateInstance<AlertSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }
    }
}
