using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.Core.Events;
using Alarma.Core.Sets;

namespace Alarma.Core.Editor
{
    // Canales de eventos y conjuntos compartidos (Data/Events): los crea una vez y todos los sistemas usan el mismo asset.
    public static class EventAssets
    {
        private const string Folder = "Assets/Party/Data/Events/";

        // Denuncias de los testigos: las oyen el aviso en pantalla y la central de policía.
        public static CrimeReportChannel CrimeReports() => LoadOrCreate<CrimeReportChannel>("Denuncias");

        // Ruido de disparos y estallidos: lo avisan las armas y lo oyen los civiles (y más adelante guardias y alerta).
        public static NoiseChannel Noise() => LoadOrCreate<NoiseChannel>("Ruido");

        // Respuesta policial: cuenta regresiva, llegada y retirada.
        public static PoliceResponseChannel PoliceResponse() => LoadOrCreate<PoliceResponseChannel>("RespuestaPolicial");

        // A quiénes puede buscar la policía (los jugadores se anotan solos).
        public static SuspectSet Suspects() => LoadOrCreate<SuspectSet>("Sospechosos");

        private static T LoadOrCreate<T>(string name) where T : ScriptableObject
        {
            string path = Folder + name + ".asset";
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null) return asset;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            asset = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }
    }
}
