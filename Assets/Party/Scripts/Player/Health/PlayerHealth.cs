using System;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Sets;

namespace Alarma.Player.Health
{
    public enum LifeState { Alive, Downed, Arrested }

    // Vida del jugador con tres estados: vivo, derribado (a 0 de vida, no puede moverse y la policía puede arrestarlo)
    // y arrestado. Solo lleva la cuenta y avisa con eventos: la interfaz, el cuerpo y el movimiento escuchan.
    // Se anota en el conjunto de sospechosos para que la policía lo encuentre. Con red, estas decisiones serán del host.
    public sealed class PlayerHealth : MonoBehaviour, IDamageable, IArrestable, IDetectable
    {
        [SerializeField] private HealthSettings settings;
        [SerializeField] private SuspectSet suspects;
        [SerializeField, Tooltip("Punto del cuerpo al que miran y apuntan (pecho).")] private Transform detectionPoint;
        private float health, timer;

        public LifeState State { get; private set; } = LifeState.Alive;
        public float Normalized => settings != null ? health / settings.MaxHealth : 0f;
        // Segundos que faltan para levantarse (derribado) o para quedar libre (arrestado).
        public float SecondsLeft => State == LifeState.Alive ? 0f : Mathf.Max(0f, timer);
        public bool CanBeArrested => State == LifeState.Downed;
        public bool IsDetectable => State != LifeState.Arrested;
        public Transform DetectionPoint => detectionPoint != null ? detectionPoint : transform;
        public event Action<float> HealthChanged;
        // Estado anterior y nuevo.
        public event Action<LifeState, LifeState> StateChanged;

        public void Configure(HealthSettings healthSettings, SuspectSet set, Transform chest)
        {
            settings = healthSettings; suspects = set; detectionPoint = chest;
        }

        private void Awake() => health = settings != null ? settings.MaxHealth : 0f;
        private void OnEnable() { if (suspects != null) suspects.Add(gameObject); }
        private void OnDisable() { if (suspects != null) suspects.Remove(gameObject); }

        public void TakeDamage(float amount, GameObject instigator)
        {
            if (State != LifeState.Alive || amount <= 0f) return;
            SetHealth(health - amount);
            if (health > 0f) return;
            timer = settings.DownedSeconds;
            Enter(LifeState.Downed);
        }

        public void Arrest(GameObject officer)
        {
            if (!CanBeArrested) return;
            timer = settings.ArrestSeconds;
            Enter(LifeState.Arrested);
        }

        private void Update()
        {
            if (State == LifeState.Alive) return;
            timer -= Time.deltaTime;
            if (timer > 0f) return;
            // Derribado sin arresto: se levanta malherido. Arrestado: queda libre con la vida completa.
            SetHealth(State == LifeState.Downed ? settings.RecoverHealth : settings.MaxHealth);
            Enter(LifeState.Alive);
        }

        private void SetHealth(float value)
        {
            health = Mathf.Clamp(value, 0f, settings.MaxHealth);
            HealthChanged?.Invoke(Normalized);
        }

        private void Enter(LifeState next)
        {
            var previous = State;
            State = next;
            StateChanged?.Invoke(previous, next);
        }
    }
}
