using UnityEngine;
using UnityEngine.UI;
using Alarma.Core.Events;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Aviso arriba al centro cuando alguien avisa a la policía (testigo, cámara o guardia). Solo escucha el canal de
    // denuncias: no conoce a quien avisa ni a la policía.
    public sealed class CrimeAlertView : MonoBehaviour
    {
        private const float Seconds = 5f;
        [SerializeField] private CrimeReportChannel reports;
        private Text label;
        private float until;

        public void Configure(CrimeReportChannel channel) => reports = channel;

        private void Awake()
        {
            var canvas = MapUi.Canvas("Aviso de denuncia", transform, 36);
            label = MapUi.Label("Texto", canvas.transform, "", 34, new Color(1f, .35f, .3f, 0f), TextAnchor.MiddleCenter);
            MapUi.Place(label.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, -170), new Vector2(0, -110));
        }

        private void OnEnable() { if (reports != null) reports.Raised += OnReport; }
        private void OnDisable() { if (reports != null) reports.Raised -= OnReport; }

        private void OnReport(CrimeReport report)
        {
            label.text = report.Source == CrimeReportSource.Camera ? "¡Una cámara te vio: avisó a la policía!"
                       : report.Source == CrimeReportSource.Guard ? "¡Guardia caído: su radio avisó a la policía!" : "¡Un testigo llamó a la policía!";
            until = Time.unscaledTime + Seconds;
        }

        private void Update()
        {
            var color = label.color;
            color.a = Mathf.Clamp01((until - Time.unscaledTime) / .6f);
            label.color = color;
        }
    }
}
