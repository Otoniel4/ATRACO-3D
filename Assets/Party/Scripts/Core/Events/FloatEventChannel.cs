using UnityEngine;

namespace Alarma.Core.Events
{
    [CreateAssetMenu(fileName = "NewFloatEvent", menuName = "Alarma/Events/Float Channel")]
    public sealed class FloatEventChannel : EventChannel<float>
    {
    }
}
