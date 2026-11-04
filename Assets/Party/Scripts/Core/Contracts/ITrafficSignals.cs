namespace Alarma.Core.Contracts
{
    public enum SignalLight { Green, Yellow, Red }

    // Lo que peatones y autos consultan de un semáforo: la luz de un eje (dirección de la vía) y cuánto falta para su verde.
    public interface ITrafficSignals
    {
        SignalLight Light(int signal, int axis);
        float SecondsUntilGreen(int signal, int axis);
    }
}
