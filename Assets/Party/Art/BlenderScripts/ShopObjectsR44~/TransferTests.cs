using System;
using System.IO;
using System.Text.Json;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

static class Transfers44
{
    const BindingFlags Flags=BindingFlags.NonPublic|BindingFlags.Instance;
    static FieldInfo Field(string n)=>typeof(ShoppingPresentation).GetField(n,Flags);
    static int checks;
    static void Check(bool value,string text){if(!value)throw new Exception(text);checks++;}
    static Vector3 V(JsonElement a)=>new(a.GetProperty("x").GetSingle(),a.GetProperty("y").GetSingle(),a.GetProperty("z").GetSingle());
    static void Place(ShoppingPresentation v,GameObject item,ItemPlace place)=>typeof(ShoppingPresentation).GetMethod("Place",Flags).Invoke(v,new object[]{item,place,Field("productPose").GetValue(v)});
    static void Main()
    {
        using var catalog=JsonDocument.Parse(File.ReadAllText("Assets/Party/Art/Props/ShopObjects/catalog.json"));
        foreach(var row in catalog.RootElement.GetProperty("items").EnumerateArray())
        foreach(float yaw in new[]{0f,90f,180f,270f})
        foreach(bool reflected in new[]{false,true})
        {
            Time.time=1;
            var root=new GameObject("Customer");var right=new GameObject("Palm").transform;
            var actor=root.AddComponent<PedestrianReach>();
            var customerSupport=root.AddComponent<CommerceSupportHand>();
            var shop=new ShopActivity();var seller=new GameObject("Seller");
            shop.exchange.CashierHand=seller.AddComponent<PedestrianReach>();
            var sellerSupport=seller.AddComponent<CommerceSupportHand>();
            var definition=new ShopProductDefinition{Id=row.GetProperty("id").GetString(),Support=V(row.GetProperty("support")),RightGrip=V(row.GetProperty("right")),LeftGrip=V(row.GetProperty("left")),
                Fingers=V(row.GetProperty("fingers")),PalmNormal=V(row.GetProperty("normal")),LeftFingers=V(row.GetProperty("leftFingers")),LeftNormal=V(row.GetProperty("leftNormal")),TwoHands=row.GetProperty("twoHands").GetBoolean()};
            root.transform.rotation=Quaternion.AngleAxis(yaw,Vector3.up);
            if(reflected)
            {
                definition.RightGrip.x=-definition.RightGrip.x;definition.LeftGrip.x=-definition.LeftGrip.x;
                definition.PalmNormal.x=-definition.PalmNormal.x;definition.LeftNormal.x=-definition.LeftNormal.x;
            }
            seller.transform.rotation=Quaternion.AngleAxis(yaw+180,Vector3.up);
            shop.shelf.rotation=root.transform.rotation;shop.shelf.position=new(0,1,2);
            shop.exchange.drop.position=new(0,1,1);shop.exchange.bag.position=new(.12f,1,1);
            var item=new GameObject(definition.Id);item.AddComponent<ShopProductInstance>().Definition=definition;
            item.transform.SetParent(shop.shelf,false);item.transform.localRotation=Quaternion.identity;
            item.renderer=new Renderer{gameObject=item,localBounds=new Bounds(new(0,.15f,0),new(.3f,.3f,.3f))};
            var view=new ShoppingPresentation{transform=root.transform};view.Configure(shop,right);Field("product").SetValue(view,item);Field("station").SetValue(view,0);
            Place(view,item,ItemPlace.Shelf);
            if(definition.TwoHands)
            {
                var heading=root.transform.rotation;
                var firstGrip=view.ProductGripOffset;
                root.transform.rotation=Quaternion.AngleAxis(180,Vector3.up)*heading;
                Check((view.ProductGripOffset-firstGrip).magnitude>.1f,"Antes del contacto corrige el lado mientras gira");
                root.transform.rotation=heading;
                Check((view.ProductGripOffset-firstGrip).magnitude<.00001f,"No fija prematuramente el agarre");
            }
            foreach(var destination in new[]{ItemPlace.CustomerHand,ItemPlace.Drop,ItemPlace.CashierHand,ItemPlace.Bag,ItemPlace.CustomerHand})
            {
                var start=item.transform.position;
                Place(view,item,destination);
                Check((item.transform.position-start).magnitude<.00001f,"No mueve objeto antes del contacto: "+definition.Id);
                for(int wait=0;wait<150;wait++)
                {
                    Time.time+=1f/60f; Place(view,item,destination);
                    Check((item.transform.position-start).magnitude<.00001f,"Ni el tiempo agotado autoriza un salto: "+definition.Id);
                }
                if(view.CustomerContact.HasValue)right.position=view.CustomerContact.Value;
                if(view.CashierContact.HasValue)shop.exchange.cashier.position=view.CashierContact.Value;
                if(definition.TwoHands)
                {
                    customerSupport.Contact=sellerSupport.Contact=false;
                    start=item.transform.position;Place(view,item,destination);
                    Check((item.transform.position-start).magnitude<.00001f,"Espera también el apoyo izquierdo");
                    customerSupport.Contact=sellerSupport.Contact=true;
                }
                Place(view,item,destination);
                Vector3 previous=item.transform.position;
                for(int f=0;f<24;f++)
                {
                    Time.time+=1f/60f;Place(view,item,destination);
                    Check((item.transform.position-previous).magnitude<.025f,"Continuidad de posición "+definition.Id);
                    previous=item.transform.position;
                }
                if(destination==ItemPlace.Drop||destination==ItemPlace.Bag)
                {
                    var support=item.transform.position+item.transform.rotation*definition.Support;
                    var target=destination==ItemPlace.Drop?shop.exchange.drop.position:shop.exchange.bag.position;
                    Check((support-target).magnitude<.00001f,"La base queda sobre el mostrador");
                }
                Check(item.name==definition.Id,"Conserva identidad del objeto");
                if(destination==ItemPlace.CustomerHand) Check(view.HasPickedUp,"Detiene acercamiento de pies cuando ya lo sostiene");
                if(destination==ItemPlace.CustomerHand)
                {
                    var beforeTurn=item.transform.position;var heading=root.transform.rotation;
                    root.transform.rotation=Quaternion.AngleAxis(180,Vector3.up)*heading;
                    Place(view,item,destination);
                    Check((item.transform.position-beforeTurn).magnitude<.00001f,"Girar no cambia el extremo agarrado");
                    root.transform.rotation=heading;
                    Field("orientCarriedProduct").SetValue(view,true);
                    root.transform.rotation=Quaternion.AngleAxis(90,Vector3.up)*heading;
                    for(int turn=0;turn<100;turn++)
                    {
                        var beforeMove=item.transform.position;
                        Time.time+=Time.deltaTime;Place(view,item,destination);
                        var pose=Field("productPose").GetValue(view);
                        var held=(Vector3)typeof(ShoppingPresentation).GetMethod("Reference",Flags).Invoke(view,new object[]{item,pose,destination});
                        Check((item.transform.position+item.transform.rotation*held-right.position).magnitude<.00001f,"Gira alrededor de la palma sin soltar contacto");
                        Check((item.transform.position-beforeMove).magnitude<.02f,"Giro transportado sin salto");
                    }
                    Field("orientCarriedProduct").SetValue(view,false);
                    root.transform.rotation=heading;
                }
            }
        }
        Console.WriteLine("R44_TRANSFER_CHECKS "+checks+"; 18 objetos, 4 orientaciones, ejes normales/reflejados, cinco cambios de apoyo y ambas manos");
    }
}
