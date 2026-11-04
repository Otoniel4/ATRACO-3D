using System;
using UnityEngine;
using UnityEngine.UI;
using Alarma.UI.Map;

namespace Alarma.UI.Pause
{
    // Botones y barras del menú creados por código, con el mismo estilo que el mapa.
    internal static class MenuUi
    {
        public static readonly Color Accent = new Color(1f, .78f, .2f);
        public static readonly Color Card = new Color(.09f, .11f, .14f, .97f);
        private static readonly Color Normal = new Color(.17f, .2f, .25f), Hover = new Color(.27f, .31f, .38f);
        public const float Row = 72f;

        // Fila que ocupa todo el ancho de la tarjeta a la altura y (desde arriba).
        public static RectTransform RowAt(Transform parent, string name, float y, float height = 60f)
            => MapUi.Place(MapUi.Rect(name, parent), new Vector2(0, 1), new Vector2(1, 1), new Vector2(48, -y - height), new Vector2(-48, -y));

        public static Button Button(Transform parent, string label, float y, Action onClick, out Text text)
        {
            var r = RowAt(parent, "Botón " + label, y);
            var image = r.gameObject.AddComponent<Image>();
            var button = r.gameObject.AddComponent<Button>();
            button.targetGraphic = image;
            var colors = button.colors;
            colors.normalColor = Normal; colors.highlightedColor = Hover; colors.selectedColor = Normal; colors.pressedColor = Accent * .85f;
            button.colors = colors;
            text = MapUi.Label("Texto", r, label, 28, Color.white, TextAnchor.MiddleCenter);
            MapUi.Place(text.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            button.onClick.AddListener(() => onClick());
            return button;
        }

        public static Button Button(Transform parent, string label, float y, Action onClick) => Button(parent, label, y, onClick, out _);

        public static Slider Slider(Transform parent, string label, float y, float min, float max, Action<float> changed, Func<float, string> format)
        {
            var r = RowAt(parent, "Ajuste " + label, y);
            var title = MapUi.Label("Nombre", r, label, 26, Color.white, TextAnchor.MiddleLeft);
            MapUi.Place(title.rectTransform, Vector2.zero, new Vector2(.42f, 1), Vector2.zero, Vector2.zero);
            var value = MapUi.Label("Valor", r, "", 26, Accent, TextAnchor.MiddleRight);
            MapUi.Place(value.rectTransform, new Vector2(.86f, 0), Vector2.one, Vector2.zero, Vector2.zero);
            var bar = MapUi.Place(MapUi.Rect("Barra", r), new Vector2(.44f, .5f), new Vector2(.84f, .5f), new Vector2(0, -9), new Vector2(0, 9));
            var back = MapUi.Panel("Fondo", bar, Normal); back.raycastTarget = true;
            MapUi.Place(back.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var fillArea = MapUi.Place(MapUi.Rect("Zona de relleno", bar), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var fill = MapUi.Panel("Relleno", fillArea, Accent);
            MapUi.Place(fill.rectTransform, Vector2.zero, new Vector2(0, 1), Vector2.zero, Vector2.zero);
            var handleArea = MapUi.Place(MapUi.Rect("Zona del tirador", bar), Vector2.zero, Vector2.one, new Vector2(12, 0), new Vector2(-12, 0));
            var handle = MapUi.Panel("Tirador", handleArea, Color.white); handle.raycastTarget = true;
            MapUi.Place(handle.rectTransform, Vector2.zero, new Vector2(0, 1), new Vector2(-12, -10), new Vector2(12, 10));
            var slider = bar.gameObject.AddComponent<Slider>();
            slider.fillRect = fill.rectTransform; slider.handleRect = handle.rectTransform; slider.targetGraphic = handle;
            slider.minValue = min; slider.maxValue = max;
            slider.onValueChanged.AddListener(v => { value.text = format(v); changed(v); });
            return slider;
        }
    }
}
