using UnityEngine;

namespace Alarma.Core.Contracts
{
    // Lo que el jugador necesita saber del mundo: si la zona ya está lista y hasta dónde puede caminar.
    public interface IPlayableWorld
    {
        bool ReadyAt(Vector3 position);
        bool LoadFailed { get; }
        float HalfSize { get; }
    }
}
