using System;
using System.Collections.Generic;
using N = System.Numerics;
using Alarma.Player.Items;

// Sustitutos matemáticos para ejecutar los resolutores reales fuera del editor. No simulan Animator ni PhysX.
namespace UnityEngine
{
    public class Object { public static void Destroy(GameObject value) { value.Destroyed = true; } }
    public class GameObject
    {
        public bool Destroyed;
        public Transform transform;
        public GameObject(string name) { transform = new Transform(name, this); }
    }
    public class Transform
    {
        public string name; public GameObject gameObject; public Transform parent;
        public Vector3 localPosition; public Quaternion localRotation = Quaternion.identity;
        private readonly List<Transform> children = new();
        public Transform(string name, GameObject owner) { this.name=name;gameObject=owner; }
        public Vector3 position { get => parent == null ? localPosition : parent.position + parent.rotation*localPosition;
            set => localPosition = parent == null ? value : Quaternion.Inverse(parent.rotation)*(value-parent.position); }
        public Quaternion rotation { get => parent == null ? localRotation : parent.rotation*localRotation;
            set => localRotation=parent == null ? value : Quaternion.Inverse(parent.rotation)*value; }
        public Vector3 right => rotation*Vector3.right;
        public Vector3 up => rotation*Vector3.up;
        public void SetParent(Transform value, bool world)
        {
            var p=position;var q=rotation;parent?.children.Remove(this);parent=value;parent?.children.Add(this);
            if(world){position=p;rotation=q;}
        }
        public Vector3 InverseTransformDirection(Vector3 v)=>Quaternion.Inverse(rotation)*v;
        public T[] GetComponentsInChildren<T>(bool _) where T:class
        {
            var result=new List<T>();if(this is T t)result.Add(t);
            foreach(var c in children)result.AddRange(c.GetComponentsInChildren<T>(true));return result.ToArray();
        }
    }
    public struct Vector3
    {
        public float x,y,z;public Vector3(float x,float y,float z){this.x=x;this.y=y;this.z=z;}
        public N.Vector3 V=>new(x,y,z);public static Vector3 From(N.Vector3 v)=>new(v.X,v.Y,v.Z);
        public float magnitude=>V.Length();public float sqrMagnitude=>V.LengthSquared();
        public Vector3 normalized=>magnitude>1e-8f?this/magnitude:zero;
        public void Normalize(){this=normalized;}
        public static Vector3 zero=>default;public static Vector3 right=>new(1,0,0);public static Vector3 up=>new(0,1,0);
        public static Vector3 down=>-up;public static Vector3 forward=>new(0,0,1);
        public static Vector3 operator +(Vector3 a,Vector3 b)=>From(a.V+b.V);
        public static Vector3 operator -(Vector3 a,Vector3 b)=>From(a.V-b.V);
        public static Vector3 operator -(Vector3 a)=>From(-a.V);
        public static Vector3 operator *(Vector3 a,float b)=>From(a.V*b);
        public static Vector3 operator /(Vector3 a,float b)=>From(a.V/b);
        public static float Distance(Vector3 a,Vector3 b)=>(a-b).magnitude;
        public static float Dot(Vector3 a,Vector3 b)=>N.Vector3.Dot(a.V,b.V);
        public static Vector3 Cross(Vector3 a,Vector3 b)=>From(N.Vector3.Cross(a.V,b.V));
        public static Vector3 ProjectOnPlane(Vector3 v,Vector3 n)=>v-n*(Dot(v,n)/MathF.Max(1e-8f,n.sqrMagnitude));
    }
    public struct Quaternion
    {
        public N.Quaternion Q;private Quaternion(N.Quaternion value){Q=N.Quaternion.Normalize(value);}
        public static Quaternion identity=>new(N.Quaternion.Identity);
        public static Quaternion Inverse(Quaternion q)=>new(N.Quaternion.Inverse(q.Q));
        public static Quaternion Slerp(Quaternion a,Quaternion b,float t)=>new(N.Quaternion.Slerp(a.Q,b.Q,Math.Clamp(t,0,1)));
        public static Quaternion operator *(Quaternion a,Quaternion b)=>new(a.Q*b.Q);
        public static Vector3 operator *(Quaternion a,Vector3 b)=>Vector3.From(N.Vector3.Transform(b.V,a.Q));
        public static Quaternion AngleAxis(float a,Vector3 axis)=>axis.sqrMagnitude<1e-8?identity:new(N.Quaternion.CreateFromAxisAngle(axis.normalized.V,a*MathF.PI/180));
        public static Quaternion FromToRotation(Vector3 a,Vector3 b)
        {
            a=a.normalized;b=b.normalized;float dot=Math.Clamp(Vector3.Dot(a,b),-1,1);
            if(dot>.999999f)return identity;
            var axis=Vector3.Cross(a,b);
            if(axis.sqrMagnitude<1e-8f){axis=Vector3.Cross(a,Vector3.up);if(axis.sqrMagnitude<1e-8)axis=Vector3.Cross(a,Vector3.right);}
            return AngleAxis(MathF.Acos(dot)*180/MathF.PI,axis);
        }
        public static Quaternion LookRotation(Vector3 f,Vector3 u)
        {
            var z=f.normalized;var x=Vector3.Cross(u,z).normalized;var y=Vector3.Cross(z,x);
            return new(N.Quaternion.CreateFromRotationMatrix(new N.Matrix4x4(x.x,x.y,x.z,0,y.x,y.y,y.z,0,z.x,z.y,z.z,0,0,0,0,1)));
        }
    }
    public static class Mathf
    {
        public static float Clamp(float v,float a,float b)=>Math.Clamp(v,a,b);
        public static float Max(float a,float b)=>MathF.Max(a,b);
        public static float Abs(float x)=>MathF.Abs(x);public static float Sqrt(float x)=>MathF.Sqrt(x);
    }
}

