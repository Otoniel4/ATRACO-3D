using System;
using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    // El jugador abre puertas y persianas con E. Mientras sigue en el umbral, la puerta no se le cierra encima.
    public sealed class ReviewDoorInteraction:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private Transform player;
        [SerializeField] private ShopDoor[] doors=Array.Empty<ShopDoor>();
        [SerializeField] private ReviewSlidingDoor[] shutters=Array.Empty<ReviewSlidingDoor>();
        public bool PromptVisible{get;private set;}
        public void Configure(ReviewInput controls,Transform observer,ShopDoor[] hinged,ReviewSlidingDoor[] sliding){input=controls;player=observer;doors=hinged;shutters=sliding;}
        private void Update()
        {
            PromptVisible=false;if(player==null || input==null)return;Vector3 p=player.position;
            foreach(var door in doors)if(door!=null && door.InReach(p))Handle(door.IsOpen,door.Push);
            foreach(var shutter in shutters)if(shutter!=null && shutter.InReach(p))Handle(shutter.IsOpen,shutter.Push);
        }
        private void Handle(bool open,Action push)
        {
            if(open){push();return;}
            PromptVisible=true;if(input.InteractPressed)push();
        }
    }
}
