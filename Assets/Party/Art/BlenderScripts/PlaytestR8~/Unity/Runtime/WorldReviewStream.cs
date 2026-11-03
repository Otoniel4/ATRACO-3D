using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
namespace Alarma.City.Playtest
{
    // Cada recurso representa una parte de ciudad; nunca instancia los 16 km² de una vez.
    [DefaultExecutionOrder(-400)]
    public sealed class WorldReviewStream:MonoBehaviour
    {
        [SerializeField] private WorldReviewData data;
        [SerializeField] private Transform observer;
        private readonly Dictionary<int,GameObject> loaded=new Dictionary<int,GameObject>();
        private readonly HashSet<int> pending=new HashSet<int>();
        private readonly HashSet<int> failed=new HashSet<int>();
        private readonly List<int> wanted=new List<int>();
        private float nextRefresh,nextUnload;
        private bool released;
        public int LoadedCount=>loaded.Count;
        public int PendingCount=>pending.Count;
        public int FailedCount=>failed.Count;
        public WorldReviewData Data=>data;
        public void Configure(WorldReviewData world,Transform focus){data=world;observer=focus;}
        private void Start(){nextUnload=Time.unscaledTime+30;}
        private static float DistanceSquared(Bounds bounds,Vector3 position)
        {Vector3 c=bounds.center,s=bounds.extents;float x=Mathf.Max(0,Mathf.Abs(position.x-c.x)-s.x),z=Mathf.Max(0,Mathf.Abs(position.z-c.z)-s.z);return x*x+z*z;}
        public bool ReadyAt(Vector3 position)
        {
            if(data==null || released)return false;
            for(int i=0;i<data.Cells.Length;i++)if((data.Cells[i].Always || DistanceSquared(data.Cells[i].Bounds,position)<1600) && !loaded.ContainsKey(i))return false;
            return true;
        }
        private void Update()
        {
            if(data==null || observer==null || released || Time.unscaledTime<nextRefresh)return;
            nextRefresh=Time.unscaledTime+.25f;wanted.Clear();Vector3 p=observer.position;
            for(int i=0;i<data.Cells.Length;i++)
            {
                float distance=DistanceSquared(data.Cells[i].Bounds,p);
                if(data.Cells[i].Always || distance<data.LoadRadius*data.LoadRadius)wanted.Add(i);
                else if(distance>data.UnloadRadius*data.UnloadRadius && loaded.TryGetValue(i,out GameObject instance))
                {Destroy(instance);loaded.Remove(i);}
            }
            wanted.Sort((a,b)=> {if(data.Cells[a].Always!=data.Cells[b].Always)return data.Cells[a].Always?-1:1;return DistanceSquared(data.Cells[a].Bounds,p).CompareTo(DistanceSquared(data.Cells[b].Bounds,p));});
            foreach(int i in wanted)if(pending.Count<data.ConcurrentLoads && !loaded.ContainsKey(i) && !pending.Contains(i) && !failed.Contains(i))StartCoroutine(Load(i));
            if(Time.unscaledTime>nextUnload && pending.Count==0){nextUnload=Time.unscaledTime+30;Resources.UnloadUnusedAssets();}
        }
        private IEnumerator Load(int index)
        {
            pending.Add(index);WorldReviewCell cell=data.Cells[index];ResourceRequest request=Resources.LoadAsync<GameObject>(cell.Resource);yield return request;
            pending.Remove(index);if(released)yield break;
            GameObject prefab=request.asset as GameObject;
            if(prefab==null){failed.Add(index);Debug.LogError("Falta una parte de ciudad: "+cell.Resource,this);yield break;}
            if(!cell.Always && DistanceSquared(cell.Bounds,observer.position)>data.UnloadRadius*data.UnloadRadius)yield break;
            var instance=Instantiate(prefab,cell.Origin,Quaternion.identity,transform);instance.name=cell.Resource.Substring(cell.Resource.LastIndexOf('/')+1);loaded.Add(index,instance);
            foreach(var roof in instance.GetComponentsInChildren<ReviewRoof>(true))roof.Configure(observer);
        }
        private void OnDestroy(){released=true;StopAllCoroutines();}
    }
}
