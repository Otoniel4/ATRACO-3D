using UnityEngine;

namespace Alarma.Vehicles
{
    // Hace que ningún auto se vea igual: pintura de la paleta y, en los que circulan, acompañante solo a veces.
    // Los autos de tráfico cambian cada vez que salen del pool; los estacionados usan su posición y no cambian al volver.
    public sealed class CarAppearance : MonoBehaviour
    {
        private static readonly int BaseColor = Shader.PropertyToID("_BaseColor");

        [SerializeField] private CarPalette palette;
        [SerializeField] private bool varyOnEveryEnable = true;
        [SerializeField] private Renderer[] paint;
        [SerializeField] private GameObject passenger;
        private MaterialPropertyBlock block;

        public void Configure(CarPalette colors, bool perSpawn, Renderer[] body, GameObject rider)
        {
            palette = colors; varyOnEveryEnable = perSpawn; paint = body; passenger = rider;
        }

        private void OnEnable()
        {
            if (palette == null) return;
            Vector3 p = transform.position;
            int seed = varyOnEveryEnable ? Random.Range(int.MinValue, int.MaxValue) : Mathf.RoundToInt(p.x * 73.1f) ^ Mathf.RoundToInt(p.z * 37.7f);
            var random = new System.Random(seed);
            block ??= new MaterialPropertyBlock();
            block.SetColor(BaseColor, palette.Paint(random));
            foreach (var r in paint) r.SetPropertyBlock(block);
            if (passenger != null) passenger.SetActive(random.NextDouble() < palette.PassengerChance);
        }
    }
}
