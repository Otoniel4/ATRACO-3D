using System;

namespace Alarma.AI.CityLife.Editor
{
    // Blender añade .001, .002... para mantener nombres únicos dentro del archivo.
    public static class BlenderAssetNames
    {
        public static string BaseName(string name)
        {
            if (string.IsNullOrEmpty(name)) return name;
            int dot = name.LastIndexOf('.');
            if (dot < 1 || name.Length - dot - 1 < 3) return name;
            for (int i = dot + 1; i < name.Length; i++)
                if (name[i] < '0' || name[i] > '9') return name;
            return name.Substring(0, dot);
        }

        public static bool Matches(string actual, string expected)
            => string.Equals(actual, expected, StringComparison.Ordinal)
                || string.Equals(BaseName(actual), expected, StringComparison.Ordinal);
    }
}
