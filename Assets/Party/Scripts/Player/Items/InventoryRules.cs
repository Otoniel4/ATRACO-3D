using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Reglas de la barra rápida y tamaño de la mochila (GDD 8.2): 1 arma, 2 herramientas, 1 consumible y 1 espacio libre.
    // Cambiar las reglas es editar este asset, no el código.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Reglas", fileName = "InventoryRules")]
    public sealed class InventoryRules : ScriptableObject
    {
        [Serializable]
        public struct SlotRule
        {
            [Tooltip("Acepta cualquier tipo de objeto.")] public bool any;
            public ItemCategory category;
            [Tooltip("Lo que se muestra en el espacio vacío.")] public string label;
        }

        [SerializeField] private SlotRule[] hotbar =
        {
            new SlotRule { category = ItemCategory.Weapon, label = "Arma" },
            new SlotRule { category = ItemCategory.Tool, label = "Herramienta" },
            new SlotRule { category = ItemCategory.Tool, label = "Herramienta" },
            new SlotRule { category = ItemCategory.Consumable, label = "Consumible" },
            new SlotRule { any = true, label = "Libre" },
        };
        [SerializeField, Min(1)] private int backpackSize = 20;

        public int HotbarSize => hotbar.Length;
        public int BackpackSize => backpackSize;
        public string Label(int slot) => hotbar[slot].label;
        public bool Accepts(int slot, ItemCategory category) => hotbar[slot].any || hotbar[slot].category == category;
    }
}
