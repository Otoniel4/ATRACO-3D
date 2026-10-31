using UnityEngine;

namespace Alarma.Core.Contracts
{
    public interface IInteractable
    {
        string InteractionPrompt { get; }
        float InteractionDuration { get; }
        bool CanInteract(GameObject interactor);
        void Interact(GameObject interactor);
    }
}
