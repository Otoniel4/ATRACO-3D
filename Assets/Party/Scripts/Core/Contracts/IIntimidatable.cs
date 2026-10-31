using UnityEngine;

namespace Alarma.Core.Contracts
{
    public interface IIntimidatable
    {
        // Cada origen se identifica para admitir varios jugadores apuntando al mismo NPC.
        void BeginIntimidation(GameObject instigator);
        void EndIntimidation(GameObject instigator);
    }
}
