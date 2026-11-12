using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    // Niveles de alerta de un local (GDD 8 y Task 15), en orden de gravedad.
    public enum AlertLevel { Stealth, Suspicion, Alarm, PoliceOnTheWay, Assault }

    // Estado de alerta de un local: cuál, en qué nivel y cuánta sospecha (0 a 1).
    public readonly struct AlertStatus
    {
        public readonly GameObject Place;
        public readonly AlertLevel Level;
        public readonly float Suspicion;

        public AlertStatus(GameObject place, AlertLevel level, float suspicion) { Place = place; Level = level; Suspicion = suspicion; }
    }

    // Canal de alerta (patrón Observer con ScriptableObject): cada local avisa su nivel y su sospecha; escuchan el
    // medidor en pantalla y, más adelante, las luces y la sirena de la alarma (Task 16).
    [CreateAssetMenu(menuName = "Alarma/Eventos/Canal de alerta", fileName = "Alerta")]
    public sealed class AlertChannel : ScriptableObject
    {
        public event Action<AlertStatus> Raised;

        public void Raise(GameObject place, AlertLevel level, float suspicion) => Raised?.Invoke(new AlertStatus(place, level, suspicion));
    }
}
