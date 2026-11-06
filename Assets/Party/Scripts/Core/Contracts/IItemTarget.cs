using UnityEngine;

namespace Alarma.Core.Contracts
{
    // Algo que responde a un arma o herramienta del jugador: una caja registradora a la palanca, una vitrina al
    // cortavidrios, una cámara a la tablet, una caja fuerte al taladro. El objeto se identifica por su id (ItemDefinition).
    public interface IItemTarget
    {
        bool Accepts(string itemId);
        // Devuelve lo que se le muestra al jugador (por ejemplo, «Caja forzada»).
        string UseItem(string itemId, GameObject user);
    }
}
