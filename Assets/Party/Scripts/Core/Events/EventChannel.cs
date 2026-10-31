using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    public abstract class EventChannel<T> : ScriptableObject
    {
        public event Action<T> Raised;

        public void Raise(T value)
        {
            Raised?.Invoke(value);
        }
    }
}
