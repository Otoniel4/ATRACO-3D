using System;
using System.IO;
using System.Linq;
using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    // Registra lo observado durante la prueba del usuario; no mueve al jugador ni declara pruebas que no ocurrieron.
    public sealed class ReviewRuntimeChecks:MonoBehaviour
    {
        [Serializable] private sealed class Evidence
        {
            public string version="playtest-r8-1";
            public bool zoneLoaded,walkingObserved,runningObserved;
            public int maximumNpcCount;
            public float observedWalkFootMotion,observedRunFootMotion;
        }
        [SerializeField] private string folder;
        [SerializeField] private WorldReviewStream world;
        [SerializeField] private ReviewPlayerMotor player;
        [SerializeField] private ReviewCharacterView view;
        [SerializeField] private CityPopulationDirector buyers;
        [SerializeField] private StreetPopulationDirector walkers;
        private readonly Evidence evidence=new Evidence();private Vector3 lastFoot;private Animator lastAnimator;private Transform foot;private bool sampled;private float nextSave;
        public void Configure(string path,WorldReviewStream stream,ReviewPlayerMotor motor,ReviewCharacterView character,CityPopulationDirector shopping,StreetPopulationDirector street)
        {folder=path;world=stream;player=motor;view=character;buyers=shopping;walkers=street;}
        private void Update()
        {
            if(world==null || player==null)return;evidence.zoneLoaded=world.ReadyAt(player.transform.position);
            evidence.maximumNpcCount=Mathf.Max(evidence.maximumNpcCount,(buyers!=null?buyers.ActiveCount:0)+(walkers!=null?walkers.ActiveCount:0));
            var animator=view.CurrentAnimator;
            if(animator!=null)
            {
                if(lastAnimator!=animator){foot=animator.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name=="LeftFoot");sampled=false;lastAnimator=animator;}
                if(foot!=null)
                {
                    Vector3 p=animator.transform.InverseTransformPoint(foot.position);float distance=sampled && lastAnimator==animator?(p-lastFoot).magnitude:0;
                    if(player.Speed>.5f && player.Speed<2.5f){evidence.observedWalkFootMotion+=distance;evidence.walkingObserved=evidence.observedWalkFootMotion>.12f;}
                    if(player.Speed>2.8f){evidence.observedRunFootMotion+=distance;evidence.runningObserved=evidence.observedRunFootMotion>.12f;}
                    lastFoot=p;lastAnimator=animator;sampled=true;
                }
            }
            if(Time.unscaledTime>nextSave){nextSave=Time.unscaledTime+5;Save();}
        }
        private void Save(){if(!string.IsNullOrEmpty(folder) && Directory.Exists(folder))File.WriteAllText(folder+"/RuntimeReview.json",JsonUtility.ToJson(evidence,true));}
        private void OnDestroy()=>Save();
    }
}
