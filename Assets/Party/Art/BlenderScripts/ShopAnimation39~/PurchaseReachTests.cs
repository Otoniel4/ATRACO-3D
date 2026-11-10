using System;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

static class PurchaseReachTests
{
    static int count;
    static void Check(bool ok,string label){if(!ok)throw new Exception(label);count++;}
    static void Call(PedestrianReach reach,string method)=>typeof(PedestrianReach).GetMethod(method,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(reach,null);
    static Transform Bone(string name,Transform parent,Vector3 p){var t=new GameObject(name).transform;t.SetParent(parent,false);t.position=p;return t;}
    static void Main()
    {
        CounterReachTests.Run();
        foreach(float yaw in new[]{0f,90f,180f,270f})
        {
            var root=Bone("Actor",null,Vector3.zero);
            var spine=Bone("Abdomen",root,new(0,1.1f,0));
            var upper=Bone("UpperArm.R",spine,new(.18f,1.42f,0));
            var lower=Bone("LowerArm.R",upper,new(.18f,1.22f,0));
            var wrist=Bone("Wrist.R",lower,new(.18f,.99f,0));
            var grip=Bone("Grip_R6",wrist,new(.18f,.93f,0));
            foreach(var pair in new[]{("Index",-.03f),("Middle",0f),("Ring",.02f),("Pinky",.04f),("Thumb",-.055f)})
            {
                var finger=Bone(pair.Item1+"2.R",wrist,new(.18f+pair.Item2,.85f,0));
                var next=Bone(pair.Item1+"3.R",finger,new(.18f+pair.Item2,.81f,0));
                Bone(pair.Item1+"4.R",next,new(.18f+pair.Item2,.78f,0));
            }
            root.rotation=Quaternion.AngleAxis(yaw,Vector3.up);
            var reach=new PedestrianReach{transform=root};reach.Configure(grip);
            var before=grip.position;
            var contact=Bone("Producto",null,root.rotation*new Vector3(.18f,1.12f,.26f));
            for(int step=0;step<120;step++)
            {Call(reach,"Update");Time.time+=Time.deltaTime;reach.ReachObject(contact);Call(reach,"LateUpdate");}
            Check((reach.PurchaseGrip.position-contact.position).magnitude<.001f,"La palma anatómica sostiene el producto");
            Check((reach.PalmPosition-reach.PurchaseGrip.position).magnitude<.0001f,"Vista y brazo usan el mismo punto de contacto");
            Check(MathF.Abs((upper.position-lower.position).magnitude-.2f)<.0001f,"No estira huesos al sostener");
            reach.Release(contact);
            for(int step=0;step<40;step++){Call(reach,"Update");Time.time+=Time.deltaTime;Call(reach,"LateUpdate");}
            Check((grip.position-before).magnitude<.0001f,"Recupera reposo tras 120 cuadros sin acumular flexión");
        }
        Console.WriteLine("PURCHASE_REACH_CHECKS_PASSED "+count);
    }
}
