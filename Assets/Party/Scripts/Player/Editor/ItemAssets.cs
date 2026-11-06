using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Alarma.Player.Items;

namespace Alarma.Player.Editor
{
    // Crea los assets del inventario en Party/Data/Items la primera vez: un ItemDefinition por objeto del GDD (7.1 y 8.2)
    // con su ícono y su modelo, las reglas de la barra rápida y el equipo inicial. Si ya existen no se tocan: desde ahí
    // se ajustan a mano en el Inspector (nombres, textos, giro en la mano).
    public static class ItemAssets
    {
        private const string Folder = "Assets/Party/Data/Items", Icons = "Assets/Party/Art/UI/Items", Models = "Assets/Party/Art/Weapons";

        private sealed class Spec
        {
            public string Id, Name, Model, Text;
            public ItemCategory Category;
            public ItemTier Tier;
            public HoldStyle Hold;
            public int Stack = 1, Start = 1;
        }

        // La porra no está: es solo de los guardias (NPC).
        private static readonly Spec[] Specs =
        {
            new Spec { Id = "pistola", Hold = HoldStyle.Pistol, Name = "Pistola", Model = "Weapon_Pistol", Category = ItemCategory.Weapon, Tier = ItemTier.Starter, Text = "Apuntar a alguien lo intimida. Disparar derriba, nunca mata." },
            new Spec { Id = "escopeta", Hold = HoldStyle.Long, Name = "Escopeta", Model = "Weapon_Shotgun", Category = ItemCategory.Weapon, Tier = ItemTier.Mid, Text = "Mucha fuerza a corta distancia. Muy ruidosa." },
            new Spec { Id = "taser", Hold = HoldStyle.Pistol, Name = "Táser", Model = "Weapon_Taser", Category = ItemCategory.Weapon, Tier = ItemTier.Mid, Text = "Deja fuera de combate a un guardia por unos segundos, sin ruido." },
            new Spec { Id = "rifle", Hold = HoldStyle.Long, Name = "Rifle", Model = "Weapon_Rifle", Category = ItemCategory.Weapon, Tier = ItemTier.Advanced, Text = "Alcance largo para los golpes grandes." },
            new Spec { Id = "palanca", Hold = HoldStyle.OneHandUpright, Name = "Palanca", Model = "Tool_Crowbar", Category = ItemCategory.Tool, Tier = ItemTier.Starter, Text = "Fuerza cerraduras, cajas registradoras y puertas. Hace ruido." },
            new Spec { Id = "ganzua", Hold = HoldStyle.OneHandPointing, Name = "Ganzúa", Model = "Tool_Lockpick", Category = ItemCategory.Tool, Tier = ItemTier.Starter, Text = "Abre cerraduras en silencio, con paciencia." },
            new Spec { Id = "taladro", Hold = HoldStyle.Pistol, Name = "Taladro", Model = "Tool_Drill", Category = ItemCategory.Tool, Tier = ItemTier.Mid, Text = "Perfora cajas fuertes. Lento y ruidoso." },
            new Spec { Id = "cortavidrios", Hold = HoldStyle.OneHandUpright, Name = "Cortavidrios", Model = "Tool_GlassCutter", Category = ItemCategory.Tool, Tier = ItemTier.Mid, Text = "Abre las vitrinas de la joyería sin romperlas ni hacer ruido." },
            new Spec { Id = "hackeo", Hold = HoldStyle.TwoHandTablet, Name = "Dispositivo de hackeo", Model = "Tool_HackingTablet", Category = ItemCategory.Tool, Tier = ItemTier.Mid, Text = "Apaga cámaras y abre puertas electrónicas." },
            new Spec { Id = "termita", Hold = HoldStyle.TwoHandCanister, Name = "Termita", Model = "Tool_ThermiteCharge", Category = ItemCategory.Tool, Tier = ItemTier.Advanced, Text = "Derrite la puerta de la bóveda del banco." },
            new Spec { Id = "gancho", Hold = HoldStyle.OneHandUpright, Name = "Gancho para azoteas", Model = "Tool_GrapplingHook", Category = ItemCategory.Tool, Tier = ItemTier.Advanced, Text = "Sube a los techos para entrar o escapar." },
            new Spec { Id = "bridas", Hold = HoldStyle.OneHandPointing, Name = "Bridas", Model = "Tool_ZipTies", Category = ItemCategory.Consumable, Tier = ItemTier.Starter, Stack = 10, Start = 6, Text = "Amarran a un empleado o cliente para que no dé la alarma." },
            new Spec { Id = "humo", Hold = HoldStyle.OneHandUpright, Name = "Granada de humo", Model = "Consumable_Smoke", Category = ItemCategory.Consumable, Tier = ItemTier.Mid, Stack = 3, Start = 2, Text = "Tapa la vista de cámaras, guardias y policías." },
            new Spec { Id = "aturdidora", Hold = HoldStyle.OneHandUpright, Name = "Granada aturdidora", Model = "Consumable_Stun", Category = ItemCategory.Consumable, Tier = ItemTier.Advanced, Stack = 3, Start = 2, Text = "Aturde a todos los que estén cerca." },
            new Spec { Id = "emp", Hold = HoldStyle.OneHandUpright, Name = "EMP", Model = "Consumable_EMP", Category = ItemCategory.Consumable, Tier = ItemTier.Advanced, Stack = 2, Start = 1, Text = "Apaga cámaras, alarmas y luces de la zona por un rato." },
        };
        // Barra rápida al empezar (GDD 8.2): arma, dos herramientas, consumible y un espacio libre.
        private static readonly string[] StartingHotbar = { "pistola", "palanca", "ganzua", "bridas", "taladro" };

