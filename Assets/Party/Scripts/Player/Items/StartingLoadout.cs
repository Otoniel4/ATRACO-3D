using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Equipo con el que empieza el jugador: lo que va a la mochila y qué se coloca en cada espacio de la barra rápida.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Equipo inicial", fileName = "StartingLoadout")]
    public sealed class StartingLoadout : ScriptableObject
    {
        [SerializeField] private ItemStack[] backpack = Array.Empty<ItemStack>();
        [SerializeField, Tooltip("Objeto de cada espacio de la barra (1 a 5); debe estar también en la mochila.")]
        private ItemDefinition[] hotbar = Array.Empty<ItemDefinition>();

        public void Configure(ItemStack[] items, ItemDefinition[] quick) { backpack = items; hotbar = quick; }

        public void ApplyTo(Inventory inventory)
        {
            foreach (var stack in backpack)
                if (!stack.IsEmpty) inventory.Add(stack.Item, stack.Count);
            for (int slot = 0; slot < hotbar.Length && slot < inventory.HotbarSize; slot++)
            {
                int index = inventory.FindInBackpack(hotbar[slot]);
                if (index >= 0) inventory.Equip(index, slot);
            }
        }
    }
}
