using UnityEngine;

namespace Alarma.AI.CityLife
{
    [RequireComponent(typeof(PedestrianMovement), typeof(PedestrianPresentation))]
    public sealed class PedestrianActor : MonoBehaviour
    {
        private PedestrianMovement movement;
        private PedestrianPresentation presentation;
        private PedestrianRoutine routine;
        private ShopActivity shop;
        public bool Failed => routine != null && routine.State == PedestrianState.Failed;
        public PedestrianState CurrentState => routine?.State ?? PedestrianState.Inactive;
        private void Awake() { movement = GetComponent<PedestrianMovement>(); presentation = GetComponent<PedestrianPresentation>(); }
        private ShoppingPresentation shopping;
        [SerializeField] private Transform grip;
        private PedestrianReach reach;
        private Transform doorTouch, pocket;
        private Vector3 doorFacing;
        private float doorWait;
        [SerializeField] private PedestrianState visibleState;
        [SerializeField] private int walletCents;
        public void ConfigureGrip(Transform hand){grip=hand;}
        public Transform Grip=>grip;
        public int WalletCents => routine?.WalletCents ?? 0;
        public void TryLeaveVisit()
        {
            doorWait = 0f;
            routine?.TryLeaveVisit();
        }
        public bool Begin(int id, Vector3 position, ShopActivity targetShop, PedestrianSettings settings, bool shopper, int routeStart,CityTrafficController traffic,
            bool oneVisit = false, int? wallet = null)
        {
            if(targetShop==null || !targetShop.IsConfigured || traffic==null)return false;
            if (movement == null) Awake();
            if (!movement.Place(id, position, traffic)) return false;
            Prepare(targetShop);
            routine = new PedestrianRoutine(id, movement, shop.Queue, shop.CreatePlan(settings, shopper, routeStart, oneVisit, wallet, id),shop.Service);
            routine.Start(); return !Failed;
        }

        // Cliente que el jugador encuentra ya dentro: aparece en su puesto mirando productos y sigue su visita.
        public bool BeginInside(int id, ShopActivity targetShop, PedestrianSettings settings, int routeStart, CityTrafficController traffic, int wallet)
        {
            if (targetShop == null || !targetShop.IsConfigured || traffic == null) return false;
            if (movement == null) Awake();
            Prepare(targetShop);
            routine = new PedestrianRoutine(id, movement, shop.Queue, shop.CreatePlan(settings, true, routeStart, true, wallet, id), shop.Service);
            int station = routine.BeginInside();
            if (station < 0 || !movement.Place(id, shop.BrowsePoint(station).position, traffic))
            {
                routine.Reset(); routine = null;
                return false;
            }
            routine.ResumeInside();
            return !Failed;
        }

        private void Prepare(ShopActivity targetShop)
        {
            shop = targetShop; presentation.ResetView();
            shopping=GetComponent<ShoppingPresentation>();if(shopping==null)shopping=gameObject.AddComponent<ShoppingPresentation>();shopping.Configure(shop,grip);
            reach=GetComponent<PedestrianReach>();if(reach==null)reach=gameObject.AddComponent<PedestrianReach>();reach.Configure(grip);
        }
        private void Update()
        {
            if (routine == null) return;
            if (WaitAtDoor())
            {
                doorWait += Time.deltaTime;
                if (doorWait < 5f) return;
            }
            else doorWait = 0f;
            routine.Tick(Time.deltaTime);movement.Pin(routine.Interaction);
            visibleState=routine.State;walletCents=routine.Session?.WalletCents??0;
            var exchange = shop.Exchange;
            var frame = exchange.Frame(routine);
            LookAtTask(exchange);
            // En el mostrador da medio paso adelante para alcanzar sin estirarse de más.
            if (frame.CustomerApproach) movement.ApproachDoor(exchange.LeanPoint(transform.position));
            if (routine.Interaction) exchange.Drive(routine, frame, reach, Pocket);
            presentation.Refresh(routine, movement.Speed);shopping.Refresh(routine, frame);
        }

        // Mira el producto que está viendo o tomando, y en el mostrador mira la caja.
        private void LookAtTask(CounterExchange exchange)
        {
            if (routine.State == PedestrianState.Browsing && movement.HasArrived && routine.BrowsingStation >= 0)
                movement.Face(shop.ProductPoint(routine.BrowsingStation).position);
            else if (routine.State == PedestrianState.PickingUp && routine.Session != null)
                movement.Face(shop.ProductPoint(routine.Session.Station).position);
            else if (routine.Interaction)
                movement.Face(exchange.FacingPoint);
        }

        // Lado derecho de la cadera: de ahí sale y ahí vuelve el dinero.
        private Transform Pocket
        {
            get
            {
                if (pocket != null) return pocket;
                pocket = new GameObject("Bolsillo").transform;
                pocket.SetParent(transform, false);
                pocket.localPosition = new Vector3(.22f, .95f, .05f);
                return pocket;
            }
        }

        // La reserva sigue en su celda hasta que el paso esté libre. El cajero conserva su propia rutina.
        private bool WaitAtDoor()
        {
            var door = shop.Entrance;
            bool crossing = routine.State == PedestrianState.Entering || routine.State == PedestrianState.Leaving;
            if (!crossing || door == null || door.Gateway == null || door.CanPass || !movement.AtStepEnd)
            {
                if (doorTouch != null) { reach.Release(doorTouch); doorTouch = null; }
                return false;
            }
            Vector3 distance = door.Gateway.position - transform.position;
            distance.y = 0;
            if (distance.sqrMagnitude > .74f * .74f) return false;
            if (doorTouch == null)
            {
                if (!door.TryGetPushContact(transform.position, .24f, out var point, out var stand, out var facing)) return false;
                movement.Face(transform.position + facing);
                if (!reach.CanReach(point.position))
                {
                    if (!movement.ApproachDoor(stand)) return false;
                    movement.Pin(true);
                    presentation.Refresh(routine, movement.Speed);
                    return true;
                }
                doorTouch = point;
                doorFacing = facing;
            }
            movement.Face(transform.position + doorFacing);
            movement.Pin(true);
            reach.ReachSurface(doorTouch);
            if (reach.HasContact) shop.PushDoor(transform.position);
            presentation.Refresh(routine, 0f);
            return true;
        }
        public void Suspend()
        {
            if (reach != null && doorTouch != null) reach.Release(doorTouch);
            doorTouch = null;
            doorWait = 0f;
            if (routine != null) { routine.Reset(); routine = null; }
            if(shopping!=null)shopping.ResetView();
            if (movement != null) movement.Suspend(); if (presentation != null) presentation.ResetView();
        }
        private void OnDisable() => Suspend();
    }
}
