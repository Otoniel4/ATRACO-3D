using UnityEngine;
using UnityEngine.UI;
using Alarma.Core.Events;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Aviso arriba al centro de la respuesta policial: cuenta regresiva mientras viene, llegada y retirada. Solo
    // escucha el canal: no conoce a la central ni a los agentes.
    public sealed class PoliceAlertView : MonoBehaviour
    {
        private const float Seconds = 4f;
        [SerializeField] private PoliceResponseChannel response;
        private Text label;
        private float until;

        public void Configure(PoliceResponseChannel channel) => response = channel;

        private void Awake()
        {
            var canvas = MapUi.Canvas("Aviso de policía", transform, 36);
            label = MapUi.Label("Texto", canvas.transform, "", 30, new Color(.45f, .7f, 1f, 0f), TextAnchor.MiddleCenter);
            MapUi.Place(label.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, -230), new Vector2(0, -175));
        }

        private void OnEnable() { if (response != null) response.Raised += OnResponse; }
        private void OnDisable() { if (response != null) response.Raised -= OnResponse; }

        private void OnResponse(PoliceResponse state)
        {
            label.text = state.Phase == PoliceResponsePhase.OnTheWay ? "Policía en camino: " + state.SecondsToArrive + " s"
                       : state.Phase == PoliceResponsePhase.OnScene ? "¡Llegó la policía!" : "La policía se retiró";
            until = Time.unscaledTime + (state.Phase == PoliceResponsePhase.OnTheWay ? 1.6f : Seconds);
        }

        private void Update()
        {
            var color = label.color;
            color.a = Mathf.Clamp01((until - Time.unscaledTime) / .6f);
            label.color = color;
        }
    }
}
