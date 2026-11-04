using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;
using Alarma.Core.Settings;
using Alarma.UI.Map;

namespace Alarma.UI.Pause
{
    // Menú de ESC: continuar, opciones, controles y salir. No congela el juego (será online): solo cubre la pantalla.
    // Quien lo abre decide qué hacer con los controles y el cursor a través del evento Toggled.
    public sealed class PauseMenuScreen : MonoBehaviour
    {
        private const float CardHeight = 640f;
        private static readonly (string key, string action)[] Controls =
        {
            ("W A S D", "Moverse"), ("Shift", "Correr"), ("Ratón", "Mirar alrededor"), ("E", "Abrir puertas"), ("M", "Mapa de la ciudad"), ("Esc", "Este menú")
        };

        [SerializeField] private GameSettings settings;
        private RectTransform root, main, options, controls;
        private Slider volume, sensitivity;
        private Text fullscreen, quality;

        public event Action<bool> Toggled;
        public event Action QuitRequested;
        public bool IsOpen => root != null && root.gameObject.activeSelf;

        public void Configure(GameSettings gameSettings) => settings = gameSettings;

        private void Awake()
        {
            EnsureEventSystem();
            Build();
            root.gameObject.SetActive(false);
        }

        public void Toggle() { if (IsOpen) Close(); else Open(); }

        public void Open()
        {
            if (IsOpen) return;
            root.gameObject.SetActive(true);
            Show(main);
            Toggled?.Invoke(true);
        }

        public void Close()
        {
            if (!IsOpen) return;
            root.gameObject.SetActive(false);
            Toggled?.Invoke(false);
        }

        // Los botones y barras necesitan un EventSystem con el módulo del Input System.
        private void EnsureEventSystem()
        {
            if (EventSystem.current != null) return;
            var go = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
            go.transform.SetParent(transform, false);
            go.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        }

        private void Build()
        {
            var canvas = MapUi.Canvas("Menú de pausa", transform, 50);
            canvas.gameObject.AddComponent<GraphicRaycaster>();
            var shade = MapUi.Panel("Fondo", canvas.transform, new Color(0, 0, 0, .55f));
            shade.raycastTarget = true; // el juego de detrás no recibe clics
            root = MapUi.Place(shade.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var card = MapUi.Panel("Tarjeta", root, MenuUi.Card).rectTransform;
            MapUi.Place(card, new Vector2(.5f, .5f), new Vector2(.5f, .5f), new Vector2(-330, -CardHeight / 2), new Vector2(330, CardHeight / 2));
            var accent = MapUi.Panel("Franja", card, MenuUi.Accent).rectTransform;
            MapUi.Place(accent, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, -6), Vector2.zero);
            main = Page(card, "PAUSA");
            MenuUi.Button(main, "Continuar", 120, Close);
            MenuUi.Button(main, "Opciones", 120 + MenuUi.Row, () => { Refresh(); Show(options); });
            MenuUi.Button(main, "Controles", 120 + MenuUi.Row * 2, () => Show(controls));
            MenuUi.Button(main, "Salir del juego", 120 + MenuUi.Row * 4, () => QuitRequested?.Invoke());
            options = Page(card, "OPCIONES");
            volume = MenuUi.Slider(options, "Volumen", 120, 0f, 1f, v => settings.SetVolume(v), v => Mathf.RoundToInt(v * 100) + " %");
            sensitivity = MenuUi.Slider(options, "Sensibilidad", 120 + MenuUi.Row, GameSettings.MinSensitivity, GameSettings.MaxSensitivity, v => settings.SetMouseSensitivity(v), v => v.ToString("0.0") + "×");
            MenuUi.Button(options, "", 120 + MenuUi.Row * 2, () => { settings.SetFullscreen(!settings.Fullscreen); Refresh(); }, out fullscreen);
            MenuUi.Button(options, "", 120 + MenuUi.Row * 3, () => { settings.SetQuality(settings.Quality + 1); Refresh(); }, out quality);
            MenuUi.Button(options, "Volver", CardHeight - 100, () => Show(main));
            controls = Page(card, "CONTROLES");
            for (int i = 0; i < Controls.Length; i++)
            {
                var row = MenuUi.RowAt(controls, "Control " + Controls[i].key, 120 + i * 58, 50);
                MapUi.Place(MapUi.Label("Tecla", row, Controls[i].key, 26, MenuUi.Accent, TextAnchor.MiddleLeft).rectTransform, Vector2.zero, new Vector2(.4f, 1), Vector2.zero, Vector2.zero);
                MapUi.Place(MapUi.Label("Acción", row, Controls[i].action, 26, Color.white, TextAnchor.MiddleLeft).rectTransform, new Vector2(.4f, 0), Vector2.one, Vector2.zero, Vector2.zero);
            }
            MenuUi.Button(controls, "Volver", CardHeight - 100, () => Show(main));
        }

        private static RectTransform Page(RectTransform card, string title)
        {
            var page = MapUi.Place(MapUi.Rect("Página " + title, card), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var label = MapUi.Label("Título", page, title, 44, MenuUi.Accent, TextAnchor.MiddleCenter);
            MapUi.Place(label.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, -96), new Vector2(0, -26));
            return page;
        }

        private void Show(RectTransform page)
        {
            main.gameObject.SetActive(page == main);
            options.gameObject.SetActive(page == options);
            controls.gameObject.SetActive(page == controls);
        }

        private void Refresh()
        {
            settings.EnsureLoaded();
            // Se fuerza el aviso para que el número junto a cada barra siempre se vea.
            volume.SetValueWithoutNotify(settings.Volume); volume.onValueChanged.Invoke(settings.Volume);
            sensitivity.SetValueWithoutNotify(settings.MouseSensitivity); sensitivity.onValueChanged.Invoke(settings.MouseSensitivity);
            fullscreen.text = "Pantalla completa: " + (settings.Fullscreen ? "sí" : "no");
            quality.text = "Calidad: " + QualitySettings.names[settings.Quality];
        }
    }
}
