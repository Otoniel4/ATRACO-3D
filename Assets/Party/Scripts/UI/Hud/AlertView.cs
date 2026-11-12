using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Alarma.Core.Events;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Medidor de sospecha arriba al centro (Task 15): barra que se llena mientras una cámara ve al jugador armado y
    // nombre del nivel de alerta del local. Solo escucha AlertChannel; si varios locales avisan, muestra el más grave.
    public sealed class AlertView : MonoBehaviour
    {
        private const float Width = 320f;
        private static readonly Color Wary = new Color(1f, .85f, .25f), Danger = new Color(1f, .3f, .25f), Police = new Color(.45f, .7f, 1f);
        [SerializeField] private AlertChannel alerts;
        private readonly Dictionary<GameObject, AlertStatus> places = new Dictionary<GameObject, AlertStatus>();
        private Canvas canvas;
        private RectTransform fill;
        private Image fillImage;
        private Text label;

        public void Configure(AlertChannel channel) => alerts = channel;

        private void Awake()
        {
            canvas = MapUi.Canvas("Alerta del local", transform, 35);
            label = MapUi.Label("Nivel", canvas.transform, "", 26, Wary, TextAnchor.MiddleCenter);
            MapUi.Place(label.rectTransform, new Vector2(.5f, 1), new Vector2(.5f, 1), new Vector2(-Width, -62), new Vector2(Width, -28));
            var back = MapUi.Panel("Fondo", canvas.transform, new Color(0f, 0f, 0f, .55f));
            MapUi.Place(back.rectTransform, new Vector2(.5f, 1), new Vector2(.5f, 1), new Vector2(-Width / 2f - 4, -92), new Vector2(Width / 2f + 4, -66));
            fillImage = MapUi.Panel("Sospecha", back.transform, Wary);
            fill = fillImage.rectTransform;
            MapUi.Place(fill, Vector2.zero, new Vector2(0, 1), new Vector2(4, 4), new Vector2(4, -4));
            canvas.enabled = false;
        }

        private void OnEnable() { if (alerts != null) alerts.Raised += OnAlert; }
        private void OnDisable() { if (alerts != null) alerts.Raised -= OnAlert; }

        private void OnAlert(AlertStatus status)
        {
            if (status.Level == AlertLevel.Stealth && status.Suspicion <= 0f) places.Remove(status.Place);
            else places[status.Place] = status;
            Show();
        }

        private void Show()
        {
            canvas.enabled = places.Count > 0;
            if (places.Count == 0) return;
            var worst = default(AlertStatus);
            foreach (var status in places.Values)
                if (status.Level > worst.Level || (status.Level == worst.Level && status.Suspicion >= worst.Suspicion)) worst = status;
            fill.offsetMax = new Vector2(4 + Width * Mathf.Clamp01(worst.Suspicion), -4);
            Color color = worst.Level >= AlertLevel.PoliceOnTheWay ? Police : worst.Level == AlertLevel.Alarm ? Danger : Color.Lerp(Wary, Danger, worst.Suspicion);
            fillImage.color = color;
            label.color = color;
            label.text = worst.Level == AlertLevel.Alarm ? "¡ALARMA!"
                       : worst.Level == AlertLevel.PoliceOnTheWay ? "POLICÍA EN CAMINO"
                       : worst.Level == AlertLevel.Assault ? "ASALTO POLICIAL" : "SOSPECHA";
        }
    }
}
