using System;

namespace Alarma.AI.CityLife
{
    // Cajas de un local, cada una con su fila. El cliente se pone en la que tiene menos gente (si empatan, la primera)
    // y en cada caja se atiende solo al primero de su fila. Un local con una caja funciona igual que antes.
    public sealed class CheckoutLanes
    {
        private readonly ShopQueue[] lanes;

        public event Action Changed;

        public CheckoutLanes(int count, int capacity)
        {
            if (count < 1) throw new ArgumentOutOfRangeException(nameof(count));
            lanes = new ShopQueue[count];
            for (int i = 0; i < count; i++)
            {
                lanes[i] = new ShopQueue(capacity);
                lanes[i].Changed += () => Changed?.Invoke();
            }
        }

        public int Count => lanes.Length;
        public int Capacity => lanes[0].Capacity;
        public ShopQueue this[int lane] => lanes[lane];

        // La caja con menos gente que todavía tiene lugar en su fila; -1 si todas están llenas.
        public int Choose()
        {
            int best = -1;
            for (int i = 0; i < lanes.Length; i++)
                if (lanes[i].Count < lanes[i].Capacity && (best < 0 || lanes[i].Count < lanes[best].Count)) best = i;
            return best;
        }

        public int LaneOf(int customer)
        {
            for (int i = 0; i < lanes.Length; i++) if (lanes[i].IndexOf(customer) >= 0) return i;
            return -1;
        }

        // Le toca: es el primero de la fila de su caja.
        public bool IsFront(int customer)
        {
            int lane = LaneOf(customer);
            return lane >= 0 && lanes[lane].IndexOf(customer) == 0;
        }

        public void Release(int customer) { foreach (var lane in lanes) lane.Release(customer); }
        public void Clear() { foreach (var lane in lanes) lane.Clear(); }
    }
}
