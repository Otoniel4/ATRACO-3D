using UnityEngine;
namespace Alarma.City.Playtest
{
    [DefaultExecutionOrder(100)]
    public sealed class ReviewCamera:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private Transform player;
        private float yaw=0,pitch=18;
        public float Yaw=>yaw;
        public bool Flying{get;private set;}
        public void Configure(ReviewInput controls,Transform target){input=controls;player=target;ResetView(0);}
        public void ResetView(float direction){Flying=false;yaw=direction;pitch=18;if(player!=null){transform.rotation=Quaternion.Euler(pitch,yaw,0);transform.position=player.position+Vector3.up*1.35f-transform.forward*4;}}
        private void LateUpdate()
        {
            if(input==null || player==null)return;
            if(input.Active){yaw+=input.Look.x*.12f;pitch=Mathf.Clamp(pitch-input.Look.y*.10f,-65,72);if(input.FlyPressed)Flying=!Flying;}
            Quaternion rotation=Quaternion.Euler(pitch,yaw,0);
            if(Flying)
            {
                transform.rotation=rotation;if(input.Active)transform.position+=(transform.forward*input.Move.y+transform.right*input.Move.x+Vector3.up*input.Lift)*(input.Run?32:10)*Time.unscaledDeltaTime;return;
            }
            pitch=Mathf.Clamp(pitch,5,65);rotation=Quaternion.Euler(pitch,yaw,0);Vector3 target=player.position+Vector3.up*1.35f;Vector3 direction=-(rotation*Vector3.forward);float distance=4;
            if(Physics.SphereCast(target,.15f,direction,out var hit,distance,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore))distance=Mathf.Max(.35f,hit.distance-.10f);
            transform.position=target+direction*distance;transform.rotation=rotation;
        }
    }
}
