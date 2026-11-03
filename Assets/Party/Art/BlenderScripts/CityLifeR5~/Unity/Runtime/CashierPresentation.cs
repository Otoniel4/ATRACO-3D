using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class CashierPresentation : MonoBehaviour
    {
        [SerializeField] private ShopActivity shop;
        [SerializeField] private Animator animator;
        private float until;
        private static readonly int Pay = Animator.StringToHash("Pay");
        public void Configure(ShopActivity target, Animator model) { Unsubscribe(); shop = target; animator = model; if (isActiveAndEnabled) Subscribe(); }
        private void Subscribe() { if (shop != null) shop.PurchaseCompleted += OnPurchase; }
        private void Unsubscribe() { if (shop != null) shop.PurchaseCompleted -= OnPurchase; }
        private void OnEnable() => Subscribe();
        private void OnDisable() => Unsubscribe();
        private void OnPurchase(int count) => until = Time.time + 1.3f;
        private void Update() { if (animator != null) animator.SetBool(Pay, Time.time < until); }
    }
}
