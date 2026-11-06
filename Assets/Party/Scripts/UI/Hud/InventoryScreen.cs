using System;
using UnityEngine;
using UnityEngine.UI;
using Alarma.Player.Items;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Inventario completo (Tab, GDD 8.2): la mochila en cuadrícula, la barra rápida debajo y la ficha del objeto elegido.
    // Clic en un objeto de la mochila y luego en un espacio de la barra para equiparlo; clic en un espacio de la barra
    // sin nada elegido lo devuelve a la mochila. Quien lo abre decide qué hacer con los controles (evento Toggled).
    public sealed class InventoryScreen : MonoBehaviour
    {
        private const int Columns = 5;
        private const float Cell = 104, Gap = 12;
        private static readonly string[] Categories = { "Arma", "Herramienta", "Consumible" };
        private static readonly string[] Tiers = { "Inicial", "Medio", "Avanzado" };
        [SerializeField] private PlayerInventory owner;
        private Inventory inventory;
        private ItemSlotWidget[] backpack, hotbar;
        private Text title, details, message;
        private RectTransform root;
        private int picked = -1;

        public event Action<bool> Toggled;
        public bool IsOpen => root != null && root.gameObject.activeSelf;

        public void Configure(PlayerInventory playerInventory) => owner = playerInventory;

        public void Toggle() { if (IsOpen) Close(); else Open(); }

        public void Open()
        {
            if (root == null || IsOpen) return;
            picked = -1;
            message.text = "";
            root.gameObject.SetActive(true);
            Refresh();
            Toggled?.Invoke(true);
        }

        public void Close()
        {
            if (!IsOpen) return;
            root.gameObject.SetActive(false);
            Toggled?.Invoke(false);
        }

        private void Start()
        {
            if (owner == null || owner.Inventory == null) { enabled = false; return; }
            inventory = owner.Inventory;
            var canvas = MapUi.Canvas("Inventario", transform, 60);
            root = MapUi.Place(MapUi.Rect("Pantalla", canvas.transform), Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            var dim = MapUi.Panel("Oscurecer", root, new Color(0, 0, 0, .6f));
            dim.raycastTarget = true;
            MapUi.Place(dim.rectTransform, Vector2.zero, Vector2.one, Vector2.zero, Vector2.zero);
            int rows = Mathf.CeilToInt(inventory.BackpackSize / (float)Columns);
            float gridWidth = Columns * Cell + (Columns - 1) * Gap, gridHeight = rows * Cell + (rows - 1) * Gap;
            var card = MapUi.Panel("Tarjeta", root, new Color(.09f, .11f, .14f, .97f)).rectTransform;
            card.anchorMin = card.anchorMax = new Vector2(.5f, .5f);
            card.sizeDelta = new Vector2(gridWidth + 480, gridHeight + 330);
            title = MapUi.Label("Título", card, "Inventario", 40, Color.white, TextAnchor.UpperLeft);
            MapUi.Place(title.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(40, -70), new Vector2(-40, -24));
            var help = MapUi.Label("Ayuda", card, "Clic en un objeto de la mochila y después en un espacio de la barra.  Clic en la barra: devolver a la mochila.  Tab: cerrar",
                20, new Color(1, 1, 1, .6f), TextAnchor.UpperLeft);
            MapUi.Place(help.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(40, -104), new Vector2(-40, -76));
            backpack = new ItemSlotWidget[inventory.BackpackSize];
            for (int i = 0; i < backpack.Length; i++)
            {
                int index = i;
                backpack[i] = CreateCell(card, "Mochila " + (i + 1), null, () => PickBackpack(index));
                backpack[i].Rect.anchoredPosition = new Vector2(40 + Cell / 2 + (i % Columns) * (Cell + Gap), -130 - Cell / 2 - (i / Columns) * (Cell + Gap));
            }
            var bar = MapUi.Label("Barra", card, "Barra rápida", 24, ItemSlotWidget.Accent, TextAnchor.LowerLeft);
            MapUi.Place(bar.rectTransform, new Vector2(0, 0), new Vector2(1, 0), new Vector2(40, Cell + 50), new Vector2(-40, Cell + 82));
            hotbar = new ItemSlotWidget[inventory.HotbarSize];
            for (int i = 0; i < hotbar.Length; i++)
            {
                int slot = i;
                hotbar[i] = CreateCell(card, "Barra " + (i + 1), (i + 1).ToString(), () => PickHotbar(slot));
                hotbar[i].Rect.anchorMin = hotbar[i].Rect.anchorMax = Vector2.zero;
                hotbar[i].Rect.anchoredPosition = new Vector2(40 + Cell / 2 + i * (Cell + Gap), 36 + Cell / 2);
            }
            details = MapUi.Label("Ficha", card, "", 24, Color.white, TextAnchor.UpperLeft);
            details.horizontalOverflow = HorizontalWrapMode.Wrap;
            MapUi.Place(details.rectTransform, new Vector2(1, 1), new Vector2(1, 1), new Vector2(-400, -130 - gridHeight), new Vector2(-40, -130));
            message = MapUi.Label("Aviso", card, "", 22, new Color(1f, .55f, .45f), TextAnchor.LowerRight);
            MapUi.Place(message.rectTransform, new Vector2(0, 0), new Vector2(1, 0), new Vector2(40, 40), new Vector2(-40, 80));
            root.gameObject.SetActive(false);
            inventory.Changed += Refresh;
        }

        private void OnDestroy()
        {
            if (inventory != null) inventory.Changed -= Refresh;
        }

        private static ItemSlotWidget CreateCell(RectTransform card, string name, string key, Action click)
        {
            var widget = new ItemSlotWidget(card, name, Cell, key, click);
            widget.Rect.anchorMin = widget.Rect.anchorMax = new Vector2(0, 1);
            return widget;
        }

        private void PickBackpack(int index)
        {
            message.text = "";
            picked = inventory.Backpack(index).IsEmpty ? -1 : index;
            Refresh();
        }

        private void PickHotbar(int slot)
        {
            if (picked >= 0)
            {
                var item = inventory.Backpack(picked).Item;
                if (inventory.Equip(picked, slot)) { picked = -1; message.text = ""; }
                else message.text = $"El espacio {slot + 1} es para: {inventory.SlotLabel(slot)}. {item.DisplayName} es {Categories[(int)item.Category].ToLowerInvariant()}.";
            }
            else if (!inventory.Hotbar(slot).IsEmpty && !inventory.Unequip(slot)) message.text = "La mochila está llena.";
            Refresh();
        }

        private void Refresh()
        {
            if (root == null || !IsOpen) return;
            for (int i = 0; i < backpack.Length; i++) backpack[i].Show(inventory.Backpack(i), "", i == picked);
            for (int i = 0; i < hotbar.Length; i++) hotbar[i].Show(inventory.Hotbar(i), inventory.SlotLabel(i), false);
            var item = picked >= 0 ? inventory.Backpack(picked).Item : inventory.SelectedStack.Item;
            details.text = item == null ? "Elige un objeto de la mochila." :
                $"<b>{item.DisplayName}</b>\n<color=#FFC733>{Categories[(int)item.Category]} · nivel {Tiers[(int)item.Tier].ToLowerInvariant()}</color>\n\n{item.Description}";
        }
    }
}
