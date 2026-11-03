using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    // Presentación de paseo; las compras siguen usando PedestrianActor y su rutina completa.
    public sealed class StreetPedestrian:MonoBehaviour
    {
        private PedestrianMovement movement;
        private PedestrianPresentation presentation;
        private Vector3[] points;
        private int goal,direction;
        public bool Begin(int id,StreetRoute route,int index,CityTrafficController traffic)
        {
            GetComponent<PedestrianActor>().enabled=false;movement=GetComponent<PedestrianMovement>();presentation=GetComponent<PedestrianPresentation>();points=route.Points;
            if(!movement.Place(id,points[index],traffic))return false;
            direction=id%2==0?1:-1;goal=(index+direction*10+points.Length)%points.Length;
            presentation.ResetView();return Go();
        }
        private bool Go(){Vector3 p=points[goal];return movement.MoveTo(new CityPoint(p.x,p.y,p.z));}
        private void Update()
        {
            if(movement==null)return;
            if(movement.HasArrived){goal=(goal+direction*10+points.Length)%points.Length;Go();}
            presentation.WalkOnly(movement.Speed);
        }
        public void Suspend(){if(movement!=null)movement.Suspend();if(presentation!=null)presentation.ResetView();movement=null;}
        private void OnDisable()=>Suspend();
    }
}
