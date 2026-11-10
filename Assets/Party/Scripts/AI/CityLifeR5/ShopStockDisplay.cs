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
            int index=session.Station;if(displayed[index]==null)displayed[index]=MakeProduct(index);return displayed[index];
        }
        private void Refill()
        {
            if(shop==null || shop.Tasks==null || shop.Service.Stock<1)return;
            for(int i=0;i<displayed.Length;i++)if(!shop.Service.IsStationBusy(i) && (displayed[i]==null || displayed[i].transform.parent!=shop.ProductPoint(i)))displayed[i]=MakeProduct(i);
        }
        private GameObject MakeProduct(int station)
        {
            var anchor=shop.ProductPoint(station);
            var item=Instantiate(shop.Tasks.ProductPrefab,anchor);
            var parts=shop.Tasks.Animation!=null?shop.Tasks.Animation.ProductParts:null;
            Bounds bounds=default;bool found=false;
            foreach(var renderer in item.GetComponentsInChildren<Renderer>(true))
            {
                bool selected=parts==null || parts.Length==0 || Array.Exists(parts,
                    part=>renderer.name==part || renderer.name.StartsWith(part+".",StringComparison.Ordinal));
                renderer.gameObject.SetActive(selected);
                if(!selected)continue;
                if(found)bounds.Encapsulate(renderer.bounds);else {bounds=renderer.bounds;found=true;}
            }
            if(found)item.transform.position+=anchor.position-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
            return item;
        }
        private void LateUpdate()=>Refill();
        private void OnDestroy(){if(displayed!=null)foreach(var item in displayed)if(item!=null)Destroy(item);}
    }
}
