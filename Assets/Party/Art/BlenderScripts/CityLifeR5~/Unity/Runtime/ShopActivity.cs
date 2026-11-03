using System;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class ShopActivity : MonoBehaviour
    {
        [SerializeField] private Transform[] walkRoute = Array.Empty<Transform>();
        [SerializeField] private Transform[] entryRoute = Array.Empty<Transform>();
        [SerializeField] private Transform browsePoint;
        [SerializeField] private Transform[] queuePoints = Array.Empty<Transform>();
        [SerializeField] private Transform[] exitRoute = Array.Empty<Transform>();
        private ShopQueue queue;
        [SerializeField] private int reservedVariant = 9;
        [SerializeField] private AutomaticShopDoor door;
        [SerializeField] private int purchaseCount;
        public int ReservedVariant => reservedVariant;
        public ShopQueue Queue => queue ?? (queue = new ShopQueue(Mathf.Max(1, queuePoints.Length)));
        public Transform[] WalkRoute => walkRoute;
        public int PurchaseCount => purchaseCount;
        public event Action<int> PurchaseCompleted;
        public void Configure(Transform[] walk, Transform[] entry, Transform browse, Transform[] positions, Transform[] exit)
        { walkRoute = walk; entryRoute = entry; browsePoint = browse; queuePoints = positions; exitRoute = exit; queue = null; }
        public void ConfigureStaff(int variant, AutomaticShopDoor entrance) { reservedVariant = variant; door = entrance; }
        public void RequestPassage(Vector3 position) { if (door != null) door.RequestNear(position); }
        public PedestrianPlan CreatePlan(PedestrianSettings settings, bool visitsShop, int startIndex)
        {
            return new PedestrianPlan { Walk = Points(walkRoute, startIndex), Entry = Points(entryRoute),
                Browse = Point(browsePoint), Queue = Points(queuePoints), Exit = Points(exitRoute),
                BrowseSeconds = settings.BrowseSeconds, PaySeconds = settings.PaySeconds,
                TravelTimeout = settings.TravelTimeout, QueueTimeout = settings.QueueTimeout, VisitsShop = visitsShop };
        }
        public void RecordPurchase() { purchaseCount++; PurchaseCompleted?.Invoke(purchaseCount); }
        private static CityPoint Point(Transform point)
        { Vector3 p = point != null ? point.position : Vector3.zero; return new CityPoint(p.x, p.y, p.z); }
        private static CityPoint[] Points(Transform[] source, int start = 0)
        {
            var result = new CityPoint[source.Length];
            for (int i = 0; i < source.Length; i++) result[i] = Point(source[(i + start) % source.Length]);
            return result;
        }
        private void OnDisable() { queue?.Clear(); }
    }
}
