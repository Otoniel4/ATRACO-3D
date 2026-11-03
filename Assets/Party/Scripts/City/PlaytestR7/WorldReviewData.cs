using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    [Serializable] public sealed class WorldReviewCell
    {
        public string Resource;
        public Bounds Bounds;
        public Vector3 Origin;
        public bool Always;
    }
    [Serializable] public sealed class ReviewDestination
    {
        public string Id,Label;
        public Vector3 Position;
        public float Yaw=180;
    }
    [CreateAssetMenu(menuName="Alarma datos/Mapa de prueba")]
    public sealed class WorldReviewData:ScriptableObject
    {
        public WorldReviewCell[] Cells=Array.Empty<WorldReviewCell>();
        public ReviewDestination[] Destinations=Array.Empty<ReviewDestination>();
        public Texture2D MapTexture;
        [Min(50)] public float LoadRadius=180;
        [Min(80)] public float UnloadRadius=240;
        [Range(1,4)] public int ConcurrentLoads=2;
    }
}
