using System.Collections.Generic;
using Alarma.Player.Items;
using NUnit.Framework;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Alarma.Player.Tests
{
    // Reglas de la barra rápida del GDD (8.2): 1 arma, 2 herramientas, 1 consumible y 1 libre; mochila y selección.
    public sealed class InventoryTests
    {
        private readonly List<ScriptableObject> created = new List<ScriptableObject>();
        private ItemDefinition pistol, crowbar, lockpick, zipTies;

        [SetUp]
        public void SetUp()
        {
            pistol = Item("pistola", ItemCategory.Weapon, 1);
            crowbar = Item("palanca", ItemCategory.Tool, 1);
            lockpick = Item("ganzua", ItemCategory.Tool, 1);
            zipTies = Item("bridas", ItemCategory.Consumable, 10);
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var asset in created) Object.DestroyImmediate(asset);
            created.Clear();
        }

        [Test]
        public void WeaponOnlyFitsTheWeaponSlotOrTheFreeSlot()
        {
            var inventory = Create();
            inventory.Add(pistol, 1);
            Assert.IsFalse(inventory.Equip(0, 1), "El espacio 2 es de herramientas.");
            Assert.IsTrue(inventory.Equip(0, 4), "El espacio 5 acepta cualquier cosa.");
            Assert.AreEqual(pistol, inventory.Hotbar(4).Item);
        }

        [Test]
        public void EquippingAnOccupiedSlotSwapsWithTheBackpack()
        {
            var inventory = Create();
            inventory.Add(crowbar, 1);
            inventory.Add(lockpick, 1);
            Assert.IsTrue(inventory.Equip(0, 1));
            Assert.IsTrue(inventory.Equip(inventory.FindInBackpack(lockpick), 1));
            Assert.AreEqual(lockpick, inventory.Hotbar(1).Item);
            Assert.GreaterOrEqual(inventory.FindInBackpack(crowbar), 0, "La palanca vuelve a la mochila.");
        }

        [Test]
        public void ConsumablesStackUpToTheirLimit()
        {
            var inventory = Create();
            Assert.AreEqual(0, inventory.Add(zipTies, 14));
            Assert.AreEqual(10, inventory.Backpack(0).Count);
            Assert.AreEqual(4, inventory.Backpack(1).Count);
        }

        [Test]
        public void UnequipReturnsTheItemToTheBackpack()
        {
            var inventory = Create();
            inventory.Add(pistol, 1);
            inventory.Equip(0, 0);
            Assert.IsTrue(inventory.Unequip(0));
            Assert.IsTrue(inventory.Hotbar(0).IsEmpty);
            Assert.AreEqual(pistol, inventory.Backpack(0).Item);
        }

        [Test]
        public void WheelCyclesAroundTheHotbar()
        {
            var inventory = Create();
            var seen = new List<int>();
            inventory.SelectionChanged += seen.Add;
            inventory.Cycle(-1);
            inventory.Cycle(1);
            inventory.Select(2);
            CollectionAssert.AreEqual(new[] { 4, 0, 2 }, seen);
        }

        [Test]
        public void PressingTheSameSlotAgainStowsAndDrawsTheItem()
        {
            var inventory = Create();
            inventory.Add(pistol, 1);
            inventory.Equip(0, 0);
            Assert.AreEqual(pistol, inventory.ActiveStack.Item);
            inventory.Select(0);
            Assert.IsTrue(inventory.Holstered);
            Assert.IsTrue(inventory.ActiveStack.IsEmpty, "Guardada: manos libres.");
            inventory.Select(0);
            Assert.AreEqual(pistol, inventory.ActiveStack.Item);
            inventory.Select(0);
            inventory.Cycle(1);
            Assert.IsFalse(inventory.Holstered, "La rueda saca el objeto del espacio nuevo.");
        }

        [Test]
        public void ConsumingTheLastUnitEmptiesTheSlot()
        {
            var inventory = Create();
            inventory.Add(zipTies, 2);
            inventory.Equip(0, 3);
            inventory.Select(3);
            Assert.IsTrue(inventory.ConsumeActive());
            Assert.AreEqual(1, inventory.ActiveStack.Count);
            Assert.IsTrue(inventory.ConsumeActive());
            Assert.IsTrue(inventory.Hotbar(3).IsEmpty);
            Assert.IsFalse(inventory.ConsumeActive());
        }

        private Inventory Create()
        {
            var rules = ScriptableObject.CreateInstance<InventoryRules>();
            created.Add(rules);
            return new Inventory(rules);
        }

        private ItemDefinition Item(string id, ItemCategory category, int stack)
        {
            var item = ScriptableObject.CreateInstance<ItemDefinition>();
            item.Configure(id, id, "", category, ItemTier.Starter, stack, null, null, HoldStyle.Pistol);
            created.Add(item);
            return item;
        }
    }
}
