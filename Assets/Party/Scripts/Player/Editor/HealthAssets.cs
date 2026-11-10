using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.Player.Health;

namespace Alarma.Player.Editor
{
    // Ajustes de vida del jugador (Data/Player/Vida.asset): los crea una vez con los valores por defecto.
    public static class HealthAssets
    {
        private const string Path = "Assets/Party/Data/Player/Vida.asset";

        public static HealthSettings Settings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<HealthSettings>(Path);
            if (settings != null) return settings;
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(Path));
            settings = ScriptableObject.CreateInstance<HealthSettings>();
            AssetDatabase.CreateAsset(settings, Path);
            return settings;
        }
    }
}
