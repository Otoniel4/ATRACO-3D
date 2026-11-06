using UnityEngine;
using Alarma.Core.Settings;
namespace Alarma.City.Playtest
{
    // Cámara en tercera persona que no atraviesa paredes ni techos. Al apuntar se acerca y pasa sobre el hombro derecho.
    [DefaultExecutionOrder(100)]
    public sealed class ReviewCamera:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private Transform player;
        [SerializeField] private GameSettings settings;
        private float yaw=0,pitch=18;
        public float Yaw=>yaw;
        // 0 normal, 1 apuntando (la fija quien usa el arma).
        public float Aim{get;set;}
        private Camera lens;
        public void Configure(ReviewInput controls,Transform target,GameSettings options){input=controls;player=target;settings=options;ResetView(0);}
        public void ResetView(float direction){yaw=direction;pitch=18;if(player!=null){transform.rotation=Quaternion.Euler(pitch,yaw,0);transform.position=player.position+Vector3.up*1.35f-transform.forward*4;}}
        private void LateUpdate()
        {
            if(input==null || player==null)return;
            if(input.Active){float sensitivity=settings!=null?settings.MouseSensitivity:1;yaw+=input.Look.x*.12f*sensitivity;pitch=Mathf.Clamp(pitch-input.Look.y*.10f*sensitivity,-35,70);}
            Quaternion rotation=Quaternion.Euler(pitch,yaw,0);Vector3 target=player.position+Vector3.up*Mathf.Lerp(1.35f,1.55f,Aim)+rotation*Vector3.right*(.48f*Aim);Vector3 direction=-(rotation*Vector3.forward);float distance=Mathf.Lerp(4f,1.6f,Aim);
            if(lens==null)lens=GetComponent<Camera>();if(lens!=null)lens.fieldOfView=Mathf.Lerp(60f,46f,Aim);
            if(Physics.SphereCast(target,.15f,direction,out var hit,distance,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore))distance=Mathf.Max(.35f,hit.distance-.10f);
            transform.position=target+direction*distance;transform.rotation=rotation;
        }
    }
}
