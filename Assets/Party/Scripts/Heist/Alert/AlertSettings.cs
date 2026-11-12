using UnityEngine;

namespace Alarma.Heist.Alert
{
    // Tiempos de la alerta de los locales (GDD 8 y Task 15). Un asset (Data/Heist/Alerta.asset) para el Inspector.
    [CreateAssetMenu(menuName = "Alarma/Atraco/Ajustes de alerta", fileName = "Alerta")]
    public sealed class AlertSettings : ScriptableObject
    {
        [field: SerializeField, Min(0f), Tooltip("Segundos que suena la alarma antes de mostrar que la policía viene en camino.")]
        public float AlarmSeconds { get; private set; } = 3f;
        [field: SerializeField, Min(1f), Tooltip("Segundos de alarma sin que venga la policía hasta volver a la calma.")]
        public float CalmSeconds { get; private set; } = 20f;
        [field: SerializeField, Min(0f), Tooltip("Metros alrededor del local donde una denuncia cuenta como suya.")]
        public float Margin { get; private set; } = 4f;
    }
}
