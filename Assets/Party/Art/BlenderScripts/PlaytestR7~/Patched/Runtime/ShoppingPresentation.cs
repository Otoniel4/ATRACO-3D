using UnityEngine;
namespace Alarma.AI.CityLife
{
    // Un objeto visible recorre estante, mano, mostrador y bolsa; no crea una compra al aparecer la bolsa.
    public sealed class ShoppingPresentation : MonoBehaviour
    {
        private GameObject product,money;private ShoppingSession current;private Transform grip;private ShopActivity shop;
        public void Configure(ShopActivity target,Transform hand){ResetView();shop=target;grip=hand;}
        public void Refresh(PedestrianRoutine routine)
        {
            var session=routine.Session;
            if(current!=session)
            {
                if(product!=null)Destroy(product);current=session;
                if(current!=null && shop.Tasks.ProductPrefab!=null)product=Instantiate(shop.Tasks.ProductPrefab);
            }
            if(current==null)return;
            if(product!=null)
            {
                product.SetActive(current.Stage<ShoppingStage.Collected);
                Transform parent=current.Stage==ShoppingStage.Reserved?shop.ProductPoint(current.Station):current.Stage==ShoppingStage.InHand?grip:current.Stage==ShoppingStage.Scanned?shop.CashierGrip:shop.Counter;
                if(product.transform.parent!=parent){product.transform.SetParent(parent,false);product.transform.localPosition=Vector3.zero;product.transform.localRotation=Quaternion.identity;}
                if(current.Stage==ShoppingStage.OnCounter && routine.State==PedestrianState.Scanning)
                    product.transform.position=Vector3.Lerp(shop.Counter.position,shop.Scan.position,Mathf.Clamp01(routine.StateSeconds/1.2f));
                if(current.Stage==ShoppingStage.Paid && routine.State==PedestrianState.ReceivingReceipt)
                    product.transform.position=Vector3.Lerp(shop.Scan.position,shop.Counter.position,Mathf.Clamp01(routine.StateSeconds/.8f));
            }
            bool offering=routine.State==PedestrianState.Paying;
            if(offering && money==null && shop.Tasks.MoneyPrefab!=null)money=Instantiate(shop.Tasks.MoneyPrefab,grip);
            if(money!=null)money.SetActive(offering);
        }
        public void ResetView(){if(product!=null)Destroy(product);if(money!=null)Destroy(money);current=null;}
        private void OnDisable()=>ResetView();
    }
}
