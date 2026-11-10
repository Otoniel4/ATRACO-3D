using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Cómo reaccionan los civiles (GDD 4.3 y Task 13): valentía, miedo a los disparos, cuánto huyen y cuánto quedan
    // aturdidos. Un asset (Data/NPC/ReaccionesCiviles.asset) que se ajusta en el Inspector sin tocar código.
    [CreateAssetMenu(menuName = "Alarma/NPC/Ajustes de reacción", fileName = "ReaccionesCiviles")]
    public sealed class NpcReactionSettings : ScriptableObject
    {
        [field: SerializeField, Tooltip("Valentía con que nace cada civil (al azar entre estos dos valores, 0 a 1).")]
        public Vector2 BraveryRange { get; private set; } = new Vector2(.15f, .85f);
        [field: SerializeField, Tooltip("Valentía que quita un disparo a quemarropa; baja con la distancia.")]
        public float GunshotFear { get; private set; } = .9f;
        [field: SerializeField, Tooltip("Valentía que quita sentirse apuntado.")]
        public float AimFear { get; private set; } = .35f;
        [field: SerializeField, Tooltip("Por debajo de esta valentía se agacha pidiendo piedad en vez de huir.")]
        public float CowerBelow { get; private set; } = .4f;
        [field: SerializeField, Tooltip("Valentía que recupera por segundo cuando ya nadie lo apunta.")]
        public float BraveryRecovery { get; private set; } = .05f;
        [field: SerializeField, Tooltip("Ángulo desde su frente para sentirse apuntado de frente (se arrodilla); si no, huye.")]
        public float FrontAngle { get; private set; } = 70f;
        [field: SerializeField, Tooltip("Hasta dónde se oye el grito de alguien a quien le apuntan: los civiles cercanos reaccionan.")]
        public float AimAlarmRadius { get; private set; } = 22f;
        [field: SerializeField, Range(0f, 1f), Tooltip("Probabilidad de que un civil que está en la calle y no se acobarda grabe y llame a la policía en vez de huir.")]
        public float WitnessChance { get; private set; } = .7f;
        [field: SerializeField, Range(0f, 1f), Tooltip("Lo mismo para quien está dentro de un local: el cliente sale corriendo y graba ya afuera; el agachado (personal) graba a escondidas cuando no lo miran.")]
        public float IndoorWitnessChance { get; private set; } = .3f;
        [field: SerializeField, Tooltip("Segundos de sorpresa mirando el atraco antes de grabar o huir.")]
        public float StartleSeconds { get; private set; } = 1.2f;
        [field: SerializeField, Tooltip("Segundos seguidos sin que la amenaza lo mire para animarse a sacar el celular estando agachado.")]
        public float DistractedSeconds { get; private set; } = 2.5f;
        [field: SerializeField, Tooltip("Ángulo desde el frente de la amenaza a partir del cual ya no lo está mirando.")]
        public float DistractedAngle { get; private set; } = 70f;
        [field: SerializeField, Tooltip("El personal sigue agachado en su puesto mientras la amenaza esté a menos de esta distancia.")]
        public float StaffStayDistance { get; private set; } = 15f;
        [field: SerializeField, Tooltip("Distancia mínima a la amenaza para animarse a grabar; si la amenaza se acerca a la mitad, corta y huye.")]
        public float WitnessMinDistance { get; private set; } = 7f;
        [field: SerializeField, Tooltip("Segundos que tarda la llamada a la policía (la barra sobre el testigo).")]
        public float CallSeconds { get; private set; } = 8f;
        [field: SerializeField, Range(0f, 1f), Tooltip("Parte de la llamada que pasa grabando con el celular en alto; el resto lo tiene en la oreja.")]
        public float FilmShare { get; private set; } = .45f;
        [field: SerializeField, Tooltip("Dentro de un local, si el camino a la salida mide más que esto (está al fondo), no corre: se queda agachado.")]
        public float MaxEscapePath { get; private set; } = 30f;
        [field: SerializeField, Tooltip("Tampoco corre si ese camino pasa a menos de esta distancia de la amenaza (le tapa la salida).")]
        public float ExitClearance { get; private set; } = 2f;
        [field: SerializeField] public float RunSpeed { get; private set; } = 4.6f;
        [field: SerializeField] public float WalkSpeed { get; private set; } = 1.5f;
        [field: SerializeField, Tooltip("Segundos corriendo antes de seguir caminando lejos.")]
        public float FleeSeconds { get; private set; } = 8f;
        [field: SerializeField, Tooltip("Segundos agachado pidiendo piedad (al azar entre los dos).")]
        public Vector2 CowerSeconds { get; private set; } = new Vector2(6f, 12f);
        [field: SerializeField, Tooltip("Segundos arrodillado después de que dejan de apuntarle, antes de escapar.")]
        public float SurrenderSeconds { get; private set; } = 10f;
        [field: SerializeField, Tooltip("Lo mismo cuando quien le apuntaba ya guardó el arma: escapa antes.")]
        public float SurrenderSecondsUnarmed { get; private set; } = 6f;
        [field: SerializeField, Tooltip("Segundos aturdido en el suelo tras un disparo.")]
        public Vector2 StunSeconds { get; private set; } = new Vector2(6f, 9f);
        [field: SerializeField, Tooltip("Segundos aturdido tras el táser.")]
        public Vector2 TaserSeconds { get; private set; } = new Vector2(4f, 6f);
        [field: SerializeField, Tooltip("Duración del clip de levantarse (build_npc_reaction_clips.py).")]
        public float GetUpSeconds { get; private set; } = 2.2f;
        [field: SerializeField, Tooltip("Empujón del disparo sobre el cuerpo (impulso, kg·m/s).")]
        public float HitImpulse { get; private set; } = 60f;
        [field: SerializeField, Tooltip("Distancia detrás de la persona arrodillada donde se para quien la amarra.")]
        public float TieDistance { get; private set; } = .62f;
        [field: SerializeField, Tooltip("Lejos de toda amenaza a esta distancia, el doble de reacción desaparece.")]
        public float DespawnDistance { get; private set; } = 60f;
    }
}
