using UnityEngine;
namespace Alarma.AI.CityLife
{
    // Objetos que el cliente maneja en su visita: el producto del estante, los billetes, el vuelto y el número del banco.
    // Cada uno va donde dice el guion del mostrador: estante, mano del cliente, mostrador o mano del cajero.
    [DefaultExecutionOrder(150)]
    public sealed class ShoppingPresentation : MonoBehaviour
    {
        private const float MoneyScale = .6f, ChangeScale = .4f;
        private GameObject product, money, change, ticket;
        private ShoppingSession current;
        private int station = -1, lane;
        private Transform grip;
        private ShopActivity shop;
        private ExchangeFrame frame;
        public bool WaitingForContact { get; private set; }
        public Vector3? CustomerContact { get; private set; }
        public Vector3? CashierContact { get; private set; }
        public float ProductGripHeight => (productPose.Top.y - productPose.Base.y) * (shop.Tasks.Animation != null ? shop.Tasks.Animation.GripHeight : 0f);
        private readonly PropPose productPose = new PropPose(), moneyPose = new PropPose(),
            changePose = new PropPose(), ticketPose = new PropPose();

        private sealed class PropPose
        {
            public GameObject Item;
            public Transform Anchor;
            public Vector3 Start, Base, Top;
            public Quaternion Rotation, Basis, Facing;
            public float Began, Duration, HalfWidth;
            public ItemPlace Place;

            public void SetItem(GameObject item)
            {
                Item = item;
                Anchor = null;
                Duration = 0f;
                Place = ItemPlace.Hidden;
                if (item == null) return;
                var root = item.transform;
                Basis = root.localRotation;
                Facing = root.rotation * Quaternion.Inverse(Basis);
                Bounds bounds = default;
                bool found = false;
                foreach (var renderer in item.GetComponentsInChildren<Renderer>(true))
                {
                    if (renderer.gameObject != item && !renderer.gameObject.activeSelf) continue;
                    var box = renderer.localBounds;
                    for (int corner = 0; corner < 8; corner++)
                    {
                        var local = new Vector3((corner & 1) == 0 ? box.min.x : box.max.x,
                            (corner & 2) == 0 ? box.min.y : box.max.y, (corner & 4) == 0 ? box.min.z : box.max.z);
                        // Medir en los ejes verticales del juego, conservando la conversión del FBX.
                        var point = Basis * Vector3.Scale(root.InverseTransformPoint(renderer.transform.TransformPoint(local)), root.lossyScale);
                        if (found) bounds.Encapsulate(point);
                        else { bounds = new Bounds(point, Vector3.zero); found = true; }
                    }
                }
                Base = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
                Top = new Vector3(bounds.center.x, bounds.max.y, bounds.center.z);
                HalfWidth = bounds.size.x * .5f;
            }
        }

        public void Configure(ShopActivity target, Transform hand) { ResetView(); shop = target; grip = hand; }

        public void Refresh(PedestrianRoutine routine, ExchangeFrame frame)
        {
            this.frame = frame;
            // La caja se elige en la fila, después de empezar la visita: se sigue en cada cuadro para que producto, dinero y
            // boleta aparezcan en el mostrador de su caja (antes quedaban en la caja 1).
            lane = routine.Lane;
            var session = routine.Session;
            if (current != session)
            {
                ReleaseProduct();
                current = session;
                station = session?.Station ?? -1;
                if (current != null && !shop.Tasks.IsWithdrawal && shop.Tasks.ProductPrefab != null) product = shop.ClaimProduct(current);
            }
        }

        private void LateUpdate()
        {
            WaitingForContact = false;
            CustomerContact = CashierContact = null;
            if (current == null) { HideItems(); return; }
            Place(product, frame.Product, productPose);
            Place(Item(ref money, shop.Tasks.MoneyPrefab, MoneyScale, frame.Money,
                shop.Tasks.IsWithdrawal ? shop.ExchangeFor(lane).TillPosition : Pocket), frame.Money, moneyPose);
            Place(Item(ref change, shop.Tasks.MoneyPrefab, ChangeScale, frame.Change, shop.ExchangeFor(lane).TillPosition), frame.Change, changePose);
            Place(Item(ref ticket, shop.Tasks.ReceiptPrefab, 1f, frame.Ticket,
                station >= 0 ? shop.ProductPoint(station).position : Pocket), frame.Ticket, ticketPose);
        }

