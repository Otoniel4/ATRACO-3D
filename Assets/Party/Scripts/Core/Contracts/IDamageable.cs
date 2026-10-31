using UnityEngine;

namespace Alarma.Core.Contracts
{
    public interface IDamageable
    {
        // El origen puede ser null para daño del entorno.
        void TakeDamage(float amount, GameObject instigator);
    }
}
