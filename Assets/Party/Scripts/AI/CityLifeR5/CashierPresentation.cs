using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Cajero de una caja: lo mueve el guion del mostrador solo mientras atiende a un cliente; sin cliente espera quieto.
    public sealed class CashierPresentation : MonoBehaviour
    {
        private static readonly int Pay = Animator.StringToHash("Pay");
        [SerializeField] private ShopActivity shop;
        [SerializeField] private Animator animator;
        // Se configura en el editor; sin serializar llegaba vacío a Play y cortaba la compra con NullReference.
        [SerializeField] private PedestrianReach reach;
        [SerializeField, Tooltip("Caja que atiende (0 = la principal).")] private int lane;

        public void Configure(ShopActivity target, Animator model, int checkout = 0)
        {
            shop = target; animator = model; lane = checkout;
            reach = GetComponent<PedestrianReach>();
            if (reach == null) reach = gameObject.AddComponent<PedestrianReach>();
            reach.Configure(shop.Checkout(lane).cashierGrip);
        }

        private void Start()
        {
            if (reach == null) reach = GetComponent<PedestrianReach>();
            if (shop != null) shop.ExchangeFor(lane).BindCashier(transform, reach);
        }

        private void Update()
        {
            bool busy = shop != null && shop.ExchangeFor(lane).CashierBusy;
            if (animator != null) animator.SetBool(Pay, busy);
        }
    }
}
