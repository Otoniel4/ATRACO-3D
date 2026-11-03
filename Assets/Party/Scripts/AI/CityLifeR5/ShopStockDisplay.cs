using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    public sealed class ShopStockDisplay:MonoBehaviour
    {
        private ShopActivity shop;private GameObject[] displayed;
        public void Configure(ShopActivity target){shop=target;displayed=new GameObject[shop.StationCount];}
        private void Start(){if(shop==null)Configure(GetComponent<ShopActivity>());Refill();}
        public GameObject Claim(ShoppingSession session)
        {
            if(shop==null)Configure(GetComponent<ShopActivity>());
            int index=session.Station;if(displayed[index]==null)displayed[index]=Instantiate(shop.Tasks.ProductPrefab,shop.ProductPoint(index));return displayed[index];
        }
        private void Refill()
        {
            if(shop==null || shop.Tasks==null || shop.Service.Stock<1)return;
            for(int i=0;i<displayed.Length;i++)if(!shop.Service.IsStationBusy(i) && (displayed[i]==null || displayed[i].transform.parent!=shop.ProductPoint(i)))displayed[i]=Instantiate(shop.Tasks.ProductPrefab,shop.ProductPoint(i));
        }
        private void LateUpdate()=>Refill();
        private void OnDestroy(){if(displayed!=null)foreach(var item in displayed)if(item!=null)Destroy(item);}
    }
}
