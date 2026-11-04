using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class CashierPresentation : MonoBehaviour
    {
        [SerializeField] private ShopActivity shop;
        [SerializeField] private Animator animator;
        // Se configura en el editor; sin serializar llegaba vacío a Play y cortaba la compra con NullReference.
        [SerializeField] private PedestrianReach reach;
        private float until;
        private static readonly int Pay = Animator.StringToHash("Pay");
        private void Awake() { if (reach == null) reach = GetComponent<PedestrianReach>(); }
        public void Configure(ShopActivity target, Animator model) { Unsubscribe(); shop = target; animator = model;reach=GetComponent<PedestrianReach>();if(reach==null)reach=gameObject.AddComponent<PedestrianReach>();reach.Configure(shop.CashierGrip); if (isActiveAndEnabled) Subscribe(); }
        private void Subscribe() { if (shop != null) shop.Transaction += OnTransaction; }
        private void Unsubscribe() { if (shop != null) shop.Transaction -= OnTransaction; }
        private void OnEnable() => Subscribe();
        private void OnDisable() => Unsubscribe();
        private void OnTransaction(ShoppingSession session,ShopAction action) {if(action==ShopAction.Placed || action==ShopAction.Scanned || action==ShopAction.Paid || action==ShopAction.Receipt){until=Time.time+1.4f;reach.Reach(shop.Scan,1.4f);}}
        private void Update() { if (animator != null) animator.SetBool(Pay, Time.time < until); }
    }
}
