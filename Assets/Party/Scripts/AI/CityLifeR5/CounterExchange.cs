using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Calcula los apoyos y las trayectorias de las manos para una caja.
    [DefaultExecutionOrder(50)]
    public sealed class CounterExchange : MonoBehaviour
    {
        private ShopActivity shop;
        private CheckoutStation station;
        private Transform drop, bag, handoff, cashier;
        private readonly CommerceHandMotion cashierMotion = new CommerceHandMotion();
        private PedestrianReach cashierHand;
        public PedestrianReach CashierHand => cashierHand;
        private Vector3 cashierHome;
        private float cashierActiveUntil;
        private HandGoal cashierGoal;
        private float scanProgress;
        private ShopAnimationProfile Profile => shop.Tasks.Animation;
        public Quaternion ProductTilt => Quaternion.Euler(0f, 0f,
            Mathf.Sin(Mathf.Clamp01((scanProgress - CounterChoreography.ScanPickup)
                / (CounterChoreography.ScanLanding - CounterChoreography.ScanPickup)) * Mathf.PI)
            * (Profile != null ? Profile.InspectionTilt : 10f));

        public bool CashierBusy => Time.time < cashierActiveUntil && cashierGoal != HandGoal.None;
        public Vector3 FacingPoint => station.scan.position;
        public Vector3 CustomerForward => -Toward();

        public void Configure(ShopActivity activity, CheckoutStation checkout) { shop = activity; station = checkout; }

        public void BindCashier(Transform body, PedestrianReach hand)
        {
            cashier = body;
            cashierHand = hand;
            if (hand != null) station.cashierGrip = hand.PurchaseGrip;
            cashierHome = body.position;
            if (station.workspace != null && hand != null)
            {
                body.rotation = Quaternion.LookRotation(station.workspace.forward);
                Vector3 stand = station.workspace.position - station.workspace.forward * (Profile.CounterWidth * .5f + .255f);
                stand.y = body.position.y;
                body.position = hand.AlignSurfaceStand(station.workspace.position, stand, station.workspace.forward);
                cashierHome = body.position;
            }
            PlaceAnchors();
        }

        public ExchangeFrame Frame(PedestrianRoutine routine)
            => CounterChoreography.Evaluate(routine.State, routine.StateSeconds, routine.Timing, shop.Tasks.IsWithdrawal);

        // Punto al que el cliente se acerca desde su lugar de la fila para alcanzar el mostrador.
        public Vector3 LeanPoint(PedestrianReach hand, Vector3 gripOffset = default, bool twoHands = false)
        {
            if (station.workspace == null) return station.counter.position;
            Vector3 stand = station.workspace.position + Toward() * (Profile.CounterWidth * .5f + .255f);
            stand.y = station.counter.position.y;
            return twoHands ? stand : hand.AlignSurfaceStand(station.workspace.position + gripOffset, stand, -Toward());
        }

        public Transform Anchor(ItemPlace place)
        {
            PlaceAnchors();
            switch (place)
            {
                case ItemPlace.Drop: return drop;
                case ItemPlace.Bag: return bag;
                case ItemPlace.Handoff: return handoff;
                case ItemPlace.CashierHand: return station.cashierGrip;
                default: return null;
            }
        }

        public Vector3 TillPosition => station.Till.position;

        // Lo llama el cliente que está en el mostrador (o tomando su producto) en cada cuadro.
        public void Drive(PedestrianRoutine routine, ExchangeFrame frame, PedestrianReach customerHand, Transform pocket, CommerceHandMotion customerMotion,
            Vector3? customerContact = null, Vector3? cashierContact = null, float productHeight = 0f,
            Vector3? customerGrip = null, Vector3? cashierGrip = null, bool twoHands = false)
        {
            var customerTarget = Target(frame.Customer, routine, pocket);
            float speed = Profile != null ? Profile.HandSpeed : 1.2f;
            float smoothing = Profile != null ? Profile.HandSmoothing : .12f;
            Vector3? customerPoint = frame.Customer == HandGoal.Carry
                ? customerHand.transform.TransformPoint(new Vector3(.24f, 1.22f, .28f))
                : customerTarget != null ? customerTarget.position : (Vector3?)null;
            bool productAction = !shop.Tasks.IsWithdrawal && (routine.State == PedestrianState.PickingUp
                || routine.State == PedestrianState.Placing || routine.State == PedestrianState.Scanning || routine.State == PedestrianState.Collecting);
            if (customerPoint.HasValue && productAction && frame.Customer != HandGoal.Carry) customerPoint += customerGrip ?? Vector3.up * productHeight;
            customerMotion.Follow(customerHand, customerContact ?? customerPoint, speed, smoothing, productAction);
            if (routine.State < PedestrianState.Placing || routine.State > PedestrianState.Collecting) return;
            if (cashier != null && cashierHand != null && station.workspace != null)
            {
                Vector3 stand = station.workspace.position - Toward() * (Profile.CounterWidth * .5f + .255f);
                stand.y = cashierHome.y;
                if (!twoHands) stand = cashierHand.AlignSurfaceStand(station.workspace.position + (cashierGrip ?? Vector3.zero), stand, Toward());
                cashier.position = Vector3.MoveTowards(cashier.position, stand, Time.deltaTime * .3f);
            }
            cashierGoal = cashierContact.HasValue ? HandGoal.Handoff : frame.Cashier;
            cashierActiveUntil = Time.time + .2f;
            var cashierTarget = Target(frame.Cashier, routine, pocket);
            Vector3? cashierPoint = cashierTarget != null ? cashierTarget.position : (Vector3?)null;
            scanProgress = routine.State == PedestrianState.Scanning ? routine.StateSeconds / Mathf.Max(.1f, routine.Timing.Scan) : 0f;
            if (cashierPoint.HasValue && routine.State == PedestrianState.Scanning && !shop.Tasks.IsWithdrawal)
                cashierPoint = ScanPath(scanProgress);
            // El banco cuenta sobre la caja antes de acercar el efectivo a la bandeja.
            if (cashierPoint.HasValue && shop.Tasks.IsWithdrawal && routine.State == PedestrianState.Paying && frame.Cashier == HandGoal.Till)
            {
                float count = Mathf.Clamp01(routine.StateSeconds / Mathf.Max(.1f, routine.Timing.Pay) / (.8f / 3f));
                cashierPoint += Vector3.up * (Mathf.Sin(count * Mathf.PI * 6f) * Mathf.Sin(count * Mathf.PI) * .025f);
            }
            if (cashierPoint.HasValue && productAction) cashierPoint += cashierGrip ?? Vector3.up * productHeight;
            cashierMotion.Follow(cashierHand, cashierContact ?? cashierPoint, speed, smoothing, productAction);
        }

        private Vector3 ScanPath(float progress)
        {
            PlaceAnchors();
            float lift = Profile != null ? Profile.InspectionLift : .08f;
            float sweep = Profile != null ? Profile.InspectionSweep : .1f;
            Vector3 side = Vector3.Cross(Vector3.up, Toward());
            Vector3 scanner = station.scan.position + Vector3.up * lift;
            if (progress <= CounterChoreography.ScanReader)
            {
                float t = Mathf.InverseLerp(CounterChoreography.ScanPickup, CounterChoreography.ScanReader, progress);
                return Vector3.Lerp(drop.position, scanner + side * sweep, CounterChoreography.Blend(t))
                    + Vector3.up * Mathf.Sin(Mathf.PI * t) * lift;
            }
            float landing = Mathf.InverseLerp(CounterChoreography.ScanReader, CounterChoreography.ScanLanding, progress);
            return Vector3.Lerp(scanner + side * sweep, bag.position, CounterChoreography.Blend(landing))
                + Vector3.up * Mathf.Sin(Mathf.PI * landing) * lift;
        }

        private Transform Target(HandGoal goal, PedestrianRoutine routine, Transform pocket)
        {
            switch (goal)
            {
                case HandGoal.Shelf: return routine.Session != null ? shop.ProductPoint(routine.Session.Station) : null;
                case HandGoal.Drop: return Anchor(ItemPlace.Drop);
                case HandGoal.Bag: return Anchor(ItemPlace.Bag);
                case HandGoal.Handoff: return Anchor(ItemPlace.Handoff);
                case HandGoal.Scanner: return station.scan;
                case HandGoal.Till: return station.Till;
                case HandGoal.Pocket: return pocket;
                default: return null;
            }
        }

        // Los pies permanecen fuera del mueble; el alcance adapta solamente la postura.
        private void Update()
        {
            if (cashier == null) return;
            if (!CashierBusy) cashierMotion.Release();
        }

        private void OnDisable() { cashierMotion.Release(); cashierActiveUntil = 0f; }

        private Vector3 Toward()
        {
            if (station.workspace != null) return station.workspace.forward;
            Vector3 from = cashier != null ? cashierHome : station.scan.position;
            Vector3 toward = station.counter.position - from;
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
            Vector3 scan = station.scan.position, toward = Toward(), side = Vector3.Cross(Vector3.up, toward).normalized;
            foreach (var anchor in new[] { drop, bag, handoff }) anchor.rotation = Quaternion.LookRotation(toward);
            if (shop.Tasks.IsWithdrawal)
            {
                drop.position = bag.position = scan;
                handoff.position = scan;
                return;
            }
            drop.position = scan + side * .055f;
            bag.position = scan - side * .055f;
            handoff.position = scan + Vector3.up * .12f;
        }
    }
}
