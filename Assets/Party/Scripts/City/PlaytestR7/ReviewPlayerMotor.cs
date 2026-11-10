using System;
using UnityEngine;
using UnityEngine.SceneManagement;
using Alarma.Core.Contracts;
namespace Alarma.City.Playtest
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ReviewPlayerMotor:MonoBehaviour
    {
        // Umbrales del Blend Tree de locomoción (CityLifeAnimatorFactory): caminar 1,6 m/s y correr 3,6 m/s.
        private const float WalkSpeed=1.6f,RunSpeed=3.6f,Acceleration=9f,Deceleration=12f,TurnSpeed=720f,Gravity=20f;
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewCamera view;
        [SerializeField] private MonoBehaviour worldSource; // implementa IPlayableWorld
        private IPlayableWorld world;
        private CharacterController controller;
        private Vector3 spawn,planar;
        private float vertical;
        private bool needsGround=true;
        private bool doorLocked;
        private Vector3 doorDirection, doorFacing;
        public float Speed{get;private set;}
        // Apuntando: el cuerpo mira hacia la cámara, camina de costado más despacio y no corre.
        public bool FaceView{get;set;}
        // Quieto mientras dura una acción de cuerpo completo (forzar con la palanca, abrir con la ganzúa, colocar la termita).
        public bool HoldStill{get;set;}
        private const float AlignSeconds=.3f;
        private Pose alignTarget;private float alignLeft;
        // Lo pide un objeto que necesita que el jugador se pare en un lugar (bridas: detrás de la persona arrodillada).
        public void AlignTo(Pose pose){alignTarget=pose;alignLeft=AlignSeconds;}
        public event Action<float> SpeedChanged;
        public bool DoorInteractionActive => doorLocked;
        public float BodyRadius => controller != null ? controller.radius : .24f;
        public Vector3 MoveDirection => Quaternion.Euler(0, view != null ? view.Yaw : 0, 0)
            * new Vector3(input != null ? input.Move.x : 0, 0, input != null ? input.Move.y : 0);

        public bool BeginDoorInteraction()
        {
            if (doorLocked || needsGround || controller == null || !controller.enabled) return false;
            doorLocked = true;
            planar = Vector3.zero;
            return true;
        }

        public void GuideDoorInteraction(Vector3 delta, Vector3 facing)
        {
            if (!doorLocked) return;
            doorDirection = Vector3.ClampMagnitude(delta / Mathf.Max(Time.deltaTime, .001f), 1.25f);
            doorFacing = facing;
        }

        public void EndDoorInteraction()
        {
            doorLocked = false;
            doorDirection = doorFacing = planar = Vector3.zero;
        }
        public void Configure(ReviewInput controls,ReviewCamera camera,IPlayableWorld playable,Vector3 position)
        {input=controls;view=camera;world=playable;worldSource=playable as MonoBehaviour;spawn=position;transform.position=position;}
        private void Awake(){controller=GetComponent<CharacterController>();world??=worldSource as IPlayableWorld;spawn=transform.position;}
        public void Teleport(Vector3 position)
        {
            EndDoorInteraction();
            if(controller==null)controller=GetComponent<CharacterController>();controller.enabled=false;transform.position=position;controller.enabled=true;planar=Vector3.zero;vertical=0;needsGround=true;
        }
        private void Update()
        {
            if(input==null || view==null || world==null)return;
            if(!world.ReadyAt(transform.position)){planar=Vector3.zero;Publish(0);return;}
            if(needsGround)
            {
                Physics.SyncTransforms();
                if(!ReviewPlayerGrounding.TryResolve(gameObject.scene.GetPhysicsScene(),transform.position,
                    controller.height,controller.radius,controller.slopeLimit,out var grounded,out _))
                {planar=Vector3.zero;Publish(0);return;}
                controller.enabled=false;transform.position=grounded;controller.enabled=true;spawn=grounded;vertical=0;
                needsGround=false;
            }
            Vector3 direction = doorLocked ? doorFacing : input.Active ? MoveDirection : Vector3.zero;
            // Arranque y frenado graduales: sin saltos de velocidad ni pies que patinan al soltar las teclas.
            if(alignLeft>0f && !doorLocked)
            {
                // Se desliza hasta el punto pedido en AlignSeconds y gira hacia donde se pide.
                Vector3 gap=alignTarget.position-transform.position;gap.y=0;
                planar=gap/Mathf.Max(alignLeft,Time.deltaTime);alignLeft-=Time.deltaTime;
                transform.rotation=Quaternion.RotateTowards(transform.rotation,alignTarget.rotation,TurnSpeed*2f*Time.deltaTime);
            }
            else
            {
                Vector3 target = doorLocked ? doorDirection : HoldStill ? Vector3.zero : direction * (FaceView ? WalkSpeed * .6f : input.Run ? RunSpeed : WalkSpeed);
                planar = doorLocked ? target : Vector3.MoveTowards(planar, target,
                    (target.sqrMagnitude > planar.sqrMagnitude ? Acceleration : Deceleration) * Time.deltaTime);
                if(FaceView && !doorLocked)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.Euler(0,view.Yaw,0),TurnSpeed*Time.deltaTime);
                else if(direction.sqrMagnitude>.001f)transform.rotation=Quaternion.RotateTowards(transform.rotation,Quaternion.LookRotation(direction),TurnSpeed*Time.deltaTime);
            }
            if(controller.isGrounded && vertical<0)vertical=-2;else vertical-=Gravity*Time.deltaTime;
            Physics.SyncTransforms();controller.Move((planar+Vector3.up*vertical)*Time.deltaTime);
            Vector3 p=transform.position;float limit=world.HalfSize;p.x=Mathf.Clamp(p.x,-limit,limit);p.z=Mathf.Clamp(p.z,-limit,limit);
            if((p-transform.position).sqrMagnitude>0)controller.Move(p-transform.position);
            if(transform.position.y<-8){Teleport(spawn);return;}
            // Contra una pared la velocidad real baja y la animación también, sin correr en el sitio.
            Vector3 real=controller.velocity;real.y=0;
            Publish(Mathf.Min(planar.magnitude,real.magnitude+.25f));
        }
        private void Publish(float speed){Speed=speed;SpeedChanged?.Invoke(speed);}
    }
}
