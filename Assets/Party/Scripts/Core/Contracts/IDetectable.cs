using UnityEngine;

namespace Alarma.Core.Contracts
{
    public interface IDetectable
    {
        bool IsDetectable { get; }
        Transform DetectionPoint { get; }
    }
}
