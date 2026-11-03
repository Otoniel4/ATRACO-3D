using UnityEngine;

namespace Alarma.AI.CityLife
{
    public abstract class CityLifeAuthority : MonoBehaviour
    {
        public abstract bool CanSimulate { get; }
    }
}