        private void Place(GameObject item, ItemPlace place, PropPose pose)
        {
            if (item == null) return;
            if (pose.Item != item) pose.SetItem(item);
            Transform anchor = Parent(place);
            var body = item.transform;
            // Billetes y comprobantes se guardan cuando la mano llega; una salida/cancelación limpia la visita.
            if (anchor == null)
            {
                if (item != product && IsHand(pose.Place) && current != null &&
                    frame.CustomerApproach && !Contact(pose.Place, pose.Anchor,
                        pose.Place == ItemPlace.CustomerHand ? Pocket : shop.ExchangeFor(lane).TillPosition)) return;
                item.SetActive(false); pose.Anchor = null; pose.Place = ItemPlace.Hidden; return;
            }
            var profile = shop.Tasks.Animation;
            Quaternion orientation = pose.Facing;
            if (item == product && place == ItemPlace.CashierHand) orientation *= shop.ExchangeFor(lane).ProductTilt;
            Quaternion rotation = orientation * pose.Basis;
            Vector3 gripPoint = Reference(item, pose, place);
            if (pose.Anchor != anchor)
            {
                Vector3 support = body.position + body.rotation * Quaternion.Inverse(pose.Basis) * gripPoint;
                // El objeto sigue en su apoyo/dueño hasta que la palma realmente llega al punto de traspaso.
                if (IsHand(place))
                {
                    if (IsHand(pose.Place)) Hold(pose.Place, pose.Anchor.position);
                    if (!Contact(place, anchor, support)) return;
                }
                else if (IsHand(pose.Place))
                {
                    Vector3 grasp = Reference(item, pose, pose.Place);
                    if (!Contact(pose.Place, pose.Anchor, anchor.position + orientation * (grasp - pose.Base))) return;
                }
                pose.Anchor = anchor;
                pose.Place = place;
                pose.Start = support;
                pose.Rotation = body.rotation;
                pose.Began = Time.time;
                pose.Duration = body.parent == anchor || place == ItemPlace.Shelf ? 0f
                    : Mathf.Clamp(profile != null ? profile.TransferSeconds : .25f, .1f, .35f);
                if (pose.Duration > 0f) body.SetParent(transform, true);
            }
            float t = pose.Duration > 0f ? Mathf.Clamp01((Time.time - pose.Began) / pose.Duration) : 1f;
            float eased = CounterChoreography.Blend(t);
            Quaternion interpolated = Quaternion.Slerp(pose.Rotation, rotation, eased);
            Vector3 contact = Vector3.Lerp(pose.Start, anchor.position, eased);
            // Girar alrededor del apoyo mantiene la base en la palma, incluso con la conversión de ejes del FBX.
            body.SetPositionAndRotation(contact - interpolated * Quaternion.Inverse(pose.Basis) * gripPoint, interpolated);
            if (t < 1f)
            {
                WaitingForContact = true;
                if (IsHand(place)) Hold(place, pose.Start);
            }
            if (t >= 1f && body.parent != anchor) body.SetParent(anchor, true);
            if (!item.activeSelf) item.SetActive(true);
        }

        private static bool IsHand(ItemPlace place) => place == ItemPlace.CustomerHand || place == ItemPlace.CashierHand;

        private Vector3 Reference(GameObject item, PropPose pose, ItemPlace place)
        {
            if (!IsHand(place)) return pose.Base;
            if (item == product) return Vector3.Lerp(pose.Base, pose.Top, shop.Tasks.Animation != null ? shop.Tasks.Animation.GripHeight : 0f);
            // Billetes/papel: cada persona toma un extremo distinto y las palmas no buscan el mismo centro.
            return pose.Base + Vector3.right * pose.HalfWidth * .8f * (place == ItemPlace.CustomerHand ? 1f : -1f);
        }

        private void Hold(ItemPlace who, Vector3 point)
        {
            if (who == ItemPlace.CustomerHand) CustomerContact = point;
            else if (who == ItemPlace.CashierHand) CashierContact = point;
        }

        private bool Contact(ItemPlace who, Transform hand, Vector3 point)
        {
            Hold(who, point);
            bool touches = hand != null && Vector3.Distance(hand.position, point) <= .025f;
            WaitingForContact |= !touches;
            return touches;
        }

        private Transform Parent(ItemPlace place)
        {
            switch (place)
            {
                case ItemPlace.Shelf: return station >= 0 ? shop.ProductPoint(station) : null;
                case ItemPlace.CustomerHand: return grip;
                case ItemPlace.Hidden: return null;
                default: return shop.ExchangeFor(lane).Anchor(place);
            }
        }

        // Los billetes, el vuelto y el número se crean al necesitarlos y se reutilizan en la visita.
        private Vector3 Pocket => transform.TransformPoint(new Vector3(.22f, .95f, .05f));

        private GameObject Item(ref GameObject item, GameObject prefab, float scale, ItemPlace place, Vector3 origin)
        {
            if (item != null || prefab == null || place == ItemPlace.Hidden) return item;
            item = Instantiate(prefab, transform);
            item.transform.localScale *= scale;
            item.transform.position = origin;
            item.SetActive(false);
            return item;
        }

        // Si el cliente se va sin comprar, el producto queda en su estante; si lo compró, se lo llevó.
        private void ReleaseProduct()
        {
            if (product != null && (station < 0 || product.transform.parent != shop.ProductPoint(station))) Destroy(product);
            product = null;
        }

        private void HideItems()
        {
            foreach (var item in new[] { money, change, ticket }) if (item != null) item.SetActive(false);
        }

        public void ResetView()
        {
            WaitingForContact = false;
            CustomerContact = CashierContact = null;
            if (shop != null) ReleaseProduct();
            foreach (var item in new[] { money, change, ticket }) if (item != null) Destroy(item);
            money = change = ticket = null;
            foreach (var pose in new[] { productPose, moneyPose, changePose, ticketPose }) pose.SetItem(null);
            current = null;
            station = -1;
        }

        private void OnDisable() => ResetView();
    }
}
