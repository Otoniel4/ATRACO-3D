using System;
using System.Collections.Generic;

namespace Alarma.AI.CityLife
{
    public sealed class ShopQueue
    {
        private readonly List<int> customers = new List<int>();
        public int Capacity { get; }
        public int Count => customers.Count;
        public event Action Changed;
        public ShopQueue(int capacity) { if (capacity < 1) throw new ArgumentOutOfRangeException(nameof(capacity)); Capacity = capacity; }
        public bool TryJoin(int customer)
        {
            if (customers.Contains(customer)) return true;
            if (customers.Count >= Capacity) return false;
            customers.Add(customer); Changed?.Invoke(); return true;
        }
        public int IndexOf(int customer) => customers.IndexOf(customer);
        public void Release(int customer) { if (customers.Remove(customer)) Changed?.Invoke(); }
        public void Clear() { if (customers.Count == 0) return; customers.Clear(); Changed?.Invoke(); }
    }
}
