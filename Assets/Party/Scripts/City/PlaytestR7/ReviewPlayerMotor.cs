using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ReviewPlayerMotor:MonoBehaviour
    {
        // Umbrales del Blend Tree de locomoción (CityLifeAnimatorFactory): caminar 1,6 m/s y correr 3,6 m/s.
        private const float WalkSpeed=1.6f,RunSpeed=3.6f,Acceleration=9f,Deceleration=12f,TurnSpeed=720f,Gravity=20f;
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewCamera view;
        [SerializeField] private WorldReviewStream world;
        private CharacterController controller;
        private Vector3 spawn,planar;
        private float vertical;
        private bool needsGround=true;
        public float Speed{get;private set;}
        public event Action<float> SpeedChanged;
        public void Configure(ReviewInput controls,ReviewCamera camera,WorldReviewStream stream,Vector3 position)
        {input=controls;view=camera;world=stream;spawn=position;transform.position=position;}
        private void Awake(){controller=GetComponent<CharacterController>();}
        public void Teleport(Vector3 position)
        {
            if(controller==null)controller=GetComponent<CharacterController>();controller.enabled=false;transform.position=position;controller.enabled=true;spawn=position;planar=Vector3.zero;vertical=0;needsGround=true;
        }
        private void Update()
        {
            if(input==null || view==null || world==null)return;
            if(!world.ReadyAt(transform.position) || view.Flying){planar=Vector3.zero;Publish(0);return;}
            if(needsGround)
            {
                Physics.SyncTransforms();if(Physics.Raycast(transform.position+Vector3.up*3,Vector3.down,out var hit,10,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore))
                {controller.enabled=false;transform.position=hit.point+Vector3.up*.035f;controller.enabled=true;}
                needsGround=false;
            }
            Vector2 axis=input.Active?input.Move:Vector2.zero;
            Vector3 direction=Quaternion.Euler(0,view.Yaw,0)*new Vector3(axis.x,0,axis.y);
            // Arranque y frenado graduales: sin saltos de velocidad ni pies que patinan al soltar las teclas.
            Vector3 target=direction*(input.Run?RunSpeed:WalkSpeed);
            planar=Vector3.MoveTowards(planar,target,(target.sqrMagnitude>planar.sqrMagnitude?Acceleration:Deceleration)*Time.deltaTime);
            if(direction.sqrMagnitude>.001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(direction),TurnSpeed*Time.deltaTime);
            if(controller.isGrounded && vertical<0)vertical=-2;else vertical-=Gravity*Time.deltaTime;
            Physics.SyncTransforms();controller.Move((planar+Vector3.up*vertical)*Time.deltaTime);
            Vector3 p=transform.position;p.x=Mathf.Clamp(p.x,-1497,1497);p.z=Mathf.Clamp(p.z,-1497,1497);
            if((p-transform.position).sqrMagnitude>0)controller.Move(p-transform.position);
            if(transform.position.y<-8){Teleport(spawn);return;}
            // Contra una pared la velocidad real baja y la animación también, sin correr en el sitio.
            Vector3 real=controller.velocity;real.y=0;
            Publish(Mathf.Min(planar.magnitude,real.magnitude+.25f));
        }
        private void Publish(float speed){Speed=speed;SpeedChanged?.Invoke(speed);}
    }
}
