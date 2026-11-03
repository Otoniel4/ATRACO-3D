using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    // Cambia solo la presentación del jugador de revisión; no sustituye su controlador al cambiar de rol.
    public sealed class ReviewCharacterView:MonoBehaviour
    {
        [SerializeField] private GameObject[] models=Array.Empty<GameObject>();
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewPlayerMotor motor;
        private GameObject visual;private Animator animator;
        public Animator CurrentAnimator=>animator;
        public int Role{get;private set;}
        public void Configure(ReviewInput controls,ReviewPlayerMotor movement,GameObject[] variants){input=controls;motor=movement;models=variants;}
        private void Start(){SelectRole(0);if(motor!=null)motor.SpeedChanged+=Animate;}
        private void Update(){if(input!=null && input.RolePressed>=0)SelectRole(input.RolePressed);}
        public void SelectRole(int index)
        {
            if(index<0 || index>=models.Length || models[index]==null)return;Role=index;
            if(visual!=null){visual.SetActive(false);Destroy(visual);}visual=Instantiate(models[index],transform);visual.transform.localPosition=Vector3.zero;visual.transform.localRotation=Quaternion.identity;
            SetLayer(visual.transform,30);animator=visual.GetComponentInChildren<Animator>();
            if(animator!=null){animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;animator.Rebind();animator.Update(0);}
            Bounds bounds=new Bounds(transform.position,Vector3.zero);bool found=false;
            foreach(var r in visual.GetComponentsInChildren<Renderer>())if(r.enabled){if(!found){bounds=r.bounds;found=true;}else bounds.Encapsulate(r.bounds);}
            var capsule=GetComponent<CharacterController>();if(found && capsule!=null){capsule.height=Mathf.Clamp(bounds.size.y,1.5f,2.1f);capsule.center=new Vector3(0,capsule.height*.5f,0);capsule.radius=index==3?.31f:.24f;}
        }
        private static void SetLayer(Transform item,int layer){item.gameObject.layer=layer;foreach(Transform child in item)SetLayer(child,layer);}
        private void Animate(float speed)
        {
            if(animator==null)return;animator.SetFloat("Speed",speed);animator.SetFloat("WalkRate",Mathf.Clamp(speed,0,4));animator.SetBool("Browse",false);animator.SetBool("Pay",false);animator.SetBool("Carry",false);
        }
        private void OnDestroy(){if(motor!=null)motor.SpeedChanged-=Animate;}
    }
}
