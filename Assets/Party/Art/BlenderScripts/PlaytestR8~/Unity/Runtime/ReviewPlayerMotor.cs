using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ReviewPlayerMotor:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewCamera view;
        [SerializeField] private WorldReviewStream world;
        private CharacterController controller;
        private Vector3 previous,spawn;
        private float vertical;
        private bool needsGround=true;
        public float Speed{get;private set;}
        public event Action<float> SpeedChanged;
        public void Configure(ReviewInput controls,ReviewCamera camera,WorldReviewStream stream,Vector3 position)
        {input=controls;view=camera;world=stream;spawn=position;transform.position=previous=position;}
        private void Awake(){controller=GetComponent<CharacterController>();previous=transform.position;}
        public void Teleport(Vector3 position)
        {
            if(controller==null)controller=GetComponent<CharacterController>();controller.enabled=false;transform.position=position;controller.enabled=true;previous=spawn=position;vertical=0;needsGround=true;
        }
        private void Update()
        {
            if(input==null || view==null || world==null)return;
            bool ready=world.ReadyAt(transform.position);
            if(ready && !view.Flying)
            {
                if(needsGround)
                {
                    Physics.SyncTransforms();if(Physics.Raycast(transform.position+Vector3.up*3,Vector3.down,out var hit,10,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore))
                    {controller.enabled=false;transform.position=hit.point+Vector3.up*.035f;controller.enabled=true;}
                    needsGround=false;previous=transform.position;
                }
                Vector2 axis=input.Active?input.Move:Vector2.zero;
                Vector3 movement=Quaternion.Euler(0,view.Yaw,0)*new Vector3(axis.x,0,axis.y);float speed=input.Run?3.6f:1.6f;
                if(movement.sqrMagnitude>.001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(movement),500*Time.deltaTime);
                if(controller.isGrounded && vertical<0)vertical=-2;else vertical-=20*Time.deltaTime;
                controller.Move((movement*speed+Vector3.up*vertical)*Time.deltaTime);
                Vector3 p=transform.position;p.x=Mathf.Clamp(p.x,-1997,1997);p.z=Mathf.Clamp(p.z,-1997,1997);
                if((p-transform.position).sqrMagnitude>0)controller.Move(p-transform.position);
                if(transform.position.y<-8)Teleport(spawn);
            }
            Vector3 delta=transform.position-previous;delta.y=0;Speed=Time.deltaTime>.00001f?delta.magnitude/Time.deltaTime:0;previous=transform.position;SpeedChanged?.Invoke(Speed);
        }
    }
}
