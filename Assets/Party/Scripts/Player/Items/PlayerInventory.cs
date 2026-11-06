using UnityEngine;

namespace Alarma.Player.Items
{
    // Inventario del jugador en la escena: crea el modelo con sus reglas y le pone el equipo inicial.
    // El resto de los sistemas (barra, mano, controles) lo leen por la propiedad Inventory y sus eventos.
    public sealed class PlayerInventory : MonoBehaviour
    {
        [SerializeField] private InventoryRules rules;
        [SerializeField] private StartingLoadout loadout;

        public Inventory Inventory { get; private set; }

        public void Configure(InventoryRules slotRules, StartingLoadout startingItems) { rules = slotRules; loadout = startingItems; }

        private void Awake()
        {
            Inventory = new Inventory(rules);
            if (loadout != null) loadout.ApplyTo(Inventory);
        }
    }
}
