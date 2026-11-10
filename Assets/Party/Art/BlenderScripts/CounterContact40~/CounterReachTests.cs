using System;
using System.IO;
using System.Text.Json;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;

static class CounterReachTests
{
    static Vector3 V(JsonElement a)=>new(a[0].GetSingle(),a[1].GetSingle(),a[2].GetSingle());
    static Transform Bone(string name,Transform parent,Vector3 p)
    {var t=new GameObject(name).transform;t.SetParent(parent,false);t.position=p;return t;}
    static void Step(PedestrianReach hand,string method)=>typeof(PedestrianReach).GetMethod(method,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(hand,null);
    public static void Run()
    {
        const string folder="Assets/Party/Art/BlenderScripts/CounterContact40~/";
        using var actors=JsonDocument.Parse(File.ReadAllText(folder+"bones.json"));
        using var counters=JsonDocument.Parse(File.ReadAllText(folder+"contacts.json"));
        using var products=JsonDocument.Parse(File.ReadAllText(folder+"product-heights.json"));
        int count=0;float worst=0;
        foreach(var actor in actors.RootElement.EnumerateArray())
        foreach(var counter in counters.RootElement.EnumerateObject())
        foreach(int phase in new[]{0,1,2})
        foreach(float yaw in new[]{0f,90f,180f,270f})
        foreach(float side in new[]{-.055f,0f,.055f})
        {
            var bones=actor.GetProperty("bones");
            var root=Bone("Actor",null,Vector3.zero);
            var spine=Bone("Abdomen",root,V(bones.GetProperty("Abdomen")));
            var upper=Bone("UpperArm.R",spine,V(bones.GetProperty("UpperArm.R")));
            var lower=Bone("LowerArm.R",upper,V(bones.GetProperty("LowerArm.R")));
            var wrist=Bone("Wrist.R",lower,V(bones.GetProperty("Wrist.R")));
            var grip=Bone("Grip_R6",wrist,wrist.position);
            foreach(string n in new[]{"Index2.R","Middle2.R","Pinky2.R","Ring2.R","Thumb2.R"})Bone(n,wrist,V(bones.GetProperty(n)));
            float a=(upper.position-lower.position).magnitude,b=(lower.position-wrist.position).magnitude;
            bool product=phase>0;
            bool above=product && counter.Name!="banco";
            float height=product?(above?products.RootElement.GetProperty(counter.Name).GetSingle():0f):.12f;
            if (phase==2 && above) height+=.14f;
            var target=new Vector3(upper.position.x+side,counter.Value.GetProperty("center")[1].GetSingle()-.1f+height,
                counter.Value.GetProperty("width").GetSingle()*.5f+.255f);
            root.rotation=Quaternion.AngleAxis(yaw,Vector3.up);
            var point=Bone("Contacto",null,root.rotation*target);
            var hand=new PedestrianReach{transform=root};hand.Configure(grip);
            for(int i=0;i<160;i++){Step(hand,"Update");Time.time+=Time.deltaTime;hand.ReachObject(point,above);Step(hand,"LateUpdate");}
            float error=(hand.PurchaseGrip.position-point.position).magnitude;worst=MathF.Max(worst,error);
            if(error>.025f || MathF.Abs((upper.position-lower.position).magnitude-a)>.0001f || MathF.Abs((lower.position-wrist.position).magnitude-b)>.0001f)
                throw new Exception($"Contacto fuera de alcance: {actor.GetProperty("name")} {counter.Name} {above} {yaw} error={error}");
            count++;
        }
        Console.WriteLine($"ACTUAL_COUNTER_CONTACTS {count}; max_error_m={worst}; sin estirar huesos");
    }
}
