using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Mostrador de un local: calcula dónde se deja el producto, dónde se entrega el dinero y mueve el brazo del cajero
    // según el guion de CounterChoreography. El cajero se inclina hacia el mostrador cuando toma o entrega algo.
    [DefaultExecutionOrder(50)]
    public sealed class CounterExchange : MonoBehaviour
    {
        private const float CashierLean = .28f, LeanSpeed = 1.4f, CustomerLean = .32f;
        private ShopActivity shop;
        private Transform drop, bag, handoff, cashier;
        private PedestrianReach cashierHand;
        private Vector3 cashierHome;
        private float cashierActiveUntil, cashierOffset;
        private HandGoal cashierGoal;

        public bool CashierBusy => Time.time < cashierActiveUntil && cashierGoal != HandGoal.None;
        public Vector3 FacingPoint => shop.Scan.position;

        public void Configure(ShopActivity activity) => shop = activity;

        public void BindCashier(Transform body, PedestrianReach hand)
        {
            cashier = body;
            cashierHand = hand;
            cashierHome = body.position;
            PlaceAnchors();
        }

        public ExchangeFrame Frame(PedestrianRoutine routine)
            => CounterChoreography.Evaluate(routine.State, routine.StateSeconds, routine.Timing, shop.Tasks.IsWithdrawal);

        // Punto al que el cliente se acerca desde su lugar de la fila para alcanzar el mostrador.
        public Vector3 LeanPoint(Vector3 from)
        {
            Vector3 toward = shop.Scan.position - from;
            toward.y = 0;
            return from + toward.normalized * CustomerLean;
        }

        public Transform Anchor(ItemPlace place)
        {
            PlaceAnchors();
            switch (place)
            {
                case ItemPlace.Drop: return drop;
                case ItemPlace.Bag: return bag;
                case ItemPlace.Handoff: return handoff;
                case ItemPlace.CashierHand: return shop.CashierGrip;
                default: return null;
            }
        }

        // Lo llama el cliente que está en el mostrador (o tomando su producto) en cada cuadro.
        public void Drive(PedestrianRoutine routine, ExchangeFrame frame, PedestrianReach customerHand, Transform pocket)
        {
            var customerTarget = Target(frame.Customer, routine, pocket);
            if (customerTarget != null && customerHand != null) customerHand.Reach(customerTarget, .15f);
            if (routine.State < PedestrianState.Placing || routine.State > PedestrianState.Collecting) return;
            cashierGoal = frame.Cashier;
            cashierActiveUntil = Time.time + .2f;
            var cashierTarget = Target(frame.Cashier, routine, pocket);
            if (cashierTarget != null && cashierHand != null) cashierHand.Reach(cashierTarget, .15f);
        }

        private Transform Target(HandGoal goal, PedestrianRoutine routine, Transform pocket)
        {
            switch (goal)
            {
                case HandGoal.Shelf: return routine.Session != null ? shop.ProductPoint(routine.Session.Station) : null;
                case HandGoal.Drop: return Anchor(ItemPlace.Drop);
                case HandGoal.Bag: return Anchor(ItemPlace.Bag);
                case HandGoal.Handoff: return Anchor(ItemPlace.Handoff);
                case HandGoal.Scanner: return shop.Scan;
                case HandGoal.Till: return shop.Till;
                case HandGoal.Pocket: return pocket;
                default: return null;
            }
        }

        // El cajero da medio paso hacia el mostrador para tomar o entregar y vuelve a su lugar.
        private void Update()
        {
            if (cashier == null) return;
            bool reaching = CashierBusy && cashierGoal != HandGoal.Till;
            cashierOffset = Mathf.MoveTowards(cashierOffset, reaching ? CashierLean : 0f, LeanSpeed * Time.deltaTime);
            cashier.position = cashierHome + Toward() * cashierOffset;
        }

        private Vector3 Toward()
        {
            Vector3 from = cashier != null ? cashierHome : shop.Scan.position;
            Vector3 toward = shop.Counter.position - from;
            toward.y = 0;
            return toward.sqrMagnitude > .0001f ? toward.normalized : transform.forward;
        }

        // Sobre el mostrador: a un lado se deja el producto, al otro queda la compra lista y al centro se pasan billetes.
        // En el banco todo pasa por la bandeja de la ventanilla.
        private void PlaceAnchors()
        {
            if (drop == null)
            {
                drop = new GameObject("Mostrador_Dejar").transform;
                bag = new GameObject("Mostrador_Compra").transform;
                handoff = new GameObject("Mostrador_Entrega").transform;
                foreach (var anchor in new[] { drop, bag, handoff }) anchor.SetParent(transform, true);
            }
            Vector3 scan = shop.Scan.position, toward = Toward(), side = Vector3.Cross(Vector3.up, toward).normalized;
            if (shop.Tasks.IsWithdrawal)
            {
                drop.position = bag.position = scan + Vector3.up * .03f;
                handoff.position = scan + Vector3.up * .05f;
                return;
            }
            drop.position = scan + toward * .15f + side * .22f + Vector3.up * .03f;
            bag.position = scan + toward * .15f - side * .25f + Vector3.up * .03f;
            handoff.position = scan + toward * .05f + Vector3.up * .2f;
        }
    }
}
