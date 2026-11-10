using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    public enum PoliceResponsePhase { OnTheWay, OnScene, Withdrawn }

    // Estado de la respuesta policial: en camino (con los segundos que faltan), en el lugar o retirada.
    public readonly struct PoliceResponse
    {
        public readonly PoliceResponsePhase Phase;
        public readonly int SecondsToArrive;

        public PoliceResponse(PoliceResponsePhase phase, int secondsToArrive) { Phase = phase; SecondsToArrive = secondsToArrive; }
    }

    // Canal de la respuesta policial (patrón Observer con ScriptableObject): la central avisa la cuenta regresiva, la
    // llegada y la retirada; el aviso en pantalla (y más adelante la música y el nivel de búsqueda) escuchan.
    [CreateAssetMenu(menuName = "Alarma/Eventos/Canal de respuesta policial", fileName = "RespuestaPolicial")]
    public sealed class PoliceResponseChannel : ScriptableObject
    {
        public event Action<PoliceResponse> Raised;

        public void Raise(PoliceResponsePhase phase, int secondsToArrive = 0) => Raised?.Invoke(new PoliceResponse(phase, secondsToArrive));
    }
}
