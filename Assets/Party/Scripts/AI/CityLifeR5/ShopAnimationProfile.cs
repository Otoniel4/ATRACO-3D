using UnityEngine;

namespace Alarma.AI.CityLife
{
    [CreateAssetMenu(menuName = "Alarma/Ciudad/Animación de atención")]
    public sealed class ShopAnimationProfile : ScriptableObject
    {
        public CounterTiming Timing = new CounterTiming();
        [Tooltip("Centro del intercambio en coordenadas locales del negocio, sobre su tablero.")]
        public Vector3 CounterCenter;
        public Vector3 CounterNormal = Vector3.forward;
        [Min(.1f)] public float CounterWidth = .95f;
        [Min(.2f)] public float HandSpeed = 1.2f;
        [Min(.04f)] public float HandSmoothing = .12f;
        [Min(.1f)] public float TransferSeconds = .32f;
        [Min(0f)] public float TransferLift = .035f;
        [Min(0f)] public float InspectionLift = .08f;
        [Min(0f)] public float InspectionSweep = .1f;
        [Range(0f, 45f)] public float InspectionTilt = 10f;
        [Tooltip("Altura del punto de agarre dentro del producto: 0 = base, 1 = parte superior.")]
        [Range(0f, 1f)] public float GripHeight = 0f;
        [Tooltip("Piezas transportables del modelo. Vacío conserva el producto completo.")]
        public string[] ProductParts = System.Array.Empty<string>();
    }
}
