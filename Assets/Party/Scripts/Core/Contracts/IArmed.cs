namespace Alarma.Core.Contracts
{
    // Quien puede llevar un arma a la vista (el jugador). Los NPC lo consultan para saber si la amenaza sigue armada
    // o ya guardó el arma, sin conocer cómo funciona el inventario.
    public interface IArmed
    {
        bool WeaponDrawn { get; }
    }
}
