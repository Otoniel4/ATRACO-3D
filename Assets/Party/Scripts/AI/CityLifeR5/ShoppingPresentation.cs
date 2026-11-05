using UnityEngine;
namespace Alarma.AI.CityLife
{
    // Objetos que el cliente maneja en su visita: el producto del estante, los billetes, el vuelto y el número del banco.
    // Cada uno va donde dice el guion del mostrador: estante, mano del cliente, mostrador o mano del cajero.
    public sealed class ShoppingPresentation : MonoBehaviour
    {
        private const float MoneyScale = .6f, ChangeScale = .4f;
        private GameObject product, money, change, ticket;
        private ShoppingSession current;
        private int station = -1;
        private Transform grip;
        private ShopActivity shop;

        public void Configure(ShopActivity target, Transform hand) { ResetView(); shop = target; grip = hand; }

        public void Refresh(PedestrianRoutine routine, ExchangeFrame frame)
        {
            var session = routine.Session;
            if (current != session)
            {
                ReleaseProduct();
                current = session;
                station = session?.Station ?? -1;
                if (current != null && !shop.Tasks.IsWithdrawal && shop.Tasks.ProductPrefab != null) product = shop.ClaimProduct(current);
            }
            if (current == null) { HideItems(); return; }
            Place(product, frame.Product);
            Place(Item(ref money, shop.Tasks.MoneyPrefab, MoneyScale), frame.Money);
            Place(Item(ref change, shop.Tasks.MoneyPrefab, ChangeScale), frame.Change);
            Place(Item(ref ticket, shop.Tasks.ReceiptPrefab, 1f), frame.Ticket);
        }

        private void Place(GameObject item, ItemPlace place)
        {
            if (item == null) return;
            Transform parent = Parent(place);
            item.SetActive(parent != null);
            if (parent == null || item.transform.parent == parent) return;
            item.transform.SetParent(parent, false);
            item.transform.localPosition = Vector3.zero;
            item.transform.localRotation = Quaternion.identity;
        }

        private Transform Parent(ItemPlace place)
        {
            switch (place)
            {
                case ItemPlace.Shelf: return station >= 0 ? shop.ProductPoint(station) : null;
                case ItemPlace.CustomerHand: return grip;
                case ItemPlace.Hidden: return null;
                default: return shop.Exchange.Anchor(place);
            }
        }

        // Los billetes, el vuelto y el número se crean al necesitarlos y se reutilizan en la visita.
        private GameObject Item(ref GameObject item, GameObject prefab, float scale)
        {
            if (item != null || prefab == null) return item;
            item = Instantiate(prefab, transform);
            item.transform.localScale *= scale;
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
            if (shop != null) ReleaseProduct();
            foreach (var item in new[] { money, change, ticket }) if (item != null) Destroy(item);
            money = change = ticket = null;
            current = null;
            station = -1;
        }

        private void OnDisable() => ResetView();
    }
}
