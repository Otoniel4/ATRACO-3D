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
        private readonly CommerceHandMotion purchaseHand = new CommerceHandMotion();
        private Transform doorTouch, pocket, streetReturn;
        private Vector3 doorFacing, doorStand;
        private float doorWait, blockedEntry;
        private float contactWait;
        private const float PalmOnPlate = .03f;
        private readonly DoorCrossing crossing = new DoorCrossing();
        private bool doorReported;
        private CommerceSupportHand doorLeft;
        private bool UsesCatalog => shop != null && shop.Tasks.Products != null && shop.Tasks.Products.Length > 0 && !shop.Tasks.IsWithdrawal;
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
            Prepare(targetShop, routeStart);
            routine = new PedestrianRoutine(id, movement, shop.Lanes, shop.CreatePlan(settings, shopper, routeStart, oneVisit, wallet, id),shop.Service);
            routine.Start(); return !Failed;
        }

        // Cliente que el jugador encuentra ya dentro: aparece en su puesto mirando productos y sigue su visita.
        public bool BeginInside(int id, ShopActivity targetShop, PedestrianSettings settings, int routeStart, CityTrafficController traffic, int wallet)
        {
            if (targetShop == null || !targetShop.IsConfigured || traffic == null) return false;
            if (movement == null) Awake();
            Prepare(targetShop, routeStart);
            routine = new PedestrianRoutine(id, movement, shop.Lanes, shop.CreatePlan(settings, true, routeStart, true, wallet, id), shop.Service);
            int station = routine.BeginInside();
            if (station < 0 || !movement.Place(id, shop.BrowsePoint(station).position, traffic))
            {
                routine.Reset(); routine = null;
                return false;
            }
            routine.ResumeInside();
            return !Failed;
        }

        private void Prepare(ShopActivity targetShop, int routeStart)
        {
            shop = targetShop; presentation.ResetView();
            streetReturn = shop.WalkRoute.Length > 0 ? shop.WalkRoute[routeStart % shop.WalkRoute.Length] : null;
            reach=GetComponent<PedestrianReach>();if(reach==null)reach=gameObject.AddComponent<PedestrianReach>();reach.Configure(grip);
            shopping=GetComponent<ShoppingPresentation>();if(shopping==null)shopping=gameObject.AddComponent<ShoppingPresentation>();shopping.Configure(shop,reach.PurchaseGrip);
        }
        private void Update()
        {
            if (routine == null) return;
            CheckEntryProgress();
            if (WaitAtDoor())
            {
                doorWait += Time.deltaTime;
                if (doorWait < 5f) return;
            }
            else doorWait = 0f;
            contactWait = shopping.WaitingForContact ? contactWait + Time.deltaTime : 0f;
            if (contactWait > 10f)
            {
                Debug.LogWarning($"Contacto bloqueado en {shop.Tasks.ShopId}, caja {routine.Lane}, estado {routine.State}: {shopping.ContactDescription}. Se cancela la visita sin dejar la fila bloqueada.", this);
                routine.CancelInteraction();
                shopping.ResetView();
                contactWait = 0f;
            }
            routine.Tick(shopping.WaitingForContact ? 0f : Time.deltaTime);movement.Pin(routine.Interaction);
            visibleState=routine.State;walletCents=routine.Session?.WalletCents??0;
            var exchange = shop.ExchangeFor(routine.Lane);
            var frame = exchange.Frame(routine);
            LookAtTask(exchange);
            // En el mostrador da medio paso adelante para alcanzar sin estirarse de más.
            if (frame.CustomerApproach) movement.ApproachDoor(exchange.LeanPoint(reach, shopping.ProductGripOffset, shopping.TwoHands));
            else if (routine.State == PedestrianState.PickingUp && routine.Session != null && !shopping.HasPickedUp)
            {
                Vector3 product = shopping.PickupContact ?? shop.ProductPoint(routine.Session.Station).position;
                Vector3 toward = Vector3.ProjectOnPlane(product - transform.position, Vector3.up).normalized;
                Vector3 stand = product - toward * .38f;
                stand.y = transform.position.y;
                movement.ApproachDoor(shopping.TwoHands ? stand : reach.AlignSurfaceStand(product, stand, toward));
            }
            if (routine.Interaction) exchange.Drive(routine, frame, reach, Pocket, purchaseHand, shopping.CustomerContact, shopping.CashierContact, shopping.ProductGripHeight, shopping.ProductGripOffset, shopping.CashierGripOffset, shopping.TwoHands);
            else if (routine.Carrying && UsesCatalog && !shopping.TwoHands)
            {
                // Caminando con el producto en una mano: el brazo sigue el clip de caminar y la mano solo lo sujeta.
                purchaseHand.Release();
                reach.CarryRelaxed();
            }
            else if (routine.Carrying && (!routine.HoldingBag || UsesCatalog))
                purchaseHand.Follow(reach, transform.TransformPoint(new Vector3(.24f, 1.22f, .28f)), 1.2f, .12f, !shop.Tasks.IsWithdrawal);
            else purchaseHand.Release();
            presentation.Refresh(routine, movement.Speed, !UsesCatalog);shopping.Refresh(routine, frame);
        }

        private void CheckEntryProgress()
        {
            var door = shop.Entrance;
            if (streetReturn == null || door == null || !door.InReach(transform.position) || routine.State != PedestrianState.Entering
                || movement.Speed > .08f
                || !door.OnSameSide(transform.position, streetReturn.position))
            {
                blockedEntry = 0f;
                return;
            }
            blockedEntry += Time.deltaTime;
            if (blockedEntry >= 8f) routine.ReturnFromEntrance();
        }

        // Mira el producto que está viendo o tomando, y en el mostrador mira la caja.
        private void LookAtTask(CounterExchange exchange)
        {
            if (routine.State == PedestrianState.Browsing && movement.HasArrived && routine.BrowsingStation >= 0)
                movement.Face(shop.ProductPoint(routine.BrowsingStation).position);
            else if (routine.State == PedestrianState.PickingUp && routine.Session != null)
                movement.Face(shop.ProductPoint(routine.Session.Station).position);
            else if (routine.Interaction)
                movement.Face(transform.position + exchange.CustomerForward);
        }

        // Lado derecho de la cadera: de ahí sale y ahí vuelve el dinero.
        private Transform Pocket
        {
            get
            {
                if (pocket == null)
                {
                    pocket = new GameObject("Bolsillo").transform;
                    pocket.SetParent(transform, false);
                }
                // Donde la mano de este personaje llega sin doblar el cuerpo.
                pocket.position = reach.PocketPoint;
                return pocket;
            }
        }

        // La reserva sigue en su celda hasta que el paso esté libre. El cajero conserva su propia rutina.
        // Frente a la puerta cerrada, DoorCrossing decide cada cuadro: girar, acercarse a la placa, extender la mano y
        // empujar (con tiempo límite en cada fase, así nunca se traba); este método solo ejecuta lo que pide.
        private bool WaitAtDoor()
        {
            var door = shop.Entrance;
            bool atDoor = AtDoorFront(door);
            if (atDoor && doorTouch == null) AcquireContact(door);
            float facing = doorTouch != null ? Vector3.Dot(transform.forward, doorFacing) : 0f;
            Vector3 stand = doorTouch != null ? reach.AlignSurfaceStand(doorTouch.position, doorStand, doorFacing) : transform.position;
            Vector3 toStand = stand - transform.position;
            toStand.y = 0f;
            var action = crossing.Tick(Time.deltaTime, atDoor && doorTouch != null, OpenEnough(door), facing,
                toStand.sqrMagnitude < .05f * .05f, Touching());
            if (crossing.Phase == DoorPhase.Idle)
            {
                ReleaseDoor();
                return false;
            }
            movement.Pin(true);
            if (action.Face) movement.Face(transform.position + doorFacing);
            bool stepping = action.Step && facing >= .9f && movement.ApproachDoor(stand);
            if (routine.Carrying && UsesCatalog)
            {
                purchaseHand.Follow(reach, transform.TransformPoint(new Vector3(.24f, 1.22f, .28f)), 1.2f, .12f);
                if (doorLeft == null) doorLeft = GetComponent<CommerceSupportHand>() ?? gameObject.AddComponent<CommerceSupportHand>();
                if (action.Reach) doorLeft.ReachSurface(doorTouch);
                shopping.Refresh(routine, shop.ExchangeFor(routine.Lane).Frame(routine));
            }
            else if (action.Reach) reach.ReachSurface(doorTouch);
            if (action.Push) shop.PushDoor(transform.position);
            ReportBlockedDoor(door);
            presentation.Refresh(routine, stepping ? movement.Speed : 0f, !UsesCatalog);
            return true;
        }

        // Le toca empujar: cruzando, con la puerta cerrada a su alcance, todavía de su lado, ya detenido (o trabado a
        // mitad de paso) y sin otro cliente entre él y la puerta (ese empuja primero).
        private bool AtDoorFront(ShopDoor door)
        {
            bool crossingState = routine.State == PedestrianState.Entering || routine.State == PedestrianState.Leaving;
            if (!crossingState || door == null || !door.InReach(transform.position) || OpenEnough(door)) return false;
            if (streetReturn != null && door.OnSameSide(transform.position, streetReturn.position) != (routine.State == PedestrianState.Entering)) return false;
            if (!movement.AtStepEnd && movement.Speed > .05f) return false;
            Vector3 toDoor = door.Gateway.position - transform.position;
            toDoor.y = 0f;
            return toDoor.sqrMagnitude < .0001f
                || !Physics.Raycast(transform.position + Vector3.up, toDoor.normalized, toDoor.magnitude, 1 << 29, QueryTriggerInteraction.Ignore);
        }

        // Camina recién con la hoja abierta del todo; si algo la frena a medio abrir, tras dos empujes pasa igual.
        private bool OpenEnough(ShopDoor door) => door != null && (door.FullyOpen || (door.CanPass && crossing.Pushes >= 2));

        // Placa de empuje de su hoja; si la puerta no la ofrece, empuja en el centro mirando hacia la puerta.
        private void AcquireContact(ShopDoor door)
        {
            if (door.TryGetPushContact(transform.position, .24f, out doorTouch, out doorStand, out doorFacing)) return;
            doorTouch = door.Handle != null ? door.Handle : door.Gateway;
            doorStand = transform.position;
            doorFacing = door.Gateway.position - transform.position;
            doorFacing.y = 0f;
            doorFacing = doorFacing.sqrMagnitude > .0001f ? doorFacing.normalized : transform.forward;
        }

        // Tres empujes seguidos sin que la puerta abra: algo bloquea la hoja (se avisa una vez).
        private void ReportBlockedDoor(ShopDoor door)
        {
            if (crossing.Pushes == 0) doorReported = false;
            if (crossing.Pushes < 3 || doorReported) return;
            doorReported = true;
            Debug.LogWarning($"La puerta de {shop.transform.parent?.name ?? shop.name} no abre tras 3 empujes de {name}: la bloquea «{door.BlockingObstacle}».", this);
        }

        // La palma está sobre la placa: la exigencia del brazo para superficies (8 mm) casi nunca se cumple y el empuje no
        // salía; a menos de PalmOnPlate la diferencia no se ve y la puerta se empuja.
        private bool Touching() => routine.Carrying && UsesCatalog
            ? doorLeft != null && doorTouch != null && doorLeft.Touches(doorTouch.position)
            : reach.HasContact
            || (doorTouch != null && (reach.PalmPosition - doorTouch.position).sqrMagnitude < PalmOnPlate * PalmOnPlate);

        private void ReleaseDoor()
        {
            if (reach != null && doorTouch != null) reach.Release(doorTouch);
            doorTouch = null;
        }

        public void Suspend()
        {
            purchaseHand.Release();
            ReleaseDoor();
            doorWait = 0f;
            blockedEntry = 0f;
            contactWait = 0f;
            streetReturn = null;
            if (routine != null) { routine.Reset(); routine = null; }
            if(shopping!=null)shopping.ResetView();
            if (movement != null) movement.Suspend(); if (presentation != null) presentation.ResetView();
        }
        private void OnDisable() => Suspend();
    }
}
