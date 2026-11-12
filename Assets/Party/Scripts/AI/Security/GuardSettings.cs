using UnityEngine;

namespace Alarma.AI.Security
{
    // Cómo defienden su local los guardias (GDD 8 y Task 14): qué ven y oyen, hasta dónde persiguen, cómo golpean con
    // la porra y cuánto quedan en el suelo. Un asset (Data/NPC/Guardias.asset) para ajustar en el Inspector.
    [CreateAssetMenu(menuName = "Alarma/NPC/Ajustes de guardias", fileName = "Guardias")]
    public sealed class GuardSettings : ScriptableObject
    {
        [field: Header("Percepción")]
        [field: SerializeField, Tooltip("Hasta dónde ve a alguien con un arma en la mano (también por las vidrieras).")]
        public float SightRange { get; private set; } = 18f;
        [field: SerializeField, Tooltip("Disparos y gritos a menos de esta distancia de su puesto lo ponen en marcha.")]
        public float HearRange { get; private set; } = 30f;
        [field: SerializeField, Tooltip("No persigue más lejos que esto de su puesto: vuelve a cuidar el local.")]
        public float LeashDistance { get; private set; } = 45f;

        [field: Header("Movimiento")]
        [field: SerializeField] public float WalkSpeed { get; private set; } = 1.6f;
        [field: SerializeField] public float RunSpeed { get; private set; } = 4.4f;

        [field: Header("Porra")]
        [field: SerializeField, Tooltip("Distancia a la que se detiene a golpear.")]
        public float StrikeDistance { get; private set; } = 1.3f;
        [field: SerializeField, Tooltip("Alcance del golpe: si el blanco se alejó más, falla.")]
        public float StrikeReach { get; private set; } = 1.9f;
        [field: SerializeField, Tooltip("Duración de un golpe completo.")]
        public float StrikeSeconds { get; private set; } = .9f;
        [field: SerializeField, Range(0f, 1f), Tooltip("Momento del golpe en que la porra pega (parte de su duración).")]
        public float HitAt { get; private set; } = .45f;
        [field: SerializeField] public float Damage { get; private set; } = 18f;

        [field: Header("Caída")]
        [field: SerializeField, Tooltip("Segundos inconsciente tras recibir un disparo (al azar entre los dos).")]
        public Vector2 StunSeconds { get; private set; } = new Vector2(10f, 10f);
        [field: SerializeField, Tooltip("Empujón del disparo (impulso, kg·m/s).")]
        public float HitImpulse { get; private set; } = 70f;
        [field: SerializeField, Tooltip("Duración del clip de levantarse.")]
        public float GetUpSeconds { get; private set; } = 2.2f;
    }
}
