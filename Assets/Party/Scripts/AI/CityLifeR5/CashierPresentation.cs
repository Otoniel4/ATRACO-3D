using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Cajero de una caja: lo mueve el guion del mostrador solo mientras atiende a un cliente; sin cliente espera quieto.
    // Queda parado en su clip de reposo: el tronco y la mano los lleva PedestrianReach (el clip de pagar abría las
    // piernas en zancada detrás del mueble).
    public sealed class CashierPresentation : MonoBehaviour
    {
        [SerializeField] private ShopActivity shop;
        // Se configura en el editor; sin serializar llegaba vacío a Play y cortaba la compra con NullReference.
        [SerializeField] private PedestrianReach reach;
        [SerializeField, Tooltip("Caja que atiende (0 = la principal).")] private int lane;

        public void Configure(ShopActivity target, int checkout = 0)
        {
            shop = target; lane = checkout;
            reach = GetComponent<PedestrianReach>();
            if (reach == null) reach = gameObject.AddComponent<PedestrianReach>();
            reach.Configure(shop.Checkout(lane).cashierGrip);
        }

        private void Start()
        {
            if (reach == null) reach = GetComponent<PedestrianReach>();
            if (shop != null) shop.ExchangeFor(lane).BindCashier(transform, reach);
        }
    }
}
