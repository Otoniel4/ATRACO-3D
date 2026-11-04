using System;
using UnityEngine;

namespace Alarma.UI.Map
{
    [Serializable]
    public sealed class MapCategory
    {
        public string Id;
        public string Label;
        public string Group;
        public Color Color = Color.white;
        public Texture2D Icon;
    }

    [Serializable]
    public sealed class MapPlace
    {
        public string Category;
        public string Name;
        public Vector3 Position;
    }

    // Datos de un mapa: fondo, límites del mundo y lugares con su categoría.
    // La pantalla y el minimapa solo leen esto, así que sirven para cualquier ciudad.
    [CreateAssetMenu(menuName = "Alarma/Mapa de ciudad")]
    public sealed class CityMapDefinition : ScriptableObject
    {
        public string Title = "Mapa";
        public Texture2D Background;
        public Texture2D PlayerIcon;
        [Tooltip("Esquina suroeste del mundo (X, Z).")] public Vector2 WorldMin = new Vector2(-1250, -1250);
        [Tooltip("Esquina noreste del mundo (X, Z).")] public Vector2 WorldMax = new Vector2(1250, 1250);
        public MapCategory[] Categories = Array.Empty<MapCategory>();
        public MapPlace[] Places = Array.Empty<MapPlace>();

        public float WorldSize => Mathf.Max(WorldMax.x - WorldMin.x, WorldMax.y - WorldMin.y);

        // 0-1 en el plano: X hacia el este y Z hacia el norte, como la textura (origen abajo a la izquierda).
        public Vector2 Normalized(Vector3 world) =>
            new Vector2(Mathf.InverseLerp(WorldMin.x, WorldMax.x, world.x), Mathf.InverseLerp(WorldMin.y, WorldMax.y, world.z));

        public MapCategory Category(string id) => Array.Find(Categories, c => c.Id == id);
    }
}
