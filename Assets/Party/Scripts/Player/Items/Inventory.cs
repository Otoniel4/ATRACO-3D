using System;

namespace Alarma.Player.Items
{
    // Inventario sin dependencias de escena: barra rápida con reglas por espacio, mochila y espacio elegido.
    // Solo guarda estado y avisa cambios; la vista, la mano y (más adelante) la red escuchan sus eventos.
    public sealed class Inventory
    {
        private readonly InventoryRules rules;
        private readonly ItemStack[] hotbar, backpack;

        public event Action Changed;
        public event Action<int> SelectionChanged;

        public Inventory(InventoryRules slotRules)
        {
            rules = slotRules ?? throw new ArgumentNullException(nameof(slotRules));
            hotbar = new ItemStack[rules.HotbarSize];
            backpack = new ItemStack[rules.BackpackSize];
        }

        public int HotbarSize => hotbar.Length;
        public int BackpackSize => backpack.Length;
        public int Selected { get; private set; }
        public ItemStack SelectedStack => hotbar[Selected];
        // Guardado: el espacio sigue elegido pero el objeto no está en la mano (manos libres).
        public bool Holstered { get; private set; }
        public ItemStack ActiveStack => Holstered ? ItemStack.Empty : hotbar[Selected];
        public ItemStack Hotbar(int slot) => hotbar[slot];
        public ItemStack Backpack(int index) => backpack[index];
        public string SlotLabel(int slot) => rules.Label(slot);
        public bool Accepts(int slot, ItemDefinition item) => item == null || rules.Accepts(slot, item.Category);

        // Guarda en la mochila: primero completa pilas del mismo objeto y luego usa espacios vacíos. Devuelve lo que no cupo.
        public int Add(ItemDefinition item, int count)
        {
            if (item == null || count <= 0) return 0;
            for (int i = 0; i < backpack.Length && count > 0; i++)
                if (backpack[i].Item == item && backpack[i].Count < item.MaxStack)
                {
                    int moved = Math.Min(count, item.MaxStack - backpack[i].Count);
                    backpack[i] = new ItemStack(item, backpack[i].Count + moved);
                    count -= moved;
                }
            for (int i = 0; i < backpack.Length && count > 0; i++)
                if (backpack[i].IsEmpty)
                {
                    int moved = Math.Min(count, item.MaxStack);
                    backpack[i] = new ItemStack(item, moved);
                    count -= moved;
                }
            Changed?.Invoke();
            return count;
        }

        public int FindInBackpack(ItemDefinition item) => Array.FindIndex(backpack, s => s.Item == item && item != null);

        // Pasa un objeto de la mochila a la barra; si el espacio estaba ocupado, lo que había vuelve a ese lugar de la mochila.
        public bool Equip(int backpackIndex, int slot)
        {
            if (!InRange(backpackIndex, backpack.Length) || !InRange(slot, hotbar.Length)) return false;
            var stack = backpack[backpackIndex];
            if (stack.IsEmpty || !rules.Accepts(slot, stack.Item.Category)) return false;
            backpack[backpackIndex] = hotbar[slot];
            hotbar[slot] = stack;
            Changed?.Invoke();
            return true;
        }

        // Devuelve a la mochila lo que hay en un espacio de la barra. Falla si la mochila está llena.
        public bool Unequip(int slot)
        {
            if (!InRange(slot, hotbar.Length) || hotbar[slot].IsEmpty) return false;
            int free = Array.FindIndex(backpack, s => s.IsEmpty);
            if (free < 0) return false;
            backpack[free] = hotbar[slot];
            hotbar[slot] = ItemStack.Empty;
            Changed?.Invoke();
            return true;
        }

        // Elegir el espacio que ya estaba elegido guarda el objeto, y volver a elegirlo lo saca.
        public void Select(int slot)
        {
            if (!InRange(slot, hotbar.Length)) return;
            Holstered = slot == Selected && !Holstered;
            Selected = slot;
            SelectionChanged?.Invoke(slot);
        }

        // Guarda lo que haya en la mano sin cambiar de espacio (así empieza la partida: manos libres).
        public void Holster()
        {
            if (Holstered) return;
            Holstered = true;
            SelectionChanged?.Invoke(Selected);
        }

        // Rueda del mouse: pasa al espacio siguiente o anterior, dando la vuelta, y saca lo que haya.
        public void Cycle(int direction)
        {
            if (direction == 0) return;
            Selected = ((Selected + Math.Sign(direction)) % hotbar.Length + hotbar.Length) % hotbar.Length;
            Holstered = false;
            SelectionChanged?.Invoke(Selected);
        }

        // Gasta unidades del objeto en la mano (granadas, bridas, termita). Si se acaba, el espacio queda vacío.
        public bool ConsumeActive(int count = 1)
        {
            var stack = ActiveStack;
            if (stack.IsEmpty || stack.Count < count) return false;
            hotbar[Selected] = stack.Count == count ? ItemStack.Empty : new ItemStack(stack.Item, stack.Count - count);
            Changed?.Invoke();
            return true;
        }

        private static bool InRange(int index, int length) => index >= 0 && index < length;
    }
}
