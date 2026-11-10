using System;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

namespace UnityEngine
{
    public class DefaultExecutionOrder:Attribute{public DefaultExecutionOrder(int n){}}
    public class MonoBehaviour:Object
    {
        public Transform transform;
        protected GameObject Instantiate(GameObject source,Transform parent){var g=new GameObject("Copia");g.transform.SetParent(parent,false);return g;}
    }
    public static class Time{public static float time;}
    public struct Bounds
    {
        public Vector3 center,size;
        public Vector3 min=>center-size*.5f;public Vector3 max=>center+size*.5f;
        public Bounds(Vector3 c,Vector3 s){center=c;size=s;}
        public void Encapsulate(Vector3 p){var a=min;var b=max;a=new(MathF.Min(a.x,p.x),MathF.Min(a.y,p.y),MathF.Min(a.z,p.z));b=new(MathF.Max(b.x,p.x),MathF.Max(b.y,p.y),MathF.Max(b.z,p.z));center=(a+b)*.5f;size=b-a;}
    }
    public class Renderer{public GameObject gameObject;public Transform transform=>gameObject.transform;public Bounds localBounds;}
}
namespace Alarma.AI.CityLife
{
    public class ShopAnimationProfile{public float GripHeight=1,TransferSeconds=.3f;}
    public class ShopTaskSettings{public bool IsWithdrawal;public GameObject ProductPrefab,MoneyPrefab,ReceiptPrefab;public ShopAnimationProfile Animation=new();}
    public class CounterExchange
    {
        public Transform drop=new GameObject("Drop").transform,bag=new GameObject("Bag").transform,cashier=new GameObject("Cashier").transform;
        public Quaternion ProductTilt=>Quaternion.identity;
        public Vector3 TillPosition=>bag.position;
        public Transform Anchor(ItemPlace p)=>p==ItemPlace.CashierHand?cashier:p==ItemPlace.Drop?drop:bag;
    }
    public class ShopActivity
    {
        public ShopTaskSettings Tasks=new();public CounterExchange exchange=new();public Transform shelf=new GameObject("Shelf").transform;
        public Transform ProductPoint(int i)=>shelf;
        public CounterExchange ExchangeFor(int i)=>exchange;
        public GameObject ClaimProduct(ShoppingSession s)=>null;
    }
}
static class TransferTests
{
    static int checks;const BindingFlags Flags=BindingFlags.NonPublic|BindingFlags.Instance;
    static FieldInfo Field(string n)=>typeof(ShoppingPresentation).GetField(n,Flags);
    static void Check(bool ok,string text){if(!ok)throw new Exception(text);checks++;}
    static void Same(Vector3 a,Vector3 b,string text)=>Check((a-b).magnitude<.00001f,text);
    static void Place(ShoppingPresentation v,GameObject item,ItemPlace p,string pose)
        =>typeof(ShoppingPresentation).GetMethod("Place",Flags).Invoke(v,new object[]{item,p,Field(pose).GetValue(v)});
    static GameObject Item(float height){var g=new GameObject("Objeto");g.renderer=new Renderer{gameObject=g,localBounds=new Bounds(new(0,height/2,0),new(.16f,height,.08f))};return g;}
    static void Main()
    {
        foreach(float height in new[]{.3f,.145f,.0954f,.003f,.3f,.3f})
        foreach(float yaw in new[]{0f,90f,180f,270f})
        {
            var shop=new ShopActivity();var root=new GameObject("Cliente").transform;root.rotation=Quaternion.AngleAxis(yaw,Vector3.up);
            var hand=new GameObject("Mano").transform;hand.position=new(0,1,0);
            shop.shelf.position=new(0,1,2);shop.exchange.drop.position=new(1,1,0);shop.exchange.bag.position=new(1.2f,1,0);
            var v=new ShoppingPresentation{transform=root};v.Configure(shop,hand);
            var item=Item(height);Field("product").SetValue(v,item);Field("station").SetValue(v,0);
            Place(v,item,ItemPlace.Shelf,"productPose");var start=item.transform.position;
            Place(v,item,ItemPlace.CustomerHand,"productPose");Same(start,item.transform.position,"No vuela desde estante");
            Check(v.WaitingForContact,"Espera contacto del cliente");hand.position=v.CustomerContact.Value;
            Place(v,item,ItemPlace.CustomerHand,"productPose");Time.time+=1;Place(v,item,ItemPlace.CustomerHand,"productPose");
            Same(item.transform.position+Vector3.up*height,hand.position,"Agarra la parte superior");
            start=item.transform.position;Place(v,item,ItemPlace.Drop,"productPose");Same(start,item.transform.position,"No vuela al mostrador");
            hand.position=v.CustomerContact.Value;Place(v,item,ItemPlace.Drop,"productPose");Time.time+=1;Place(v,item,ItemPlace.Drop,"productPose");
            Same(item.transform.position,shop.exchange.drop.position,"Apoya la base del producto");
            start=item.transform.position;Place(v,item,ItemPlace.CashierHand,"productPose");Same(start,item.transform.position,"Cajero debe tocar antes de tomar");
            shop.exchange.cashier.position=v.CashierContact.Value;Place(v,item,ItemPlace.CashierHand,"productPose");Time.time+=1;Place(v,item,ItemPlace.CashierHand,"productPose");
            Same(item.transform.position+Vector3.up*height,shop.exchange.cashier.position,"Palma del vendedor sobre producto");
            Place(v,item,ItemPlace.Bag,"productPose");shop.exchange.cashier.position=v.CashierContact.Value;
            Place(v,item,ItemPlace.Bag,"productPose");Time.time+=1;Place(v,item,ItemPlace.Bag,"productPose");Same(item.transform.position,shop.exchange.bag.position,"Devuelve al apoyo de recogida");
            // Dinero: el receptor toma otro extremo sin llevarse la palma del donante.
            var cash=Item(.02f);cash.transform.position=new(2,1,0);Place(v,cash,ItemPlace.CustomerHand,"moneyPose");hand.position=v.CustomerContact.Value;
            Place(v,cash,ItemPlace.CustomerHand,"moneyPose");Time.time+=1;Place(v,cash,ItemPlace.CustomerHand,"moneyPose");
            start=cash.transform.position;var donor=hand.position;Place(v,cash,ItemPlace.CashierHand,"moneyPose");
            Same(start,cash.transform.position,"Dinero permanece con su dueño hasta contacto");Same(v.CustomerContact.Value,donor,"Donante mantiene su extremo");
            Check((v.CustomerContact.Value-v.CashierContact.Value).magnitude>.1f,"Palmas en extremos separados");
            shop.exchange.cashier.position=v.CashierContact.Value;Place(v,cash,ItemPlace.CashierHand,"moneyPose");Time.time+=1;Place(v,cash,ItemPlace.CashierHand,"moneyPose");
            Same(start,cash.transform.position,"Cambio de dueño sin salto ni giro");
        }
        Console.WriteLine("TRANSFER_CHECKS_PASSED "+checks+"; 6 tipos, 4 orientaciones; ShoppingPresentation real");
    }
}
