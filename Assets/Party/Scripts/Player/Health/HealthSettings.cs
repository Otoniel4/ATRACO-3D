using UnityEngine;

namespace Alarma.Player.Health
{
    // Vida del jugador (GDD 9 y Task 18): cuánta tiene y cuánto dura derribado o detenido. Un asset
    // (Data/Player/Vida.asset) que se ajusta en el Inspector sin tocar código.
    [CreateAssetMenu(menuName = "Alarma/Jugador/Ajustes de vida", fileName = "Vida")]
    public sealed class HealthSettings : ScriptableObject
    {
        [field: SerializeField, Min(1f)] public float MaxHealth { get; private set; } = 100f;
        [field: SerializeField, Tooltip("Segundos derribado antes de levantarse solo si nadie lo arresta (el rescate de un compañero llega con la red).")]
        public float DownedSeconds { get; private set; } = 10f;
        [field: SerializeField, Tooltip("Vida con que se levanta después de estar derribado.")]
        public float RecoverHealth { get; private set; } = 25f;
        [field: SerializeField, Tooltip("Segundos detenido antes de volver al escondite (la cárcel y la fianza son de Task 20).")]
        public float ArrestSeconds { get; private set; } = 5f;
    }
}
