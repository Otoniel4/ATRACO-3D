using System;
using Alarma.Core.Events;

namespace Alarma.Heist.Alert
{
    // Alerta de un local sin dependencias de escena (contexto del patrón State; los estados están en AlertStates.cs):
    // sigilo → sospecha → alarma → policía en camino → asalto. Recibe la sospecha, las denuncias y el estado de la
    // policía, y avisa cada cambio de nivel. Con red, la lleva solo el host.
    public sealed class AlertMachine
    {
        private AlertState state;

        public AlertMachine(float alarmSeconds, float calmSeconds)
        {
            AlarmSeconds = alarmSeconds;
            CalmSeconds = calmSeconds;
            state = new StealthState();
        }

        public event Action<AlertLevel> LevelChanged;

        public AlertLevel Level => state.Level;
        // Sospecha de 0 a 1; desde la alarma en adelante queda llena.
        public float Suspicion { get; private set; }
        // Segundos que suena la alarma antes de pasar a «policía en camino».
        public float AlarmSeconds { get; }
        // Segundos de alarma sin que venga la policía hasta volver a la calma.
        public float CalmSeconds { get; }
        // Última noticia de la policía; null si no viene o ya se retiró.
        public PoliceResponsePhase? Police { get; private set; }

        public void Tick(float suspicion, float deltaTime)
        {
            Suspicion = Level >= AlertLevel.Alarm ? 1f : Math.Min(1f, Math.Max(0f, suspicion));
            state.Tick(this, deltaTime);
        }

        // Alguien denunció un delito en este local (testigo, cámara o radio de un guardia).
        public void Report() => state.Report(this);

        public void PoliceUpdate(PoliceResponsePhase phase)
        {
            Police = phase == PoliceResponsePhase.Withdrawn ? (PoliceResponsePhase?)null : phase;
        }

        // Vuelve a sigilo (el local se apagó por estar lejos de todos los jugadores).
        public void Reset()
        {
            Suspicion = 0f;
            if (Level != AlertLevel.Stealth) Change(new StealthState());
        }

        internal void Change(AlertState next)
        {
            state = next;
            if (Level >= AlertLevel.Alarm) Suspicion = 1f;
            LevelChanged?.Invoke(Level);
        }
    }
}
