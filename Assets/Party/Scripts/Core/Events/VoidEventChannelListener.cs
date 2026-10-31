using UnityEngine;
using UnityEngine.Events;

namespace Alarma.Core.Events
{
    [DisallowMultipleComponent]
    [AddComponentMenu("Alarma/Events/Void Event Channel Listener")]
    public sealed class VoidEventChannelListener : MonoBehaviour
    {
        [SerializeField, Tooltip("Canal que se escuchará al activar el componente.")]
        private VoidEventChannel channel;

        [SerializeField, Tooltip("Acciones que responderán al evento.")]
        private UnityEvent response = new UnityEvent();

        private VoidEventChannel subscribedChannel;

        private void OnEnable()
        {
            subscribedChannel = channel;
            if (subscribedChannel != null)
            {
                subscribedChannel.Raised += HandleRaised;
            }
        }

        private void OnDisable()
        {
            // Se libera el canal realmente suscrito, aunque el Inspector haya cambiado.
            if (subscribedChannel != null)
            {
                subscribedChannel.Raised -= HandleRaised;
            }

            subscribedChannel = null;
        }

        private void HandleRaised()
        {
            response.Invoke();
        }
    }
}
