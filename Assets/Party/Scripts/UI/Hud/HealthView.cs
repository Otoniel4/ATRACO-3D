using UnityEngine;
using UnityEngine.UI;
using Alarma.Player.Health;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Barra de vida abajo a la izquierda y aviso al centro cuando el jugador está derribado o arrestado. Solo escucha
    // a PlayerHealth: no decide nada.
    public sealed class HealthView : MonoBehaviour
    {
        private const float Width = 300f;
        [SerializeField] private PlayerHealth health;
        private RectTransform fill;
        private Image fillImage;
        private Text status;

        public void Configure(PlayerHealth playerHealth) => health = playerHealth;

        private void Awake()
        {
            var canvas = MapUi.Canvas("Vida", transform, 34);
            var back = MapUi.Panel("Fondo", canvas.transform, new Color(0f, 0f, 0f, .55f));
            MapUi.Place(back.rectTransform, Vector2.zero, Vector2.zero, new Vector2(40, 40), new Vector2(40 + Width + 8, 72));
            fillImage = MapUi.Panel("Vida", back.transform, new Color(.3f, .85f, .4f));
            fill = fillImage.rectTransform;
            MapUi.Place(fill, Vector2.zero, new Vector2(0, 1), new Vector2(4, 4), new Vector2(4 + Width, -4));
            status = MapUi.Label("Estado", canvas.transform, "", 40, new Color(1f, .35f, .3f), TextAnchor.MiddleCenter);
            MapUi.Place(status.rectTransform, new Vector2(0, .5f), new Vector2(1, .5f), new Vector2(0, 60), new Vector2(0, 130));
        }

        private void OnEnable() { if (health != null) health.HealthChanged += Show; }
        private void OnDisable() { if (health != null) health.HealthChanged -= Show; }
        private void Start() { if (health != null) Show(health.Normalized); }

        private void Show(float normalized)
        {
            fill.offsetMax = new Vector2(4 + Width * Mathf.Clamp01(normalized), -4);
            fillImage.color = normalized > .35f ? new Color(.3f, .85f, .4f) : new Color(.9f, .3f, .25f);
        }

        private void Update()
        {
            if (health == null) return;
            int seconds = Mathf.CeilToInt(health.SecondsLeft);
            status.text = health.State == LifeState.Downed ? "DERRIBADO — te levantas en " + seconds + " s"
                        : health.State == LifeState.Arrested ? "ARRESTADO — vuelves al escondite en " + seconds + " s" : "";
        }
    }
}
