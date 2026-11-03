using System;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewBuildActivities
    {
        public static ShopActivity[] Create(string folder,string assetFolder,WorldBuildData world,PedestrianActor[] civilians,Dictionary<string,AutomaticShopDoor> doors)
        {
            var result=new List<ShopActivity>();
            foreach(var source in world.shops)
            {
                var root=new GameObject("Routine_"+source.id);root.transform.position=ReviewBuildWorld.Vector(source.origin);
                var graph=ScriptableObject.CreateInstance<TrafficGraph>();graph.Cells=source.nodes.Select(n=>new TrafficCell{Position=ReviewBuildWorld.Vector(n.v),Links=n.links}).ToArray();
                AssetDatabase.CreateAsset(graph,folder+"/Data/Traffic_"+source.id+".asset");
                var traffic=root.AddComponent<CityTrafficController>();traffic.Configure(graph,.75f);
                var shop=root.AddComponent<ShopActivity>();shop.ConfigureTraffic(traffic);
                Transform[] walk=Markers(root.transform,"Walk",source.walk,graph),entry=Markers(root.transform,"Entry",source.entry,graph),queue=Markers(root.transform,"Queue",source.queue,graph),exit=Markers(root.transform,"Exit",source.exit,graph),browse=Markers(root.transform,"Browse",source.browseStations,graph),products=Markers(root.transform,"Product",source.products,null);
                Transform counter=Marker(root.transform,"Counter",source.counter,null),scan=Marker(root.transform,"Scan",source.scan,null),receipt=Marker(root.transform,"Receipt",source.receipt,null),till=Marker(root.transform,"Till",source.till,null);
                var tasks=ScriptableObject.CreateInstance<ShopTaskSettings>();tasks.ShopId=source.id;tasks.ProductName=source.product;tasks.PriceCents=source.priceCents;
                tasks.ProductPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(assetFolder+"/Art/Props/"+source.product+".fbx");tasks.MoneyPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(assetFolder+"/Art/Props/CashNote.fbx");tasks.ReceiptPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(assetFolder+"/Art/Props/Receipt.fbx");
                if(tasks.ProductPrefab==null || tasks.MoneyPrefab==null || tasks.ReceiptPrefab==null)throw new InvalidOperationException("Faltan los productos de "+source.id);
                AssetDatabase.CreateAsset(tasks,folder+"/Data/Shop_"+source.id+".asset");shop.Configure(walk,entry,browse,queue,exit,products,counter,scan,receipt,till,tasks);
                CityTrafficGraphBuilder.Validate(graph,queue.Concat(browse));CityTrafficGraphBuilder.ValidateRoutes(graph,entry[0],walk.Concat(entry).Concat(queue).Concat(exit).Concat(browse));
                var staff=UnityEngine.Object.Instantiate(civilians[source.staffVariant]);staff.name="Dependiente_"+source.id;staff.enabled=false;staff.GetComponent<NavMeshAgent>().enabled=false;
                staff.transform.position=ReviewBuildWorld.Vector(source.staffWorld);staff.transform.rotation=Quaternion.Euler(0,source.staffYaw*Mathf.Rad2Deg,0);
                Transform grip=staff.GetComponentsInChildren<Transform>(true).First(t=>t.name.StartsWith("Grip_R6_",StringComparison.Ordinal));shop.ConfigureStaff(source.staffVariant,doors[source.id],grip);
                staff.gameObject.AddComponent<CashierPresentation>().Configure(shop,staff.GetComponentInChildren<Animator>());result.Add(shop);
            }
            return result.ToArray();
        }
        private static Transform Marker(Transform parent,string name,float[] p,TrafficGraph graph)
        {
            var obj=new GameObject(name);obj.transform.SetParent(parent,false);obj.transform.localPosition=ReviewBuildWorld.Blender(p);
            if(graph!=null){int cell=graph.Nearest(obj.transform.position,.65f);if(cell<0)throw new InvalidOperationException("Puesto fuera del grafo: "+parent.name+"/"+name);obj.transform.position=graph.Cells[cell].Position;}
            return obj.transform;
        }
        private static Transform[] Markers(Transform parent,string name,PointData[] points,TrafficGraph graph)=>points.Select((p,i)=>Marker(parent,name+"_"+i,p.v,graph)).ToArray();
    }
}
