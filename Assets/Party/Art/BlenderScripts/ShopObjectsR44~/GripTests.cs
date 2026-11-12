using System;
using System.IO;
using System.Text.Json;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

static class GripTests44
{
    static Vector3 V(JsonElement a) => a.ValueKind == JsonValueKind.Array ? new(a[0].GetSingle(),a[1].GetSingle(),a[2].GetSingle())
        : new(a.GetProperty("x").GetSingle(),a.GetProperty("y").GetSingle(),a.GetProperty("z").GetSingle());
    static Transform Bone(string n,Transform parent,Vector3 p){var t=new GameObject(n).transform;t.SetParent(parent,false);t.position=p;return t;}
    static void Step(object hand,string m)=>hand.GetType().GetMethod(m,BindingFlags.NonPublic|BindingFlags.Instance).Invoke(hand,null);
    static void Main()
    {
        using var actors=JsonDocument.Parse(File.ReadAllText("Assets/Party/Art/BlenderScripts/CounterContact40~/bones.json"));
        using var counters=JsonDocument.Parse(File.ReadAllText("Assets/Party/Art/BlenderScripts/CounterContact40~/contacts.json"));
        using var catalog=JsonDocument.Parse(File.ReadAllText("Assets/Party/Art/Props/ShopObjects/catalog.json"));
        int count=0;float worst=0;int failures=0;
        foreach(var actor in actors.RootElement.EnumerateArray())
        foreach(var product in catalog.RootElement.GetProperty("items").EnumerateArray())
        foreach(bool cashier in new[]{false,true})
        {
            var data=actor.GetProperty("bones"); var root=Bone("Actor",null,Vector3.zero);
            var spine=Bone("Abdomen",root,V(data.GetProperty("Abdomen")));
            Transform upper=null,lower=null,wrist=null,grip=null;
            foreach(bool left in new[]{false,true})
            {
                Vector3 P(string n){var p=V(data.GetProperty(n+".R"));if(left)p.x=-p.x;return p;}
                string suffix=left?".L":".R";
                var u=Bone("UpperArm"+suffix,spine,P("UpperArm"));var l=Bone("LowerArm"+suffix,u,P("LowerArm"));
                var w=Bone("Wrist"+suffix,l,P("Wrist"));
                foreach(string n in new[]{"Index2","Middle2","Pinky2","Ring2","Thumb2"})Bone(n+suffix,w,P(n));
                if(!left){upper=u;lower=l;wrist=w;grip=Bone("Grip_R6",w,w.position);}
            }
            var hand=new PedestrianReach{transform=root};hand.Configure(grip);
            var support=new CommerceSupportHand{transform=root};
            var counter=counters.RootElement.GetProperty(product.GetProperty("shop").GetString());
            bool two=product.GetProperty("twoHands").GetBoolean();
            var q=Quaternion.AngleAxis(cashier?180:0,Vector3.up);
            var right=V(product.GetProperty(cashier&&two?"left":"right"));
            var leftPoint=V(product.GetProperty(cashier&&two?"right":"left"));
            var offset=q*right;
            var center=new Vector3(two?0:upper.position.x-offset.x,counter.GetProperty("center")[1].GetSingle()-.1f,
                counter.GetProperty("width").GetSingle()*.5f+.255f);
            var point=Bone("Target",null,center+offset);
            var fingers=q*V(product.GetProperty(cashier&&two?"leftFingers":"fingers"));
            if(Vector3.Dot(fingers,root.forward)<0f)fingers=-fingers;
            var normal=q*V(product.GetProperty(cashier&&two?"leftNormal":"normal"));
            float a=(upper.position-lower.position).magnitude,b=(lower.position-wrist.position).magnitude;
            for(int i=0;i<180;i++)
            {
                Step(support,"Update");Step(hand,"Update");Time.time+=Time.deltaTime;
                hand.SetObjectPose(fingers,normal,product.GetProperty("curl").GetSingle());hand.ReachObject(point);
                var leftFingers=q*V(product.GetProperty(cashier?"fingers":"leftFingers"));if(Vector3.Dot(leftFingers,root.forward)<0f)leftFingers=-leftFingers;
                if(two)support.Follow(center+q*leftPoint,leftFingers,q*V(product.GetProperty(cashier?"normal":"leftNormal")),.65f);
                Step(hand,"LateUpdate");Step(support,"LateUpdate");
            }
            float error=(hand.PurchaseGrip.position-point.position).magnitude;worst=MathF.Max(error,worst);
            bool ok=error<.025f && (!two||support.Touches(center+q*leftPoint));
            if(!ok){Console.WriteLine($"FAIL {actor.GetProperty("name")} {product.GetProperty("id")} cashier={cashier} error={error} left={support.Touches(center+q*leftPoint)}");failures++;}
            if(MathF.Abs((upper.position-lower.position).magnitude-a)>.0001f||MathF.Abs((lower.position-wrist.position).magnitude-b)>.0001f)throw new Exception("Huesos estirados");
            count++;
        }
        Console.WriteLine($"R44_GRIPS {count}; failures={failures}; worst={worst}");
        if(failures>0)Environment.Exit(1);
    }
}
