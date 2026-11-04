using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Alarma.UI.Map
{
    // Minimapa en la esquina: muestra el entorno del jugador con el norte arriba y la flecha girando hacia donde va.
    public sealed class CityMinimap : MonoBehaviour
    {
        private const float Size = 270, IconSize = 26, ArrowSize = 30;
        [SerializeField] private CityMapDefinition map;
        [SerializeField] private Transform tracked;
        [SerializeField, Min(50), Tooltip("Metros visibles desde el jugador hasta el borde.")] private float radius = 220;
        private readonly List<(MapPlace place, RectTransform icon)> icons = new List<(MapPlace, RectTransform)>();
        private RectTransform view, arrow;
        private RawImage ground;
        private GameObject root;

        public void Configure(CityMapDefinition definition, Transform subject)
        {
            map = definition;
            tracked = subject;
        }

        public void SetVisible(bool visible)
        {
            if (root != null) root.SetActive(visible);
        }

        private void Start()
        {
            var canvas = MapUi.Canvas("Minimapa", transform, 40);
            root = canvas.gameObject;
            var frame = MapUi.Panel("Marco", canvas.transform, new Color(.04f, .06f, .08f, .9f)).rectTransform;
            frame.anchorMin = frame.anchorMax = frame.pivot = Vector2.zero;
            frame.anchoredPosition = new Vector2(24, 24);
            frame.sizeDelta = new Vector2(Size + 10, Size + 10);
            view = MapUi.Place(MapUi.Rect("Vista", frame), Vector2.zero, Vector2.one, new Vector2(5, 5), new Vector2(-5, -5));
            view.gameObject.AddComponent<RectMask2D>();
            ground = MapUi.Raw("Plano", view, map.Background, Size);
            MapUi.Place(ground.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            foreach (var place in map.Places)
            {
                var category = map.Category(place.Category);
                if (category == null) continue;
                var icon = MapUi.Raw(place.Name, view, category.Icon, IconSize).rectTransform;
                icon.anchorMin = icon.anchorMax = Vector2.zero;
                icons.Add((place, icon));
            }
            arrow = MapUi.Raw("Tú", view, map.PlayerIcon, ArrowSize).rectTransform;
            arrow.anchorMin = arrow.anchorMax = new Vector2(.5f, .5f);
            var north = MapUi.Label("Norte", frame, "N", 22, new Color(1, .82f, .25f), TextAnchor.MiddleCenter);
            north.rectTransform.anchorMin = north.rectTransform.anchorMax = new Vector2(.5f, 1);
            north.rectTransform.anchoredPosition = new Vector2(0, -18);
        }

        private void LateUpdate()
        {
            if (tracked == null || ground == null || !root.activeSelf) return;
            Vector2 center = map.Normalized(tracked.position);
            float span = 2 * radius / map.WorldSize;
            ground.uvRect = new Rect(center.x - span / 2, center.y - span / 2, span, span);
            float side = view.rect.width;
            foreach (var (place, icon) in icons)
            {
                Vector2 local = (map.Normalized(place.Position) - center) / span;
                bool inside = Mathf.Abs(local.x) < .48f && Mathf.Abs(local.y) < .48f;
                icon.gameObject.SetActive(inside);
                if (inside) icon.anchoredPosition = (local + new Vector2(.5f, .5f)) * side;
            }
            arrow.localEulerAngles = new Vector3(0, 0, -tracked.eulerAngles.y);
            arrow.SetAsLastSibling();
        }
    }
}
