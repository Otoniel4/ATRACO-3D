using Alarma.Core.Events;

namespace Alarma.Heist.Alert
{
    // Un nivel de alerta del local: qué hace cada cuadro y cómo responde a una denuncia. Agregar un nivel es agregar
    // una clase; la máquina no cambia.
    public abstract class AlertState
    {
        public abstract AlertLevel Level { get; }
        public abstract void Tick(AlertMachine machine, float deltaTime);
        public virtual void Report(AlertMachine machine) { }
    }

    // Nadie sospecha nada.
    public sealed class StealthState : AlertState
    {
        public override AlertLevel Level => AlertLevel.Stealth;

        public override void Tick(AlertMachine machine, float deltaTime)
        {
            if (machine.Suspicion >= 1f) machine.Change(new AlarmState());
            else if (machine.Suspicion > 0f) machine.Change(new SuspicionState());
        }

        public override void Report(AlertMachine machine) => machine.Change(new AlarmState());
    }

    // Una cámara está viendo algo raro: el medidor se llena; si se vacía, vuelve la calma.
    public sealed class SuspicionState : AlertState
    {
        public override AlertLevel Level => AlertLevel.Suspicion;

        public override void Tick(AlertMachine machine, float deltaTime)
        {
            if (machine.Suspicion >= 1f) machine.Change(new AlarmState());
            else if (machine.Suspicion <= 0f) machine.Change(new StealthState());
        }

        public override void Report(AlertMachine machine) => machine.Change(new AlarmState());
    }

    // Saltó la alarma: suena unos segundos y sigue según lo que haga la policía. Si nadie viene, se apaga sola.
    public sealed class AlarmState : AlertState
    {
        private float elapsed;

        public override AlertLevel Level => AlertLevel.Alarm;

        public override void Tick(AlertMachine machine, float deltaTime)
        {
            elapsed += deltaTime;
            if (elapsed < machine.AlarmSeconds) return;
            if (machine.Police == PoliceResponsePhase.OnScene) machine.Change(new AssaultState());
            else if (machine.Police == PoliceResponsePhase.OnTheWay) machine.Change(new PoliceOnTheWayState());
            else if (elapsed >= machine.CalmSeconds) machine.Change(new StealthState());
        }
    }

    // La policía ya salió hacia el local.
    public sealed class PoliceOnTheWayState : AlertState
    {
        public override AlertLevel Level => AlertLevel.PoliceOnTheWay;

        public override void Tick(AlertMachine machine, float deltaTime)
        {
            if (machine.Police == PoliceResponsePhase.OnScene) machine.Change(new AssaultState());
            else if (machine.Police == null) machine.Change(new StealthState());
        }
    }

    // La policía está en el lugar; termina cuando se retira.
    public sealed class AssaultState : AlertState
    {
        public override AlertLevel Level => AlertLevel.Assault;

        public override void Tick(AlertMachine machine, float deltaTime)
        {
            if (machine.Police == null) machine.Change(new StealthState());
        }
    }
}
