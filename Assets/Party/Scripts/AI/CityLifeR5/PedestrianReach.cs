using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    // CCD corto sobre el brazo derecho. Corrige el contacto según la estatura sin estirar huesos.
    [DefaultExecutionOrder(100)]
    public sealed class PedestrianReach : MonoBehaviour
    {
        [SerializeField] private Transform upper,lower,grip,spine;
        private Transform target;private float until;
        // Pose previa al ajuste. Los huesos que ninguna animación escribe (p. ej. Abdomen del pack modular)
        // no se reinician solos: sin devolverlos, la inclinación se sumaba cada fotograma y el NPC quedaba doblado.
        private Quaternion spinePose,upperPose,lowerPose;private bool adjusted;
        private void Update()
        {
            if(!adjusted)return;
            spine.localRotation=spinePose;upper.localRotation=upperPose;lower.localRotation=lowerPose;adjusted=false;
        }
        public void Configure(Transform hand)
        {
            grip=hand;upper=Bone(HumanBodyBones.RightUpperArm);lower=Bone(HumanBodyBones.RightLowerArm);spine=Bone(HumanBodyBones.Spine);
        }
        private Transform Bone(HumanBodyBones bone)=>RigBones.Find(transform,bone)??throw new InvalidOperationException("Falta el hueso "+bone+" en "+name);
        public void Reach(Transform point,float seconds=.1f){target=point;until=Time.time+seconds;}
        private void LateUpdate()
        {
            if(target==null || grip==null || Time.time>until || Time.deltaTime<=0)return;
            spinePose=spine.localRotation;upperPose=upper.localRotation;lowerPose=lower.localRotation;adjusted=true;
            Vector3 direction=target.position-upper.position;direction.y=0;
            if(direction.sqrMagnitude>.001f)spine.rotation=Quaternion.AngleAxis(16,Vector3.Cross(Vector3.up,direction.normalized))*spine.rotation;
            for(int i=0;i<6;i++)foreach(Transform joint in new[]{lower,upper})
            {
                Vector3 from=grip.position-joint.position,to=target.position-joint.position;
                if(from.sqrMagnitude>.000001f && to.sqrMagnitude>.000001f)joint.rotation=Quaternion.FromToRotation(from,to)*joint.rotation;
            }
        }
    }
}
