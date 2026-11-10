using UnityEngine;

namespace Alarma.AI.Security
{
    // Cómo vigilan las cámaras de los locales (GDD 8 y Task 15): giro, cono de visión y cuánto tardan en dar aviso.
    // Un asset (Data/NPC/Camaras.asset) para ajustar en el Inspector.
    [CreateAssetMenu(menuName = "Alarma/NPC/Ajustes de cámaras", fileName = "Camaras")]
    public sealed class SecurityCameraSettings : ScriptableObject
    {
        [field: SerializeField, Range(0f, 90f), Tooltip("Cuánto gira a cada lado de su posición de reposo.")]
        public float Sweep { get; private set; } = 40f;
        [field: SerializeField, Min(1f), Tooltip("Segundos de un barrido completo de ida y vuelta.")]
        public float Period { get; private set; } = 9f;
        [field: SerializeField, Tooltip("Alcance del cono de visión, en metros.")]
        public float Range { get; private set; } = 14f;
        [field: SerializeField, Range(5f, 80f), Tooltip("Mitad del ángulo del cono de visión.")]
        public float HalfAngle { get; private set; } = 28f;
        [field: SerializeField, Tooltip("Segundos viendo a alguien con un arma en la mano hasta dar aviso (la luz pasa de verde a rojo).")]
        public float DetectSeconds { get; private set; } = 2f;
        [field: SerializeField, Tooltip("Segundos sin verlo para olvidar la sospecha.")]
        public float ForgetSeconds { get; private set; } = 4f;
        [field: SerializeField, Tooltip("Segundos entre un aviso y el siguiente de la misma cámara.")]
        public float ReportCooldown { get; private set; } = 30f;
    }
}
