namespace Alarma.AI.CityLife
{
    // A dónde apunta cada mano durante la venta.
    public enum HandGoal { None, Shelf, Drop, Scanner, Bag, Handoff, Till, Pocket, Carry }
    // Dónde está cada objeto de la venta.
    public enum ItemPlace { Hidden, Shelf, CustomerHand, CashierHand, Drop, Bag, Handoff }

    public readonly struct ExchangeFrame
    {
        public readonly HandGoal Customer, Cashier;
        public readonly ItemPlace Product, Money, Change, Ticket;
        public readonly bool CustomerApproach;
        public ExchangeFrame(HandGoal customer, HandGoal cashier, ItemPlace product, ItemPlace money, ItemPlace change, ItemPlace ticket, bool approach)
        { Customer = customer; Cashier = cashier; Product = product; Money = money; Change = change; Ticket = ticket; CustomerApproach = approach; }
        public bool CashierBusy => Cashier != HandGoal.None;
    }

    // Duraciones de cada paso en el mostrador; la rutina y la coreografía usan las mismas.
    [System.Serializable]
    public sealed class CounterTiming
    {
        public float Pick = 1.2f, Place = 1.4f, Scan = 2.4f, Pay = 3.0f, Change = 1.2f, Bag = 1.2f;
        public static readonly CounterTiming Standard = new CounterTiming();
    }

    // Guion de la venta como lo haría una persona: toma el producto, lo deja en el mostrador, el cajero lo escanea y lo
    // deja del lado del cliente, el cliente saca el dinero, se lo da en la mano, el cajero lo guarda, entrega el vuelto
    // y el cliente se lleva la compra. En el banco: saca número, lo entrega en la ventanilla y recibe el efectivo.
    public static class CounterChoreography
    {
        public const float ScanPickup = .26f, ScanReader = .60f, ScanLanding = .87f, ScanRelease = .97f;

        public static float Blend(float progress)
        {
            float t = System.Math.Max(0f, System.Math.Min(1f, progress));
            return t * t * t * (t * (t * 6f - 15f) + 10f);
        }
        public static ExchangeFrame Evaluate(PedestrianState state, float t, CounterTiming timing, bool withdrawal)
            => withdrawal ? Withdrawal(state, CanonicalTime(state, t, timing)) : Purchase(state, CanonicalTime(state, t, timing), timing);

        // Los hitos conservan su proporción al ajustar las duraciones de cualquier negocio.
        private static float CanonicalTime(PedestrianState state, float seconds, CounterTiming timing)
        {
            switch (state)
            {
                case PedestrianState.PickingUp: return seconds * 1.2f / System.Math.Max(.1f, timing.Pick);
                case PedestrianState.Placing: return seconds * 1.4f / System.Math.Max(.1f, timing.Place);
                case PedestrianState.Scanning: return seconds * 2.4f / System.Math.Max(.1f, timing.Scan);
                case PedestrianState.Paying: return seconds * 3f / System.Math.Max(.1f, timing.Pay);
                case PedestrianState.ReceivingReceipt: return seconds * 1.2f / System.Math.Max(.1f, timing.Change);
                case PedestrianState.Collecting: return seconds * 1.2f / System.Math.Max(.1f, timing.Bag);
                default: return seconds;
            }
        }

