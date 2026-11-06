using System;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.Player.Items;
namespace Alarma.City.Playtest
{
    // Cambia solo la presentación del jugador de revisión; no sustituye su controlador al cambiar de rol.
    // También da los huesos para sostener objetos: pecho, brazos y palmas (Grip_R6 en la derecha; la izquierda se crea).
    public sealed class ReviewCharacterView:MonoBehaviour,ICharacterRig,ICharacterAnimator
    {
        [SerializeField] private GameObject[] models=Array.Empty<GameObject>();
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewPlayerMotor motor;
        private static readonly int SpeedId=Animator.StringToHash("Speed");
        private GameObject visual;private Animator animator;
        public Animator CurrentAnimator=>animator;
        Animator ICharacterAnimator.Animator=>animator; // clips de uso de objetos (ItemActionAnimator)
        public PedestrianReach CurrentReach{get;private set;}
        public Transform Root=>transform;
        public Transform Chest{get;private set;}
        public Transform Spine{get;private set;}
        public Transform RightUpperArm{get;private set;}
        public Transform RightLowerArm{get;private set;}
        public Transform RightPalm{get;private set;}
        public Transform LeftUpperArm{get;private set;}
        public Transform LeftLowerArm{get;private set;}
        public Transform LeftPalm{get;private set;}
        public bool HandsBusy => motor != null && motor.DoorInteractionActive;
        public event Action RigChanged;
        public int Role{get;private set;}
        public void Configure(ReviewInput controls,ReviewPlayerMotor movement,GameObject[] variants){input=controls;motor=movement;models=variants;}
        private void Start(){SelectRole(0);if(motor!=null)motor.SpeedChanged+=Animate;}
        private void Update(){if(input!=null && input.RolePressed>=0)SelectRole(input.RolePressed);}
        public void SelectRole(int index)
        {
            if(index<0 || index>=models.Length || models[index]==null)return;Role=index;
            if(visual!=null){visual.SetActive(false);Destroy(visual);}visual=Instantiate(models[index],transform);visual.transform.localPosition=Vector3.zero;visual.transform.localRotation=Quaternion.identity;
            SetLayer(visual.transform,30);animator=visual.GetComponentInChildren<Animator>();CurrentReach=visual.GetComponentInChildren<PedestrianReach>();
            if(animator!=null){animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;animator.Rebind();animator.Update(0);}
            Bounds bounds=new Bounds(transform.position,Vector3.zero);bool found=false;
            foreach(var r in visual.GetComponentsInChildren<Renderer>())if(r.enabled){if(!found){bounds=r.bounds;found=true;}else bounds.Encapsulate(r.bounds);}
            var capsule=GetComponent<CharacterController>();if(found && capsule!=null){capsule.height=Mathf.Clamp(bounds.size.y,1.5f,2.1f);capsule.center=new Vector3(0,capsule.height*.5f,0);capsule.radius=index==3?.31f:.24f;}
            FindRig();RigChanged?.Invoke();
        }
        private void FindRig()
        {
            Transform bone(HumanBodyBones b)=>RigBones.Find(visual.transform,b);
            Spine=bone(HumanBodyBones.Spine);Chest=bone(HumanBodyBones.Chest)??Spine;RightUpperArm=bone(HumanBodyBones.RightUpperArm);RightLowerArm=bone(HumanBodyBones.RightLowerArm);
            LeftUpperArm=bone(HumanBodyBones.LeftUpperArm);LeftLowerArm=bone(HumanBodyBones.LeftLowerArm);
            RightPalm=null;foreach(var t in visual.GetComponentsInChildren<Transform>(true))if(t.name.StartsWith("Grip_R6_",StringComparison.Ordinal)){RightPalm=t;break;}
            // Palma izquierda como la derecha del elenco: 6 cm más allá de la muñeca siguiendo el antebrazo y 2 cm abajo.
            var wrist=bone(HumanBodyBones.LeftHand);LeftPalm=null;
            if(wrist!=null && LeftLowerArm!=null){LeftPalm=new GameObject("Palma_L").transform;LeftPalm.SetParent(wrist,false);LeftPalm.position=wrist.position+(wrist.position-LeftLowerArm.position).normalized*.06f-Vector3.up*.02f;}
        }
        private static void SetLayer(Transform item,int layer){item.gameObject.layer=layer;foreach(Transform child in item)SetLayer(child,layer);}
        private void Animate(float speed)
        {
            // Amortiguar el parámetro mezcla caminar y correr sin cortes de un fotograma a otro.
            if(animator==null)return;animator.SetFloat(SpeedId,speed,.1f,Time.deltaTime);animator.SetFloat("WalkRate",Mathf.Clamp(speed,0,4));animator.SetBool("Browse",false);animator.SetBool("Pay",false);animator.SetBool("Carry",false);
        }
        private void OnDestroy(){if(motor!=null)motor.SpeedChanged-=Animate;}
    }
}
