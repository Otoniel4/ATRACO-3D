using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Pool;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    public sealed class StreetPopulationDirector:MonoBehaviour
    {
        [SerializeField] private StreetCrowdData data;
        [SerializeField] private PedestrianActor[] variants=Array.Empty<PedestrianActor>();
        [SerializeField] private Transform observer;
        [SerializeField] private WorldReviewStream world;
        private readonly Dictionary<int,District> active=new Dictionary<int,District>();
        private readonly List<int> wanted=new List<int>(),expired=new List<int>();
        private ObjectPool<StreetPedestrian> pool;private int serial;private float nextUpdate;
        private sealed class District{public TrafficGraph Graph;public CityTrafficController Traffic;public readonly List<StreetPedestrian> People=new List<StreetPedestrian>();}
        public int ActiveCount{get;private set;}
        public void Configure(StreetCrowdData routes,PedestrianActor[] prefabs,Transform player,WorldReviewStream stream){data=routes;variants=prefabs;observer=player;world=stream;}
        private void Awake(){pool=new ObjectPool<StreetPedestrian>(Create,null,p=>{p.Suspend();p.gameObject.SetActive(false);},p=>Destroy(p.gameObject),true,8,24);}
        private StreetPedestrian Create(){var actor=Instantiate(variants[serial%variants.Length],transform);actor.enabled=false;actor.gameObject.SetActive(false);return actor.gameObject.AddComponent<StreetPedestrian>();}
        private void Update()
        {
            if(Time.unscaledTime<nextUpdate || data==null || observer==null || world==null)return;nextUpdate=Time.unscaledTime+.5f;
            wanted.Clear();for(int i=0;i<data.Routes.Length;i++)if(Vector3.SqrMagnitude(data.Routes[i].Center-observer.position)<90*90 && world.ReadyAt(data.Routes[i].Center))wanted.Add(i);
            wanted.Sort((a,b)=>(data.Routes[a].Center-observer.position).sqrMagnitude.CompareTo((data.Routes[b].Center-observer.position).sqrMagnitude));
            if(wanted.Count>4)wanted.RemoveRange(4,wanted.Count-4);
            expired.Clear();foreach(int key in active.Keys)if(!wanted.Contains(key))expired.Add(key);foreach(int key in expired)Release(key);
            foreach(int key in wanted)if(!active.ContainsKey(key))Spawn(key);
            ActiveCount=0;foreach(var district in active.Values)ActiveCount+=district.People.Count;
        }
        private void Spawn(int key)
        {
            StreetRoute route=data.Routes[key];var graph=ScriptableObject.CreateInstance<TrafficGraph>();graph.Cells=new TrafficCell[route.Points.Length];
            for(int i=0;i<graph.Cells.Length;i++)graph.Cells[i]=new TrafficCell{Position=route.Points[i],Links=new[]{(i+graph.Count-1)%graph.Count,(i+1)%graph.Count}};
            var root=new GameObject("Paseo de acera");root.transform.SetParent(transform,false);var traffic=root.AddComponent<CityTrafficController>();traffic.Configure(graph,.8f);traffic.ConfigureBlocker(observer);
            var district=new District{Graph=graph,Traffic=traffic};active.Add(key,district);
            for(int i=0;i<3;i++)
            {
                var actor=pool.Get();actor.gameObject.SetActive(true);int id=++serial;
                if(actor.Begin(id,route,i*route.Points.Length/3,traffic))district.People.Add(actor);else pool.Release(actor);
            }
        }
        private void Release(int key){var item=active[key];foreach(var actor in item.People)pool.Release(actor);Destroy(item.Traffic.gameObject);Destroy(item.Graph);active.Remove(key);}
        private void OnDisable(){expired.Clear();expired.AddRange(active.Keys);foreach(int key in expired)Release(key);ActiveCount=0;}
        private void OnDestroy(){pool?.Clear();}
    }
}
