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
        private Transform grip;
        private PedestrianReach reach;
        [SerializeField] private PedestrianState visibleState;
        [SerializeField] private int walletCents;
        public void ConfigureGrip(Transform hand){grip=hand;}
        public bool Begin(int id, Vector3 position, ShopActivity targetShop, PedestrianSettings settings, bool shopper, int routeStart,CityTrafficController traffic)
        {
            if(targetShop==null || !targetShop.IsConfigured || traffic==null)return false;
            if (movement == null) Awake();
            if (!movement.Place(id, position, traffic)) return false;
            shop = targetShop; presentation.ResetView();
            shopping=GetComponent<ShoppingPresentation>();if(shopping==null)shopping=gameObject.AddComponent<ShoppingPresentation>();shopping.Configure(shop,grip);
            reach=GetComponent<PedestrianReach>();if(reach==null)reach=gameObject.AddComponent<PedestrianReach>();reach.Configure(grip);
            routine = new PedestrianRoutine(id, movement, shop.Queue, shop.CreatePlan(settings, shopper, routeStart),shop.Service);
            routine.Start(); return !Failed;
        }
        private void Update()
        {
            if (routine == null) return;
            routine.Tick(Time.deltaTime);movement.Pin(routine.Interaction);
            visibleState=routine.State;walletCents=routine.Session?.WalletCents??0;
            if(routine.Interaction || routine.State==PedestrianState.Browsing && movement.HasArrived)
                movement.Face(routine.State==PedestrianState.PickingUp || routine.State==PedestrianState.Browsing?shop.ProductPoint(routine.Session.Station).position:shop.Counter.position);
            presentation.Refresh(routine, movement.Speed);shopping.Refresh(routine);shop.RequestPassage(transform.position);
            if(routine.Interaction)reach.Reach(routine.State==PedestrianState.PickingUp?shop.ProductPoint(routine.Session.Station):shop.Counter);
        }
        public void Suspend()
        {
            if (routine != null) { routine.Reset(); routine = null; }
            if(shopping!=null)shopping.ResetView();
            if (movement != null) movement.Suspend(); if (presentation != null) presentation.ResetView();
        }
        private void OnDisable() => Suspend();
    }
}
