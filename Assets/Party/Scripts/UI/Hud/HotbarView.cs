using UnityEngine;
using UnityEngine.UI;
using Alarma.Player.Items;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Barra rápida abajo al centro (GDD: HUD inferior): 5 espacios con su tecla, el elegido resaltado y su nombre encima,
    // que se desvanece a los pocos segundos. Solo muestra el inventario; elegir con 1–5 lo hace quien lee los controles.
    public sealed class HotbarView : MonoBehaviour
    {
        private const float SlotSize = 92, Gap = 10, NameSeconds = 2.2f;
        [SerializeField] private PlayerInventory owner;
        [SerializeField, Tooltip("Muestra los avisos de las herramientas (por ejemplo, «No hay nada que forzar»).")] private ItemUser user;
        private Inventory inventory;
        private ItemSlotWidget[] slots;
        private Text itemName;
        private GameObject root;
        private float nameUntil;

        public void Configure(PlayerInventory playerInventory, ItemUser itemUser) { owner = playerInventory; user = itemUser; }

        public void SetVisible(bool visible)
        {
            if (root != null) root.SetActive(visible);
        }

        private void Start()
        {
            if (owner == null || owner.Inventory == null) { enabled = false; return; }
            inventory = owner.Inventory;
            var canvas = MapUi.Canvas("Barra rápida", transform, 35);
            root = canvas.gameObject;
            int count = inventory.HotbarSize;
            float width = count * SlotSize + (count - 1) * Gap;
            var bar = MapUi.Rect("Espacios", canvas.transform);
            bar.anchorMin = bar.anchorMax = new Vector2(.5f, 0);
            bar.pivot = new Vector2(.5f, 0);
            bar.anchoredPosition = new Vector2(0, 26);
            bar.sizeDelta = new Vector2(width, SlotSize);
            slots = new ItemSlotWidget[count];
            for (int i = 0; i < count; i++)
            {
                slots[i] = new ItemSlotWidget(bar, "Espacio " + (i + 1), SlotSize, (i + 1).ToString(), null);
                slots[i].Rect.anchorMin = slots[i].Rect.anchorMax = new Vector2(0, .5f);
                slots[i].Rect.anchoredPosition = new Vector2(SlotSize / 2 + i * (SlotSize + Gap), 0);
            }
            itemName = MapUi.Label("Nombre", bar, "", 26, Color.white, TextAnchor.LowerCenter);
            MapUi.Place(itemName.rectTransform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, 12), new Vector2(0, 50));
            inventory.Changed += Refresh;
            inventory.SelectionChanged += OnSelected;
            if (user != null) user.Feedback += ShowMessage;
            Refresh();
        }

        private void ShowMessage(string message)
        {
            itemName.text = message;
            nameUntil = Time.unscaledTime + NameSeconds;
        }

        private void OnDestroy()
        {
            if (inventory == null) return;
            inventory.Changed -= Refresh;
            inventory.SelectionChanged -= OnSelected;
            if (user != null) user.Feedback -= ShowMessage;
        }

        private void OnSelected(int slot)
        {
            Refresh();
            var stack = inventory.Hotbar(slot);
            itemName.text = stack.IsEmpty ? inventory.SlotLabel(slot) + " (vacío)" : stack.Item.DisplayName + (inventory.Holstered ? " (guardada)" : "");
            nameUntil = Time.unscaledTime + NameSeconds;
        }

        private void Refresh()
        {
            for (int i = 0; i < slots.Length; i++) slots[i].Show(inventory.Hotbar(i), inventory.SlotLabel(i), i == inventory.Selected, inventory.Holstered);
        }

        private void Update()
        {
            if (itemName == null) return;
            float left = nameUntil - Time.unscaledTime;
            itemName.color = new Color(1, 1, 1, Mathf.Clamp01(left / .5f));
        }
    }
}
