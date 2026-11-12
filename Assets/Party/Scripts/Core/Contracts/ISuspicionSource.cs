namespace Alarma.Core.Contracts
{
    // Algo que vigila y acumula sospecha de 0 a 1 (una cámara; más adelante un guardia). La alerta del local lee este
    // valor sin saber qué lo produce.
    public interface ISuspicionSource
    {
        float Suspicion { get; }
    }
}
