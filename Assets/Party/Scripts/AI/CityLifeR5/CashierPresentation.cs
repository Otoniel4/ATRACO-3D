using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Cajero del local: lo mueve el guion del mostrador mientras atiende y, entre clientes, sigue con su trabajo.
    public sealed class CashierPresentation : MonoBehaviour
    {
        private static readonly int Pay = Animator.StringToHash("Pay");
        [SerializeField] private ShopActivity shop;
        [SerializeField] private Animator animator;
        // Se configura en el editor; sin serializar llegaba vacío a Play y cortaba la compra con NullReference.
        [SerializeField] private PedestrianReach reach;
        [SerializeField] private StaffWork work;

        public void Configure(ShopActivity target, Animator model, StaffWork routine = null)
        {
            shop = target; animator = model; work = routine;
            reach = GetComponent<PedestrianReach>();
            if (reach == null) reach = gameObject.AddComponent<PedestrianReach>();
            reach.Configure(shop.CashierGrip);
        }

        private void Start()
        {
            if (reach == null) reach = GetComponent<PedestrianReach>();
            if (shop != null) shop.Exchange.BindCashier(transform, reach);
        }

        private void Update()
        {
            bool busy = shop != null && shop.Exchange.CashierBusy;
            if (work != null) work.Paused = busy;
            if (animator != null) animator.SetBool(Pay, busy);
        }
    }
}
