using UnityEngine;

namespace Alarma.Core.Events
{
    [CreateAssetMenu(fileName = "NewIntEvent", menuName = "Alarma/Events/Int Channel")]
    public sealed class IntEventChannel : EventChannel<int>
    {
    }
}
