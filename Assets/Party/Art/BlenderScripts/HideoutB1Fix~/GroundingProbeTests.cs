using System;
using System.Collections.Generic;
using System.Reflection;
using Alarma.City.Playtest;
using UnityEngine;

namespace UnityEngine
{
    public struct Vector3
    {
        public float x,y,z;
        public Vector3(float x,float y,float z){this.x=x;this.y=y;this.z=z;}
        public static Vector3 up=>new Vector3(0,1,0);
        public static Vector3 down=>new Vector3(0,-1,0);
        public static Vector3 zero=>new Vector3(0,0,0);
        public float sqrMagnitude=>x*x+y*y+z*z;
        public float magnitude=>(float)Math.Sqrt(sqrMagnitude);
        public static Vector3 operator +(Vector3 a,Vector3 b)=>new Vector3(a.x+b.x,a.y+b.y,a.z+b.z);
        public static Vector3 operator -(Vector3 a,Vector3 b)=>new Vector3(a.x-b.x,a.y-b.y,a.z-b.z);
        public static Vector3 operator *(Vector3 a,float b)=>new Vector3(a.x*b,a.y*b,a.z*b);
        public static Vector3 MoveTowards(Vector3 current,Vector3 target,float step){var delta=target-current;return delta.magnitude<=step?target:current+delta*(step/delta.magnitude);}
    }
    public struct Vector2 { public float x,y;public static Vector2 zero=>default; }
    public struct Quaternion
    {
        public static Quaternion Euler(float x,float y,float z)=>default;
        public static Quaternion LookRotation(Vector3 p)=>default;
        public static Quaternion RotateTowards(Quaternion a,Quaternion b,float step)=>default;
        public static Vector3 operator *(Quaternion q,Vector3 p)=>p;
    }
    public static class Mathf
    {
        public const float Deg2Rad=(float)Math.PI/180f;
        public static float Cos(float f)=>(float)Math.Cos(f);
        public static float Clamp(float value,float min,float max)=>Math.Min(max,Math.Max(min,value));
        public static float Min(float a,float b)=>Math.Min(a,b);
    }
    public static class Time { public static float deltaTime=.016f; }
    public static class Physics { public static void SyncTransforms(){} }
    public class Transform { public Vector3 position;public Quaternion rotation; }
    public class GameObject { public SceneManagement.Scene scene; }
    public class MonoBehaviour
    {
        public Transform transform=new Transform();public GameObject gameObject=new GameObject();
        private CharacterController controller;
        public T GetComponent<T>() where T:class
        {
            controller??=new CharacterController{transform=transform};return controller as T;
        }
    }
    public class CharacterController
    {
        public Transform transform; public bool enabled=true,isGrounded=true;
        public float height=1.75f,radius=.24f,slopeLimit=50;
        public Vector3 velocity;
        public void Move(Vector3 delta){transform.position+=delta;velocity=delta*(1/Time.deltaTime);}
    }
    [AttributeUsage(AttributeTargets.Class)]public class RequireComponent:Attribute { public RequireComponent(Type type){} }
    [AttributeUsage(AttributeTargets.Field)]public class SerializeField:Attribute {}
    public class Collider { }
    public enum QueryTriggerInteraction { Ignore }
    public struct RaycastHit { public Vector3 point,normal; }
    public struct Surface
    {
        public float y,normalY;public int layer;public bool trigger;
        public Surface(float y,float normalY=1f,int layer=0,bool trigger=false){this.y=y;this.normalY=normalY;this.layer=layer;this.trigger=trigger;}
    }
    public static class ProbeWorld
    {
        public static List<Surface> surfaces=new List<Surface>();
        public static bool obstruction;public static int obstructionLayer;public static Vector3 origin;
        public static void Reset(params Surface[] values){surfaces=new List<Surface>(values);obstruction=false;obstructionLayer=0;}
    }
    // Geometría analítica mínima para probar la regla; no representa PhysX ni ejecuta Unity.
    public struct PhysicsScene
    {
        private bool valid;
        public PhysicsScene(bool valid){this.valid=valid;}
        public bool IsValid()=>valid;
        public bool Raycast(Vector3 origin,Vector3 direction,out RaycastHit hit,float distance,int mask,QueryTriggerInteraction query)
        {
            ProbeWorld.origin=origin;hit=default;float closest=float.MaxValue;bool found=false;
            foreach(var surface in ProbeWorld.surfaces)
            {
                float drop=origin.y-surface.y;
                if(surface.trigger || (mask&(1<<surface.layer))==0 || drop<0 || drop>distance || drop>=closest)continue;
                hit=new RaycastHit{point=new Vector3(origin.x,surface.y,origin.z),normal=new Vector3(0,surface.normalY,0)};
                closest=drop;found=true;
            }
            return found;
        }
        public int OverlapCapsule(Vector3 bottom,Vector3 top,float radius,Collider[] results,int mask,QueryTriggerInteraction query)
        {
            if(ProbeWorld.obstruction && (mask&(1<<ProbeWorld.obstructionLayer))!=0){results[0]=new Collider();return 1;}
            return 0;
        }
    }
}

