using UnityEngine;

namespace Alarma.Core.Contracts
{
    // Objetivo que pide dónde debe pararse quien lo usa (las bridas se ponen desde atrás de la persona). Se llama antes
    // de empezar la animación: el objetivo puede prepararse (por ejemplo, llevar las manos a la espalda).
    public interface IUseAnchor
    {
        bool PrepareUse(string itemId, GameObject user, out Pose standAt);
    }
}
