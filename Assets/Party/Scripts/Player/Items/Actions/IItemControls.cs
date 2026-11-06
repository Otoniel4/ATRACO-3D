namespace Alarma.Player.Items
{
    // Controles para usar el objeto en la mano: clic derecho apunta, clic izquierdo usa (o dispara) y mantenerlo repite.
    public interface IItemControls
    {
        bool AimHeld { get; }
        bool UsePressed { get; }
        bool UseHeld { get; }
    }
}
