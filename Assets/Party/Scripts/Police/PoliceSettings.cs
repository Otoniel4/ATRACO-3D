using UnityEngine;

namespace Alarma.Police
{
    // Cómo responde la policía a pie (GDD 10 y Task 19): cuánto tarda, cuántos llegan, cómo persiguen, disparan y
    // arrestan, y cuánto quedan en el suelo al ser derribados. Un asset (Data/Police/Policia.asset) para el Inspector.
    [CreateAssetMenu(menuName = "Alarma/Policía/Ajustes de policía a pie", fileName = "Policia")]
    public sealed class PoliceSettings : ScriptableObject
    {
        [field: Header("Respuesta")]
        [field: SerializeField, Tooltip("Cuenta regresiva desde la denuncia hasta que aparecen los agentes.")]
        public float ResponseSeconds { get; private set; } = 20f;
        [field: SerializeField, Min(1)] public int Officers { get; private set; } = 2;
        [field: SerializeField, Tooltip("Distancia al lugar de la denuncia a la que aparecen (mínima y máxima).")]
        public Vector2 SpawnDistance { get; private set; } = new Vector2(30f, 45f);

        [field: Header("Movimiento y búsqueda")]
        [field: SerializeField] public float WalkSpeed { get; private set; } = 1.6f;
        [field: SerializeField] public float RunSpeed { get; private set; } = 4.2f;
        [field: SerializeField, Tooltip("Hasta dónde ve a un sospechoso si nada lo tapa.")]
        public float SightRange { get; private set; } = 40f;
        [field: SerializeField, Tooltip("Segundos sin verlo antes de dejar de perseguir y ponerse a buscar.")]
        public float LoseSightSeconds { get; private set; } = 6f;
        [field: SerializeField, Tooltip("Segundos buscando alrededor del último lugar antes de retirarse.")]
        public float SearchSeconds { get; private set; } = 25f;
        [field: SerializeField] public float SearchRadius { get; private set; } = 12f;
        [field: SerializeField, Tooltip("Segundos caminando de regreso antes de desaparecer.")]
        public float LeaveSeconds { get; private set; } = 10f;

        [field: Header("Disparo")]
        [field: SerializeField, Tooltip("Distancia a la que se detiene, apunta y dispara.")]
        public float ShootRange { get; private set; } = 16f;
        [field: SerializeField, Tooltip("Segundos apuntando antes del primer disparo (da tiempo a cubrirse).")]
        public float AimSeconds { get; private set; } = 1.2f;
        [field: SerializeField] public float ShotInterval { get; private set; } = .9f;
        [field: SerializeField] public float Damage { get; private set; } = 12f;
        [field: SerializeField, Tooltip("Dispersión del disparo, en grados.")]
        public float Spread { get; private set; } = 4f;
        [field: SerializeField, Tooltip("Hasta dónde se oye el disparo (asusta a los civiles).")]
        public float GunshotRadius { get; private set; } = 35f;

        [field: Header("Arresto")]
        [field: SerializeField, Tooltip("Distancia al derribado para esposarlo.")]
        public float ArrestDistance { get; private set; } = 1.2f;
        [field: SerializeField, Tooltip("Duración del clip Esposar (build_npc_reaction_clips.py).")]
        public float ArrestSeconds { get; private set; } = 2.4f;

        [field: Header("Caída")]
        [field: SerializeField, Tooltip("Segundos en el suelo tras recibir un disparo (al azar entre los dos).")]
        public Vector2 StunSeconds { get; private set; } = new Vector2(10f, 10f);
        [field: SerializeField, Tooltip("Empujón del disparo (impulso, kg·m/s): exagerado a propósito, la caída es cómica.")]
        public float HitImpulse { get; private set; } = 150f;
        [field: SerializeField, Tooltip("Cuánto del empujón va hacia arriba.")]
        public float HitLift { get; private set; } = .55f;
        [field: SerializeField, Tooltip("Duración del clip de levantarse.")]
        public float GetUpSeconds { get; private set; } = 2.2f;
    }
}
