using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    [CreateAssetMenu(fileName = "NewVoidEvent", menuName = "Alarma/Events/Void Channel")]
    public sealed class VoidEventChannel : ScriptableObject
    {
        public event Action Raised;

        [ContextMenu("Raise Event")]
        public void Raise()
        {
            Raised?.Invoke();
        }
    }
}
