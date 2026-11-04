using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace Alarma.UI.Map
{
    // Mapa a pantalla completa: marcas por categoría, leyenda, zoom con la rueda, arrastre para moverse
    // y la flecha del jugador en tiempo real. Al hacer clic en un lugar avisa con PlaceSelected; quien escucha decide qué hacer.
    public sealed class CityMapScreen : MonoBehaviour
    {
        private const float MinZoom = 1, MaxZoom = 6, IconSize = 30, ArrowSize = 34, LegendWidth = 360;
        [SerializeField] private CityMapDefinition map;
        [SerializeField] private Transform tracked;
        private readonly List<(MapPlace place, RectTransform icon)> icons = new List<(MapPlace, RectTransform)>();
        private RectTransform root, viewport, content, arrow;
        private Text tooltip;
        private float zoom = 1;
        private Vector2 pan, pressPoint, lastMouse;
        private bool dragging;
        private MapPlace pressed;

        public event Action<MapPlace> PlaceSelected;
        public event Action<bool> Toggled;
        public bool IsOpen => root != null && root.gameObject.activeSelf;

        public void Configure(CityMapDefinition definition, Transform subject)
        {
            map = definition;
            tracked = subject;
        }

        private void Start()
        {
            Build();
            root.gameObject.SetActive(false);
        }

        public void Toggle()
        {
            if (IsOpen) Close();
            else Open();
        }

        public void Open()
        {
            root.gameObject.SetActive(true);
            zoom = 2;
            Center();
            Toggled?.Invoke(true);
        }

        public void Close()
        {
            root.gameObject.SetActive(false);
            Toggled?.Invoke(false);
        }

        private void Build()
        {
            var canvas = MapUi.Canvas("Mapa de la ciudad", transform, 60);
            root = MapUi.Place(MapUi.Rect("Pantalla", canvas.transform), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            MapUi.Place(MapUi.Panel("Fondo", root, new Color(.04f, .06f, .08f, .94f)).rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var title = MapUi.Label("Título", root, map.Title.ToUpperInvariant(), 34, new Color(1, .82f, .25f), TextAnchor.MiddleLeft);
            MapUi.Place(title.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(32, -62), new Vector2(-LegendWidth, -12));
            var help = MapUi.Label("Ayuda", root, "M: cerrar  ·  Rueda: zoom  ·  Arrastrar: mover  ·  Clic en un lugar: ir", 18, new Color(.8f, .84f, .88f), TextAnchor.MiddleRight);
            MapUi.Place(help.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(32, -62), new Vector2(-LegendWidth - 24, -12));

            viewport = MapUi.Place(MapUi.Rect("Vista", root), Vector2.zero, Vector2.one, new Vector2(24, 24), new Vector2(-LegendWidth, -72));
            viewport.gameObject.AddComponent<RectMask2D>();
            MapUi.Place(MapUi.Panel("Marco", viewport, new Color(.08f, .11f, .14f)).rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            content = MapUi.Rect("Plano", viewport);
            content.anchorMin = content.anchorMax = new Vector2(.5f, .5f);
            content.gameObject.AddComponent<RawImage>().texture = map.Background;
            content.GetComponent<RawImage>().raycastTarget = false;
            foreach (var place in map.Places)
            {
                var category = map.Category(place.Category);
                if (category == null) continue;
                var icon = MapUi.Raw(place.Name, content, category.Icon, IconSize).rectTransform;
                icon.anchorMin = icon.anchorMax = map.Normalized(place.Position);
                icons.Add((place, icon));
            }
            arrow = MapUi.Raw("Tú", content, map.PlayerIcon, ArrowSize).rectTransform;
            tooltip = MapUi.Label("Nombre", root, "", 20, Color.white, TextAnchor.MiddleLeft);
            tooltip.rectTransform.pivot = new Vector2(0, .5f);
            BuildLegend();
        }

        private void BuildLegend()
        {
            var panel = MapUi.Place(MapUi.Panel("Leyenda", root, new Color(.07f, .09f, .12f, .96f)).rectTransform,
                new Vector2(1, 0), new Vector2(1, 1), new Vector2(-LegendWidth + 12, 24), new Vector2(-24, -24));
            float y = -24;
            string group = null;
            foreach (var category in map.Categories)
            {
                int count = Array.FindAll(map.Places, p => p.Category == category.Id).Length;
                if (count == 0) continue;
                if (category.Group != group)
                {
                    group = category.Group;
                    y -= 10;
                    var header = MapUi.Label(group, panel, group, 16, new Color(.6f, .65f, .7f), TextAnchor.MiddleLeft);
                    MapUi.Place(header.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(20, y - 22), new Vector2(-12, y));
                    y -= 30;
                }
                var icon = MapUi.Raw(category.Id, panel, category.Icon, 28).rectTransform;
                icon.anchorMin = icon.anchorMax = new Vector2(0, 1);
                icon.anchoredPosition = new Vector2(36, y - 16);
                var label = MapUi.Label(category.Label, panel, category.Label + (count > 1 ? "  ×" + count : ""), 19, new Color(.93f, .95f, .97f), TextAnchor.MiddleLeft);
                MapUi.Place(label.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(60, y - 32), new Vector2(-12, y));
                y -= 38;
            }
            y -= 12;
            var you = MapUi.Raw("Tú", panel, map.PlayerIcon, 28).rectTransform;
            you.anchorMin = you.anchorMax = new Vector2(0, 1);
            you.anchoredPosition = new Vector2(36, y - 16);
            MapUi.Place(MapUi.Label("Tú", panel, "Tú (apunta hacia donde vas)", 19, Color.white, TextAnchor.MiddleLeft).rectTransform,
                new Vector2(0, 1), new Vector2(1, 1), new Vector2(60, y - 32), new Vector2(-12, y));
        }

        private void Update()
        {
            if (!IsOpen) return;
            var mouse = Mouse.current;
            if (mouse != null) HandleMouse(mouse);
            Layout();
        }

        private void HandleMouse(Mouse mouse)
        {
            Vector2 point = mouse.position.ReadValue();
            float scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) > .01f && RectTransformUtility.RectangleContainsScreenPoint(viewport, point, null)) ZoomAt(point, scroll > 0 ? 1.2f : 1 / 1.2f);
            if (mouse.leftButton.wasPressedThisFrame)
            {
                pressPoint = lastMouse = point;
                dragging = false;
                pressed = PlaceAt(point);
            }
            if (mouse.leftButton.isPressed)
            {
                if ((point - pressPoint).sqrMagnitude > 64) dragging = true;
                if (dragging) pan += (point - lastMouse) / root.lossyScale.x;
            }
            if (mouse.leftButton.wasReleasedThisFrame && !dragging && pressed != null && pressed == PlaceAt(point)) PlaceSelected?.Invoke(pressed);
            lastMouse = point;
            ShowTooltip(PlaceAt(point), point);
        }

        private void ZoomAt(Vector2 screen, float factor)
        {
            RectTransformUtility.ScreenPointToLocalPointInRectangle(viewport, screen, null, out Vector2 local);
            float before = Side();
            zoom = Mathf.Clamp(zoom * factor, MinZoom, MaxZoom);
            // El punto bajo el cursor se queda donde estaba.
            pan = local - (local - pan) * (Side() / before);
        }

        private float Side() => Mathf.Min(viewport.rect.width, viewport.rect.height) * zoom;

        private void Center()
        {
            if (tracked == null) return;
            Canvas.ForceUpdateCanvases();
            pan = -(map.Normalized(tracked.position) - new Vector2(.5f, .5f)) * Side();
        }

        private void Layout()
        {
            float side = Side();
            Vector2 slack = new Vector2(Mathf.Max(0, (side - viewport.rect.width) * .5f), Mathf.Max(0, (side - viewport.rect.height) * .5f));
            pan = new Vector2(Mathf.Clamp(pan.x, -slack.x, slack.x), Mathf.Clamp(pan.y, -slack.y, slack.y));
            content.sizeDelta = new Vector2(side, side);
            content.anchoredPosition = pan;
            if (tracked == null) return;
            arrow.anchorMin = arrow.anchorMax = map.Normalized(tracked.position);
            arrow.localEulerAngles = new Vector3(0, 0, -tracked.eulerAngles.y);
            arrow.SetAsLastSibling();
        }

        private MapPlace PlaceAt(Vector2 screen)
        {
            foreach (var (place, icon) in icons)
                if (RectTransformUtility.RectangleContainsScreenPoint(icon, screen, null)) return place;
            return null;
        }

        private void ShowTooltip(MapPlace place, Vector2 screen)
        {
            tooltip.enabled = place != null;
            if (place == null) return;
            var category = map.Category(place.Category);
            float distance = tracked != null ? Vector2.Distance(new Vector2(tracked.position.x, tracked.position.z), new Vector2(place.Position.x, place.Position.z)) : 0;
            tooltip.text = place.Name + "\n" + category.Label + " · " + Mathf.RoundToInt(distance) + " m";
            RectTransformUtility.ScreenPointToLocalPointInRectangle(root, screen, null, out Vector2 local);
            tooltip.rectTransform.anchoredPosition = local + new Vector2(24, 0);
        }
    }
}
