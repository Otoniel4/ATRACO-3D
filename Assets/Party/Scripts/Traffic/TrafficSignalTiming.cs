using UnityEngine;

namespace Alarma.Traffic
{
    // Tiempos de cada turno de un cruce: verde, amarillo y un instante con todo en rojo antes del siguiente eje.
    [CreateAssetMenu(menuName = "Alarma/Tiempos de semáforo", fileName = "TrafficSignalTiming")]
    public sealed class TrafficSignalTiming : ScriptableObject
    {
        [SerializeField, Min(3f)] private float green = 14f;
        [SerializeField, Min(1f)] private float yellow = 3f;
        [SerializeField, Min(0f)] private float allRed = 1.5f;

        public float Green => green;
        public float Yellow => yellow;
        public float Slot => green + yellow + allRed;
    }
}
