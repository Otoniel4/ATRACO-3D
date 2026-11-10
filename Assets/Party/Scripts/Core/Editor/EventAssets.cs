using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.Core.Events;

namespace Alarma.Core.Editor
{
    // Canales de eventos compartidos (Data/Events): los crea una vez y todos los sistemas usan el mismo asset.
    public static class EventAssets
    {
        private const string NoisePath = "Assets/Party/Data/Events/Ruido.asset";
        private const string ReportsPath = "Assets/Party/Data/Events/Denuncias.asset";

        // Denuncias de los testigos: las oye el aviso en pantalla (y más adelante la policía y el nivel de búsqueda).
        public static CrimeReportChannel CrimeReports()
        {
            var channel = AssetDatabase.LoadAssetAtPath<CrimeReportChannel>(ReportsPath);
            if (channel != null) return channel;
            Directory.CreateDirectory(Path.GetDirectoryName(ReportsPath));
            channel = ScriptableObject.CreateInstance<CrimeReportChannel>();
            AssetDatabase.CreateAsset(channel, ReportsPath);
            return channel;
        }

        // Ruido de disparos y estallidos: lo avisan las armas y lo oyen los civiles (y más adelante guardias y alerta).
        public static NoiseChannel Noise()
        {
            var channel = AssetDatabase.LoadAssetAtPath<NoiseChannel>(NoisePath);
            if (channel != null) return channel;
            Directory.CreateDirectory(Path.GetDirectoryName(NoisePath));
            channel = ScriptableObject.CreateInstance<NoiseChannel>();
            AssetDatabase.CreateAsset(channel, NoisePath);
            return channel;
        }
    }
}
