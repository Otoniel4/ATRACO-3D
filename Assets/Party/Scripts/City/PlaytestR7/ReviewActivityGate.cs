using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    [DefaultExecutionOrder(-300)]
    public sealed class ReviewActivityGate:MonoBehaviour
    {
        [SerializeField] private WorldReviewStream world;
        [SerializeField] private Transform observer;
        [SerializeField] private CityPopulationDirector population;
        public void Configure(WorldReviewStream stream,Transform focus,CityPopulationDirector director){world=stream;observer=focus;population=director;population.enabled=false;}
        private void Update(){if(population!=null && world!=null && observer!=null)population.enabled=world.ReadyAt(observer.position);}
    }
}