        private static ExchangeFrame Purchase(PedestrianState state, float t, CounterTiming timing)
        {
            const ItemPlace hidden = ItemPlace.Hidden;
            switch (state)
            {
                case PedestrianState.PickingUp:
                    return Frame(t < .96f ? HandGoal.Shelf : HandGoal.Carry, HandGoal.None, t < .65f ? ItemPlace.Shelf : ItemPlace.CustomerHand);
                case PedestrianState.WaitingForSpace:
                case PedestrianState.Queueing:
                case PedestrianState.ApproachingCounter:
                    return Frame(HandGoal.None, HandGoal.None, ItemPlace.CustomerHand);
                case PedestrianState.Placing:
                    return Frame(t < 1.2f ? HandGoal.Drop : HandGoal.None, HandGoal.None, t < .82f ? ItemPlace.CustomerHand : ItemPlace.Drop, approach: true);
                case PedestrianState.Scanning:
                {
                    float scan = t / 2.4f;
                    var cashier = scan < ScanPickup ? HandGoal.Drop : scan < ScanReader ? HandGoal.Scanner
                        : scan < ScanRelease ? HandGoal.Bag : HandGoal.None;
                    var product = scan < ScanPickup ? ItemPlace.Drop : scan < ScanLanding ? ItemPlace.CashierHand : ItemPlace.Bag;
                    return Frame(HandGoal.None, cashier, product, approach: true);
                }
                case PedestrianState.Paying:
                {
                    var customer = t < .5f ? HandGoal.Pocket : t < 1.4f ? HandGoal.Handoff : t < 2.4f ? HandGoal.None : HandGoal.Handoff;
                    var cashier = t < .8f ? HandGoal.None : t < 1.4f ? HandGoal.Handoff : t < 2.1f ? HandGoal.Till : HandGoal.Handoff;
                    var money = t < .4f ? hidden : t < 1.3f ? ItemPlace.CustomerHand : t < 2.0f ? ItemPlace.CashierHand : hidden;
                    var change = t < 2.1f ? hidden : ItemPlace.CashierHand;
                    return Frame(customer, cashier, ItemPlace.Bag, money, change, approach: true);
                }
                case PedestrianState.ReceivingReceipt:
                {
                    var change = t < .35f ? ItemPlace.CashierHand : t < .9f ? ItemPlace.CustomerHand : hidden;
                    return Frame(t < .4f ? HandGoal.Handoff : HandGoal.Pocket, t < .4f ? HandGoal.Handoff : HandGoal.None, ItemPlace.Bag, change: change, approach: true);
                }
                case PedestrianState.Collecting:
                    return Frame(t < 1f ? HandGoal.Bag : HandGoal.Carry, HandGoal.None, t < .65f ? ItemPlace.Bag : ItemPlace.CustomerHand, approach: true);
                case PedestrianState.Inactive:
                case PedestrianState.Walking:
                case PedestrianState.WaitingForEntry:
                case PedestrianState.Entering:
                case PedestrianState.Browsing:
                    return Frame(HandGoal.None, HandGoal.None, ItemPlace.Shelf);
                default:
                    return Frame(HandGoal.None, HandGoal.None, hidden);
            }
        }

        private static ExchangeFrame Withdrawal(PedestrianState state, float t)
        {
            const ItemPlace hidden = ItemPlace.Hidden;
            switch (state)
            {
                case PedestrianState.PickingUp: // saca número en la máquina de turnos
                    return Frame(t < .7f ? HandGoal.Shelf : HandGoal.None, HandGoal.None, hidden, ticket: t < .6f ? hidden : ItemPlace.CustomerHand);
                case PedestrianState.WaitingForSpace:
                case PedestrianState.Queueing:
                case PedestrianState.ApproachingCounter:
                    return Frame(HandGoal.None, HandGoal.None, hidden, ticket: ItemPlace.CustomerHand);
                case PedestrianState.Placing: // pasa el número por la bandeja
                    return Frame(t < .8f ? HandGoal.Drop : HandGoal.None, HandGoal.None, hidden, ticket: t < .75f ? ItemPlace.CustomerHand : ItemPlace.Drop, approach: true);
                case PedestrianState.Scanning: // el cajero lo toma y registra el retiro en su terminal
                {
                    var cashier = t < .7f ? HandGoal.Drop : t < 2.1f ? HandGoal.Till : HandGoal.None;
                    var ticket = t < .7f ? ItemPlace.Drop : t < 1.2f ? ItemPlace.CashierHand : hidden;
                    return Frame(HandGoal.None, cashier, hidden, ticket: ticket, approach: true);
                }
                case PedestrianState.Paying: // cuenta el efectivo, lo deja en la bandeja y el cliente lo guarda
                {
                    var cashier = t < .8f ? HandGoal.Till : t < 1.6f ? HandGoal.Handoff : HandGoal.None;
                    var customer = t < 1.6f ? HandGoal.None : t < 2.4f ? HandGoal.Handoff : HandGoal.Pocket;
                    var money = t < .6f ? hidden : t < 1.5f ? ItemPlace.CashierHand : t < 2.2f ? ItemPlace.Handoff : t < 2.9f ? ItemPlace.CustomerHand : hidden;
                    return Frame(customer, cashier, hidden, money, approach: true);
                }
                case PedestrianState.ReceivingReceipt:
                case PedestrianState.Collecting:
                    return Frame(HandGoal.None, HandGoal.None, hidden, approach: true);
                default:
                    return Frame(HandGoal.None, HandGoal.None, hidden);
            }
        }

        private static ExchangeFrame Frame(HandGoal customer, HandGoal cashier, ItemPlace product, ItemPlace money = ItemPlace.Hidden,
            ItemPlace change = ItemPlace.Hidden, ItemPlace ticket = ItemPlace.Hidden, bool approach = false)
            => new ExchangeFrame(customer, cashier, product, money, change, ticket, approach);
    }
}
