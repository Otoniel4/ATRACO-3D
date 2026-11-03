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
        public bool Begin(int id, Vector3 position, ShopActivity targetShop, PedestrianSettings settings, bool shopper, int routeStart)
        {
            if (movement == null) Awake();
            if (!movement.Place(position, settings.WalkingSpeed, 20 + id % 50)) return false;
            shop = targetShop; presentation.ResetView();
            routine = new PedestrianRoutine(id, movement, shop.Queue, shop.CreatePlan(settings, shopper, routeStart));
            routine.Purchased += shop.RecordPurchase; routine.Start(); return !Failed;
        }
        private void Update()
        {
            if (routine == null) return;
            routine.Tick(Time.deltaTime); presentation.Refresh(routine, movement.Speed); shop.RequestPassage(transform.position);
        }
        public void Suspend()
        {
            if (routine != null) { routine.Purchased -= shop.RecordPurchase; routine.Reset(); routine = null; }
            if (movement != null) movement.Suspend(); if (presentation != null) presentation.ResetView();
        }
        private void OnDisable() => Suspend();
    }
}
