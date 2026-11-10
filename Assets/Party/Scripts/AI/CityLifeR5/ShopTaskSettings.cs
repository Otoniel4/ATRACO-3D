using UnityEngine;
namespace Alarma.AI.CityLife
{
    [CreateAssetMenu(menuName="Alarma/Ciudad/Producto y caja ambiental")]
    public sealed class ShopTaskSettings : ScriptableObject
    {
        public string ShopId="Market",ProductName="Producto";
        [Min(1)] public int PriceCents=750;
        [Min(0)] public int InitialStock=60;
        [Min(0)] public int CustomerWalletCents=10000;
        public bool IsWithdrawal;
        public ShopAnimationProfile Animation;
        public GameObject ProductPrefab;
        public GameObject MoneyPrefab;
        public GameObject ReceiptPrefab;
    }
}