namespace UnityEngine.SceneManagement
{
    public struct Scene {}
    public static class ScenePhysics { public static PhysicsScene GetPhysicsScene(this Scene scene)=>new PhysicsScene(true); }
}
namespace Alarma.Core.Contracts
{
    public interface IPlayableWorld { bool ReadyAt(Vector3 p);float HalfSize{get;} }
}
namespace Alarma.City.Playtest
{
    public class ReviewInput:MonoBehaviour { public bool Active=true,Run;public Vector2 Move; }
    public class ReviewCamera:MonoBehaviour { public float Yaw; }
}
class FakeWorld:MonoBehaviour,Alarma.Core.Contracts.IPlayableWorld
{
    public bool Ready=true;
    public bool ReadyAt(Vector3 p)=>Ready;
    public float HalfSize=>1000;
}

static class GroundingProbeTests
{
    static int passed;
    static void Require(bool condition,string label){if(!condition)throw new Exception(label);passed++;Console.WriteLine("PASS "+label);}
    static bool Near(float a,float b)=>Math.Abs(a-b)<.0001f;
    static Vector3 Spawn(ReviewPlayerMotor motor)=>(Vector3)typeof(ReviewPlayerMotor).GetField("spawn",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(motor);
    static void Invoke(ReviewPlayerMotor motor,string name)=>typeof(ReviewPlayerMotor).GetMethod(name,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(motor,null);
    static bool Resolve(Vector3 feet,out Vector3 grounded,out RaycastHit support)=>ReviewPlayerGrounding.TryResolve(new PhysicsScene(true),feet,1.75f,.24f,50,out grounded,out support);
    static void Main()
    {
        var feet=new Vector3(-528,.5f,135.9f);
        ProbeWorld.Reset(new Surface(.15f),new Surface(3f),new Surface(6.6f),new Surface(2.75f));
        Require(Resolve(feet,out var grounded,out var support)&&Near(grounded.y,.185f)&&Near(support.point.y,.15f),"piso interior bajo cielo raso a 3m");
        new PhysicsScene(true).Raycast(feet+Vector3.up*3,Vector3.down,out var old,10,~((1<<29)|(1<<30)|(1<<31)),QueryTriggerInteraction.Ignore);
        Require(Near(old.point.y,3f),"consulta anterior reproduce seleccion de losa");
        ProbeWorld.Reset();Require(!Resolve(feet,out grounded,out support),"sin apoyo no acepta destino");
        ProbeWorld.Reset(new Surface(.15f));Require(!Resolve(new Vector3(0,2,0),out grounded,out support),"no baja mas de 65cm al resolver inicio");
        ProbeWorld.Reset(new Surface(.15f,.5f));Require(!Resolve(feet,out grounded,out support),"rechaza pendiente fuera de limite");
        ProbeWorld.Reset(new Surface(.15f));ProbeWorld.obstruction=true;Require(!Resolve(feet,out grounded,out support),"rechaza cuerpo dentro de mueble o puerta");
        ProbeWorld.obstructionLayer=29;Require(Resolve(feet,out grounded,out support),"ignora personajes de capa 29 al validar cuerpo");
        ProbeWorld.Reset(new Surface(.15f),new Surface(.6f,1,30),new Surface(.7f,1,0,true));Require(Resolve(feet,out grounded,out support)&&Near(support.point.y,.15f),"ignora jugador y triggers en la sonda");
        ProbeWorld.Reset(new Surface(.14f));Require(Resolve(new Vector3(0,0,0),out grounded,out support)&&Near(grounded.y,.175f),"destino del mapa a y0 admite vereda elevada");
        Require(!ReviewPlayerGrounding.TryResolve(new PhysicsScene(false),feet,1.75f,.24f,50,out grounded,out support),"rechaza escena fisica invalida");
        Require(!ReviewPlayerGrounding.TryResolve(new PhysicsScene(true),feet,.2f,.24f,50,out grounded,out support),"rechaza capsula invalida");
        var motor=new ReviewPlayerMotor();motor.transform.position=feet;Invoke(motor,"Awake");
        Require(Near(Spawn(motor).x,-528)&&Near(Spawn(motor).z,135.9f),"Awake recaptura destino guardado y evita origen cero");
        var world=new FakeWorld{Ready=false};motor.Configure(new ReviewInput(),new ReviewCamera(),world,feet);
        Invoke(motor,"Update");Require(Near(motor.transform.position.y,.5f),"espera mundo listo sin mover jugador");
        world.Ready=true;ProbeWorld.Reset();Invoke(motor,"Update");Require(Near(motor.transform.position.y,.5f),"sin soporte mantiene pendiente y no avanza");
        ProbeWorld.Reset(new Surface(.15f),new Surface(3f),new Surface(6.6f),new Surface(2.75f));Invoke(motor,"Update");
        Require(Near(Spawn(motor).y,.185f),"nuevo intento resuelve planta baja y guarda respawn valido");
        motor.Teleport(new Vector3(10,0,20));ProbeWorld.Reset();Invoke(motor,"Update");
        Require(Near(Spawn(motor).x,-528)&&Near(Spawn(motor).z,135.9f),"teleport sin apoyo conserva ultimo respawn seguro");
        ProbeWorld.Reset(new Surface(.14f));Invoke(motor,"Update");
        Require(Near(Spawn(motor).x,10)&&Near(Spawn(motor).z,20)&&Near(Spawn(motor).y,.175f),"teleport valido recaptura respawn y suelo de vereda");
        motor.transform.position=new Vector3(777,-9,888);Invoke(motor,"Update");
        Require(Near(motor.transform.position.x,10)&&Near(motor.transform.position.z,20),"caida recupera ultimo punto seguro sin ir al origen");
        Console.WriteLine("ANALYTIC_RULE_TESTS_PASSED "+passed);
    }
}
