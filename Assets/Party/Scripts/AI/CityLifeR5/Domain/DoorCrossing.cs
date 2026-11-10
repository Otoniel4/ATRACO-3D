namespace Alarma.AI.CityLife
{
    public enum DoorPhase { Idle, Turning, Stepping, Reaching, Opening }

    // Lo que el cliente hace este cuadro frente a la puerta cerrada.
    public readonly struct DoorAction
    {
        public readonly bool Face, Step, Reach, Push;
        public DoorAction(bool face, bool step, bool reach, bool push) { Face = face; Step = step; Reach = reach; Push = push; }
    }

    // Cruzar una puerta de empuje (patrón State) sin poder trabarse: gira hacia la puerta, se acerca a la placa, extiende
    // la mano y empuja. Cada fase termina al cumplirse su objetivo o al vencer su tiempo, como el evento de una animación,
    // así que la precisión del brazo o del giro nunca deja al cliente esperando para siempre. Si la puerta no abre o se
    // cierra antes de pasar, vuelve a empujar. Sin Unity: se prueba sola (DoorCrossingTests).
    public sealed class DoorCrossing
    {
        public const float TurnLimit = .6f, StepLimit = .7f, ReachLimit = .5f, OpenLimit = 1.4f;
        public const float Faced = .95f, Touchable = .82f;
        private float time;

        public DoorPhase Phase { get; private set; } = DoorPhase.Idle;
        // Empujes desde que llegó a la puerta: más de dos seguidos sin abrir indican algo que bloquea la hoja.
        public int Pushes { get; private set; }

        // atDoor: primero en la fila, de su lado y con la puerta a su alcance. facing: 1 = mirando de frente a la puerta.
        public DoorAction Tick(float deltaTime, bool atDoor, bool doorOpen, float facing, bool atStand, bool touching)
        {
            if (!atDoor || doorOpen)
            {
                Phase = DoorPhase.Idle;
                time = 0f;
                if (!atDoor && !doorOpen) Pushes = 0; // se fue o la puerta volvió a cerrarse: la próxima vez empieza de cero
                return default;
            }
            if (Phase == DoorPhase.Idle) Enter(DoorPhase.Turning);
            time += deltaTime;
            switch (Phase)
            {
                case DoorPhase.Turning:
                    if (facing >= Faced || time >= TurnLimit) Enter(DoorPhase.Stepping);
                    return new DoorAction(true, false, false, false);
                case DoorPhase.Stepping:
                    if (atStand || time >= StepLimit) Enter(DoorPhase.Reaching);
                    return new DoorAction(true, true, false, false);
                case DoorPhase.Reaching:
                    if ((touching && facing >= Touchable) || time >= ReachLimit)
                    {
                        Enter(DoorPhase.Opening);
                        Pushes++;
                        return new DoorAction(true, false, true, true);
                    }
                    return new DoorAction(true, false, true, false);
                default: // Opening: mantiene la mano en la placa mientras la hoja se abre; si no abrió, otro intento
                    if (time >= OpenLimit) Enter(DoorPhase.Reaching);
                    return new DoorAction(true, false, true, false);
            }
        }

        private void Enter(DoorPhase next) { Phase = next; time = 0f; }
    }
}