class GripTests
{
    static int checks;
    static void Check(bool value,string label){if(!value)throw new Exception(label);checks++;Console.WriteLine("PASS "+label);}
    static UnityEngine.Transform Bone(string name,UnityEngine.Transform parent,UnityEngine.Vector3 position)
    {
        var t=new UnityEngine.GameObject(name).transform;t.SetParent(parent,false);t.localPosition=position;return t;
    }
    static void Main()
    {
        usingFixture(true);usingFixture(false);
        Console.WriteLine("GRIP_TESTS_PASSED "+checks);
    }
    static void usingFixture(bool right)
    {
        string side=right?".R":".L";
        var upper=Bone("UpperArm"+side,null,new(right?.18f:-.18f,1.42f,0));
        var lower=Bone("LowerArm"+side,upper,new(0,-.20f,0));
        var wrist=Bone("Wrist"+side,lower,new(0,-.23f,0));
        var oldPalm=Bone("OldPalm",wrist,new(0,0,.06f));
        foreach(var spec in new[]{("Index",-.03f),("Middle",0f),("Ring",.022f),("Pinky",.04f),("Thumb",-.055f)})
        {
            var p=Bone(spec.Item1+"1"+side,wrist,new(0,0,.02f));
            p=Bone(spec.Item1+"2"+side,p,new(spec.Item2,0,.12f));
            p=Bone(spec.Item1+"3"+side,p,new(0,0,.04f));
            if(spec.Item1!="Thumb")Bone(spec.Item1+"4"+side,p,new(0,0,.03f));
        }
        var hand=new HandGripPose(oldPalm,right);
        var target=new UnityEngine.Vector3(right?.02f:-.02f,1.15f,.27f);
        var normal=right?-UnityEngine.Vector3.right:UnityEngine.Vector3.right;
        var rotation=hand.WristRotation(UnityEngine.Quaternion.identity,UnityEngine.Vector3.forward,normal);
        var bend=(right?UnityEngine.Vector3.right:-UnityEngine.Vector3.right)*.45f+UnityEngine.Vector3.down;
        float a=(lower.position-upper.position).magnitude,b=(wrist.position-lower.position).magnitude;
        var original=oldPalm.position;
        hand.Capture(upper,lower);
        TwoBoneIk.Solve(upper,lower,hand.Palm,target,bend,1);
        wrist.rotation=rotation;
        Check((hand.Palm.position-target).magnitude>.01f,"Detecta desfase de resolver palma antes de girar muñeca "+side);
        hand.Restore();
        for(int i=0;i<60;i++)
        {
            hand.Capture(upper,lower);
            TwoBoneIk.SolveHand(upper,lower,hand.Palm,target,rotation,bend,1);
            hand.Curl(1,true);
            if(i==59)
            {
                Check((hand.Palm.position-target).magnitude<.001f,"Contacto final menor a 1 mm tras orientar muñeca "+side);
                Check(MathF.Abs((lower.position-upper.position).magnitude-a)<.0001f && MathF.Abs((wrist.position-lower.position).magnitude-b)<.0001f,"Conserva longitud de brazo y antebrazo "+side);
                var objectFrame=hand.ItemRotation(UnityEngine.Vector3.forward,normal);
                Check((objectFrame*UnityEngine.Vector3.forward-UnityEngine.Vector3.forward).magnitude<.001f,"El arma conserva su dirección con la mano orientada "+side);
            }
            hand.Restore();
        }
        Check((oldPalm.position-original).magnitude<.0001f,"Restaura la pose original sin deriva tras 60 fotogramas "+side);
        var before=hand.Palm.position;
        TwoBoneIk.SolveHand(upper,lower,hand.Palm,target,rotation,bend,0);
        Check((hand.Palm.position-before).magnitude<.0001f,"Peso cero libera el brazo para locomoción y puertas "+side);
        hand.Dispose();
        Check(hand.Palm.gameObject.Destroyed,"Libera el ancla al cambiar de personaje "+side);
    }
}
