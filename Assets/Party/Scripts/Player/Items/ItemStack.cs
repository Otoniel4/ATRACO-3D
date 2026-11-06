using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Lo que ocupa un espacio: un objeto y cuántos hay. Vacío si no hay objeto.
    [Serializable]
    public struct ItemStack
    {
        [SerializeField] private ItemDefinition item;
        [SerializeField, Min(0)] private int count;

        public ItemStack(ItemDefinition definition, int amount) { item = definition; count = definition != null ? Mathf.Max(1, amount) : 0; }

        public static ItemStack Empty => default;
        public ItemDefinition Item => item;
        public int Count => item != null ? Mathf.Max(1, count) : 0;
        public bool IsEmpty => item == null;
    }
}
