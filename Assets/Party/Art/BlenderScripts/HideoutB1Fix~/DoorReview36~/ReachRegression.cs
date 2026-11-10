using System;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

namespace UnityEngine
{
    public class SerializeField:Attribute{}
    public class DefaultExecutionOrder:Attribute{public DefaultExecutionOrder(int n){}}
    public class MonoBehaviour {public Transform transform;public string name=>transform.name;}
    public enum HumanBodyBones{RightUpperArm,RightLowerArm,RightHand,Spine}
    public static class Time {public static float time,deltaTime=1f/60;}
}
namespace Alarma.AI.CityLife
{
    public static class RigBones
    {
        public static Transform Find(Transform root,HumanBodyBones bone)
        {
            string name=bone==HumanBodyBones.RightUpperArm?"UpperArm.R":bone==HumanBodyBones.RightLowerArm?"LowerArm.R":bone==HumanBodyBones.RightHand?"Wrist.R":"Abdomen";
            foreach(var t in root.GetComponentsInChildren<Transform>(true))if(t.name==name)return t;
            return null;
        }
    }
}
class ReachRegression
{
    static int checks;
    static void Check(bool v,string label){if(!v)throw new Exception(label);checks++;}
    static void Call(PedestrianReach reach,string method)=>typeof(PedestrianReach).GetMethod(method,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(reach,null);
    static Transform Bone(string name,Transform parent,Vector3 p){var t=new GameObject(name).transform;t.SetParent(parent,false);t.position=p;return t;}
    static void Main()
    {
        foreach(float heading in new[]{0f,90f,180f,270f})
        foreach(float shoulder in new[]{-.22f,-.118f,.18f,.22f})
        {
            Time.time=1;
            var root=Bone("Actor",null,Vector3.zero);
            var spine=Bone("Abdomen",root,new(0,1.1f,0));
            var upper=Bone("UpperArm.R",spine,new(shoulder,1.42f,0));
            var lower=Bone("LowerArm.R",upper,new(shoulder,1.22f,0));
            var wrist=Bone("Wrist.R",lower,new(shoulder,.99f,0));
            var grip=Bone("Grip_R6",wrist,new(shoulder,.93f,0));
            Bone("Middle2.R",wrist,new(shoulder,.85f,0));
            Bone("Index2.R",wrist,new(shoulder-.03f,.85f,0));
            Bone("Pinky2.R",wrist,new(shoulder+.04f,.85f,0));
            root.rotation=Quaternion.AngleAxis(heading,Vector3.up);
            var reach=new PedestrianReach{transform=root};reach.Configure(grip);
            var tooFar=Bone("TooFar",null,root.rotation*new Vector3(shoulder,1.28f,.48f));
            tooFar.rotation=Quaternion.LookRotation(-root.forward,Vector3.up);
            Check(reach.CanReach(tooFar.position,.02f) && !reach.CanReachSurface(tooFar),
                "Detecta falso alcance del agarre cuando la muñeca orientada no llega");
            var contact=Bone("Contact",null,root.rotation*new Vector3(.16f,1.28f,.365f));
            contact.rotation=Quaternion.LookRotation(-root.forward,Vector3.up);
            var stand=reach.AlignSurfaceStand(contact.position,Vector3.zero,root.forward);
            Check(MathF.Abs(Vector3.Dot(contact.position-stand-(upper.position-root.position),root.right))<.0001f,"Alinea hombro real a la placa");
            root.position=stand;
            var before=grip.position;
            for(int frame=0;frame<120;frame++)
            {
                Call(reach,"Update");Time.time+=Time.deltaTime;reach.ReachSurface(contact);Call(reach,"LateUpdate");
            }
            Check(reach.HasContact,"El NPC completa contacto sin una orden del jugador");
            Check((reach.PalmPosition-contact.position).magnitude<.005f,"Palma orientada queda a menos de 5 mm");
            Check(MathF.Abs((upper.position-lower.position).magnitude-.2f)<.0001f,"No estira brazo");
            reach.Release(contact);
            for(int frame=0;frame<30;frame++){Call(reach,"Update");Time.time+=Time.deltaTime;Call(reach,"LateUpdate");}
            Check(!reach.HasContact && (grip.position-before).magnitude<.0001f,"Libera mano y restaura reposo sin deriva");
        }
        Console.WriteLine("REACH_REGRESSION_PASSED "+checks);
    }
}
