namespace Alarma.Vehicles
{
    // Lo que las luces necesitan saber de quien maneja el auto (conductor de tráfico o, más adelante, un jugador).
    public interface IVehicleState
    {
        bool Braking { get; }
        int TurnSignal { get; } // -1 izquierda, 0 nada, 1 derecha
    }
}
