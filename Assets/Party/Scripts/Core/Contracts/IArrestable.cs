using UnityEngine;

namespace Alarma.Core.Contracts
{
    public interface IArrestable
    {
        bool CanBeArrested { get; }
        void Arrest(GameObject officer);
    }
}