        public static (InventoryRules rules, StartingLoadout loadout, HoldPoseLibrary poses) Prepare()
        {
            Directory.CreateDirectory(Folder);
            AssetDatabase.Refresh();
            var items = Specs.Select(Item).ToArray();
            var rules = LoadOrCreate<InventoryRules>(Folder + "/InventoryRules.asset", _ => { });
            var poses = LoadOrCreate<HoldPoseLibrary>(Folder + "/HoldPoses.asset", _ => { });
            var defaults = ScriptableObject.CreateInstance<HoldPoseLibrary>();
            if (poses.CompleteAimFrom(defaults)) EditorUtility.SetDirty(poses); // pose de apuntar en assets anteriores
            Object.DestroyImmediate(defaults);
            var loadout = LoadOrCreate<StartingLoadout>(Folder + "/StartingLoadout.asset", created => created.Configure(
                items.Select((item, i) => new ItemStack(item, Specs[i].Start)).ToArray(),
                StartingHotbar.Select(id => items[System.Array.FindIndex(Specs, s => s.Id == id)]).ToArray()));
            AssetDatabase.SaveAssets();
            return (rules, loadout, poses);
        }

        private static ItemDefinition Item(Spec spec)
        {
            string icon = Icons + "/Icon_" + spec.Model + ".png";
            ConfigureIcon(icon);
            var item = LoadOrCreate<ItemDefinition>(Folder + "/Item_" + spec.Id + ".asset", created => created.Configure(spec.Id, spec.Name, spec.Text, spec.Category, spec.Tier, spec.Stack,
                AssetDatabase.LoadAssetAtPath<Texture2D>(icon) ?? throw new FileNotFoundException("Falta el ícono (build_item_icons.py)", icon),
                AssetDatabase.LoadAssetAtPath<GameObject>(Models + "/" + spec.Model + ".fbx") ?? throw new FileNotFoundException("Falta el modelo", spec.Model), spec.Hold));
            // Assets creados antes de que existiera la forma de sostener: se completa sin tocar lo ajustado a mano.
            if (item.HoldStyle == HoldStyle.Unset) { item.AssignHoldStyle(spec.Hold); EditorUtility.SetDirty(item); }
            // Qué hace con clic izquierdo y su animación (item_actions.json): el asset se crea o se pone al día si subió la versión.
            var action = ItemActionAssets.For(spec.Id);
            if (item.Action == null && action != null) { item.AssignAction(action); EditorUtility.SetDirty(item); }
            return item;
        }

        private static T LoadOrCreate<T>(string path, System.Action<T> setup) where T : ScriptableObject
        {
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null) return asset;
            asset = ScriptableObject.CreateInstance<T>();
            setup(asset);
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }

        // Íconos con transparencia, sin mipmaps (se ven nítidos en la barra).
        private static void ConfigureIcon(string path)
        {
            var importer = AssetImporter.GetAtPath(path) as TextureImporter ?? throw new FileNotFoundException("Falta el ícono (build_item_icons.py)", path);
            if (importer.alphaIsTransparency && !importer.mipmapEnabled && importer.wrapMode == TextureWrapMode.Clamp) return;
            importer.textureType = TextureImporterType.Default;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.SaveAndReimport();
        }
    }
}
