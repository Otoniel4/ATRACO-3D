using UnityEngine;

namespace Alarma.Player.Items
{
    // Tipo de objeto según el GDD (8.2): la barra rápida reserva espacios por tipo.
    public enum ItemCategory { Weapon, Tool, Consumable }

    // Nivel de la tienda en que se desbloquea (GDD 7.1).
    public enum ItemTier { Starter, Mid, Advanced }

    // Cómo se sostiene: con una o dos manos y en qué posición (las posiciones están en HoldPoseLibrary).
    public enum HoldStyle { Unset, Pistol, Long, OneHandUpright, OneHandPointing, TwoHandTablet, TwoHandCanister }

    // Datos de un arma, herramienta o consumible: nombre, tipo, ícono y el modelo que se ve en la mano.
    // Cada objeto es un asset: agregar uno nuevo no cambia el código del inventario.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Objeto", fileName = "Item")]
    public sealed class ItemDefinition : ScriptableObject
    {
        [SerializeField] private string id;
        [SerializeField] private string displayName;
        [SerializeField, TextArea] private string description;
        [SerializeField] private ItemCategory category;
        [SerializeField] private ItemTier tier;
        [SerializeField, Min(1), Tooltip("Cuántos caben en un espacio (bridas y granadas se apilan).")] private int maxStack = 1;
        [SerializeField] private Texture2D icon;
        [SerializeField] private GameObject handModel;
        [SerializeField] private HoldStyle holdStyle;
        [SerializeField, Tooltip("Qué hace con clic izquierdo y con qué animación (disparar, lanzar, colocar, herramienta).")] private ItemAction action;
        [SerializeField, Tooltip("Giro extra sobre la pose de su forma de sostener, en grados.")] private Vector3 holdEuler;
        [SerializeField, Tooltip("Ajuste extra de la posición sobre la pose, en metros (x derecha, y arriba, z adelante).")] private Vector3 holdOffset;

        public string Id => id;
        public string DisplayName => displayName;
        public string Description => description;
        public ItemCategory Category => category;
        public ItemTier Tier => tier;
        public int MaxStack => maxStack;
        public Texture2D Icon => icon;
        public GameObject HandModel => handModel;
        public HoldStyle HoldStyle => holdStyle;
        public ItemAction Action => action;
        public Vector3 HoldEuler => holdEuler;
        public Vector3 HoldOffset => holdOffset;

        // Lo usa el preparador del editor al crear el asset por primera vez.
        public void Configure(string itemId, string label, string text, ItemCategory kind, ItemTier level, int stack, Texture2D image, GameObject model, HoldStyle hold)
        {
            id = itemId; displayName = label; description = text; category = kind; tier = level; maxStack = Mathf.Max(1, stack); icon = image; handModel = model; holdStyle = hold;
        }

        // Para assets creados antes de que existiera la forma de sostener: el preparador la completa una sola vez.
        public void AssignHoldStyle(HoldStyle hold) { if (holdStyle == HoldStyle.Unset) holdStyle = hold; }

        // Igual para la acción: se asigna una vez y después se puede cambiar a mano.
        public void AssignAction(ItemAction use) { if (action == null) action = use; }
    }
}
