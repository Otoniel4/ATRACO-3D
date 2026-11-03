using System;
using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    public sealed class ReviewDoorAccess:MonoBehaviour
    {
        [SerializeField] private Transform player;
        [SerializeField] private AutomaticShopDoor[] doors=Array.Empty<AutomaticShopDoor>();
        [SerializeField] private ReviewSlidingDoor[] shutters=Array.Empty<ReviewSlidingDoor>();
        public void Configure(Transform observer,AutomaticShopDoor[] hinged,ReviewSlidingDoor[] sliding){player=observer;doors=hinged;shutters=sliding;}
        private void Update(){if(player==null)return;foreach(var door in doors)if(door!=null)door.RequestNear(player.position);foreach(var shutter in shutters)if(shutter!=null)shutter.RequestNear(player.position);}
    }
}
