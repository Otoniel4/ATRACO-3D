using System;
using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.City
{
    // Activa solo los sectores de edificios y mobiliario cercanos al observador; el suelo queda siempre visible.
    // Todo está ya en la escena, así que la zona siempre está lista para caminar.
    public sealed class CitySectorStreamer : MonoBehaviour, IPlayableWorld
    {
        [Serializable]
        public struct Sector
        {
            public GameObject Root;
            [Tooltip("Esquina suroeste (X, Z).")] public Vector2 Min;
            [Tooltip("Esquina noreste (X, Z).")] public Vector2 Max;
        }

        [SerializeField] private Transform observer;
        [SerializeField] private Sector[] sectors = Array.Empty<Sector>();
        [SerializeField, Min(50f)] private float activeRadius = 420f;
        [SerializeField, Min(100f)] private float halfSize = 1000f;
        [SerializeField, Min(.05f)] private float refreshSeconds = .25f;
        private float nextRefresh;

        public bool LoadFailed => false;
        public float HalfSize => halfSize - 3f;
        public int ActiveCount { get; private set; }

        public void Configure(Transform focus, Sector[] parts, float half, float radius)
        {
            observer = focus; sectors = parts; halfSize = half; activeRadius = radius;
        }

        public bool ReadyAt(Vector3 position) => true;

        private void Start() => Refresh();

        private void Update()
        {
            if (Time.unscaledTime < nextRefresh) return;
            nextRefresh = Time.unscaledTime + refreshSeconds;
            Refresh();
        }

        private void Refresh()
        {
            if (observer == null) return;
            Vector3 p = observer.position;
            float limit = activeRadius * activeRadius;
            int active = 0;
            foreach (var sector in sectors)
            {
                // Distancia del observador al rectángulo del sector, no a su centro.
                float dx = Mathf.Max(0f, Mathf.Max(sector.Min.x - p.x, p.x - sector.Max.x));
                float dz = Mathf.Max(0f, Mathf.Max(sector.Min.y - p.z, p.z - sector.Max.y));
                bool on = dx * dx + dz * dz < limit;
                if (sector.Root.activeSelf != on) sector.Root.SetActive(on);
                if (on) active++;
            }
            ActiveCount = active;
        }
    }
}
