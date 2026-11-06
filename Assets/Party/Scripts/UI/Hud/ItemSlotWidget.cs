using System;
using UnityEngine;
using UnityEngine.UI;
using Alarma.Player.Items;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Un espacio de inventario dibujado por código: marco, ícono, cantidad, número de tecla y el tipo que acepta si está vacío.
    // Lo usan la barra rápida y la pantalla de la mochila, así ambos se ven iguales.
    internal sealed class ItemSlotWidget
    {
        public static readonly Color Accent = new Color(1f, .78f, .2f);
        private static readonly Color Stowed = new Color(.62f, .52f, .3f, .95f);
        private static readonly Color Border = new Color(.3f, .34f, .4f, .95f), Fill = new Color(.07f, .09f, .12f, .88f);
        private readonly Image frame;
        private readonly RawImage icon;
        private readonly Text count, hint;

        public RectTransform Rect { get; }

        public ItemSlotWidget(Transform parent, string name, float size, string key, Action onClick)
        {
            Rect = MapUi.Rect(name, parent);
            Rect.sizeDelta = new Vector2(size, size);
            frame = Rect.gameObject.AddComponent<Image>();
            frame.color = Border;
            frame.raycastTarget = onClick != null;
            var inside = MapUi.Panel("Fondo", Rect, Fill).rectTransform;
            MapUi.Place(inside, Vector2.zero, Vector2.one, new Vector2(3, 3), new Vector2(-3, -3));
            icon = MapUi.Raw("Ícono", Rect, null, size);
            MapUi.Place(icon.rectTransform, Vector2.zero, Vector2.one, new Vector2(8, 8), new Vector2(-8, -8));
            hint = MapUi.Label("Tipo", Rect, "", Mathf.RoundToInt(size * .15f), new Color(1, 1, 1, .45f), TextAnchor.MiddleCenter);
            MapUi.Place(hint.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            count = MapUi.Label("Cantidad", Rect, "", Mathf.RoundToInt(size * .22f), Color.white, TextAnchor.LowerRight);
            MapUi.Place(count.rectTransform, Vector2.zero, Vector2.one, new Vector2(6, 4), new Vector2(-8, -4));
            if (!string.IsNullOrEmpty(key))
            {
                var number = MapUi.Label("Tecla", Rect, key, Mathf.RoundToInt(size * .2f), Accent, TextAnchor.UpperLeft);
                MapUi.Place(number.rectTransform, Vector2.zero, Vector2.one, new Vector2(8, 4), new Vector2(-4, -4));
            }
            if (onClick != null)
            {
                var button = Rect.gameObject.AddComponent<Button>();
                button.targetGraphic = frame;
                button.onClick.AddListener(() => onClick());
            }
        }

        // emptyLabel: lo que acepta el espacio cuando no tiene nada (en la barra rápida).
        // stowed: es el espacio elegido pero su objeto está guardado (se ve apagado).
        public void Show(ItemStack stack, string emptyLabel, bool highlighted, bool stowed = false)
        {
            icon.texture = stack.IsEmpty ? null : stack.Item.Icon;
            icon.enabled = icon.texture != null;
            count.text = stack.Count > 1 ? "x" + stack.Count : "";
            hint.text = stack.IsEmpty ? emptyLabel : (icon.enabled ? "" : stack.Item.DisplayName);
            frame.color = highlighted ? (stowed ? Stowed : Accent) : Border;
            icon.color = stowed ? new Color(1, 1, 1, .45f) : Color.white;
            Rect.localScale = Vector3.one * (highlighted && !stowed ? 1.08f : 1f);
        }
    }
}
