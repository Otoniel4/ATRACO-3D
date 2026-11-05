using System;
using System.Collections.Generic;

namespace UnityEngine
{
    public sealed class SerializeField : Attribute { }
    public class ScriptableObject { }
    public class MonoBehaviour
    {
        public readonly Transform transform = new Transform();
        public readonly GameObject gameObject = new GameObject();
        public bool isActiveAndEnabled = true;
        public object Component;
        public T GetComponent<T>() where T : class => Component as T;
        // Las pruebas de población deciden cómo se copia un prefab.
        public static Func<MonoBehaviour, MonoBehaviour> Factory;
        public static T Instantiate<T>(T original, Transform parent) where T : MonoBehaviour => (T)Factory(original);
        public static void Destroy(GameObject target) { }
    }
    public sealed class GameObject
    {
        public bool activeSelf = true;
        public void SetActive(bool value) => activeSelf = value;
    }
    public sealed class MinAttribute : Attribute { public MinAttribute(float min) { } }
    public sealed class HeaderAttribute : Attribute { public HeaderAttribute(string text) { } }
    public sealed class TooltipAttribute : Attribute { public TooltipAttribute(string text) { } }
    public sealed class Camera
    {
        public static Camera main;
        public Func<Vector3, Vector3> Viewport = p => new Vector3(.5f, .5f, 1f);
        public Vector3 WorldToViewportPoint(Vector3 position) => Viewport(position);
    }
    public class Transform
    {
        public Vector3 position;
        public Quaternion rotation;
        public bool IsChildOf(Transform other) => ReferenceEquals(this, other);
    }
    public struct Quaternion
    {
        public static Quaternion LookRotation(Vector3 direction) => default;
        public static Quaternion RotateTowards(Quaternion from, Quaternion to, float step) => to;
    }
    public struct Vector2
    {
        public float x,y;
        public Vector2(float x,float y) { this.x=x; this.y=y; }
        public static Vector2 Min(Vector2 a, Vector2 b) => new Vector2(Math.Min(a.x,b.x),Math.Min(a.y,b.y));
        public static Vector2 Max(Vector2 a, Vector2 b) => new Vector2(Math.Max(a.x,b.x),Math.Max(a.y,b.y));
    }
    public struct Vector3
    {
        public float x,y,z;
        public Vector3(float x,float y,float z) { this.x=x; this.y=y; this.z=z; }
        public float sqrMagnitude => x*x+y*y+z*z;
        public float magnitude => (float)Math.Sqrt(sqrMagnitude);
        public Vector3 normalized => magnitude > .00001f ? this / magnitude : default;
        public void Normalize() => this = normalized;
        public static Vector3 up => new Vector3(0,1,0);
        public static Vector3 down => new Vector3(0,-1,0);
        public static Vector3 operator +(Vector3 a,Vector3 b) => new Vector3(a.x+b.x,a.y+b.y,a.z+b.z);
        public static Vector3 operator -(Vector3 a,Vector3 b) => new Vector3(a.x-b.x,a.y-b.y,a.z-b.z);
        public static Vector3 operator *(Vector3 a,float f) => new Vector3(a.x*f,a.y*f,a.z*f);
        public static Vector3 operator /(Vector3 a,float f) => a*(1/f);
        public static Vector3 Lerp(Vector3 a,Vector3 b,float t) => a + (b-a)*t;
    }
    public static class Mathf
    {
        public static int Max(int a,int b) => Math.Max(a,b);
        public static float Max(float a,float b) => Math.Max(a,b);
        public static int Min(int a,int b) => Math.Min(a,b);
        public static float Min(float a,float b) => Math.Min(a,b);
        public static float Abs(float x) => Math.Abs(x);
        public static int CeilToInt(float x) => (int)Math.Ceiling(x);
        public static int FloorToInt(float x) => (int)Math.Floor(x);
    }
    public static class Time { public static float time, deltaTime = .1f; }
    public sealed class Animator
    {
        public static int StringToHash(string name) => name.GetHashCode();
        public float Speed { get; private set; }
        public void SetFloat(int parameter, float speed) => Speed = speed;
    }
    public enum QueryTriggerInteraction { Ignore }
    public sealed class Collider
    {
        public Transform transform;
        public float Radius;
        public int Layer;
        public bool Trigger;
    }
    public struct RaycastHit { public Vector3 point,normal; public Collider collider; }

    // Modelo analítico horizontal de discos para las pruebas. La malla y PhysX se verifican en Unity.
    public static class Physics
    {
        public static readonly List<Collider> Bodies = new List<Collider>();
        public static bool Ground = true;
        public static float CurbHeight;
        private static readonly Collider Curb = new Collider { transform = new Transform() };
        public static void SyncTransforms() { }
        public static bool Raycast(Vector3 from, Vector3 direction, out RaycastHit hit, float distance, int mask, QueryTriggerInteraction triggers)
        {
            float height = CurbHeight > 0f && from.z <= 0f ? .14f + CurbHeight : .14f;
            hit = new RaycastHit { point = new Vector3(from.x,height,from.z), normal = Vector3.up };
            return Ground && from.y >= height && from.y - height <= distance;
        }
        public static int OverlapCapsuleNonAlloc(Vector3 a, Vector3 b, float radius, Collider[] result, int mask, QueryTriggerInteraction triggers)
        {
            int count = 0;
            if ((mask & 1) != 0 && HitsCurb(a,radius)) result[count++] = Curb;
            foreach (Collider body in Bodies)
                if (Included(body,mask) && Hits(a,b,body,radius) && count < result.Length) result[count++] = body;
            return count;
        }
        public static int CapsuleCastNonAlloc(Vector3 a, Vector3 b, float radius, Vector3 direction,
            RaycastHit[] result, float distance, int mask, QueryTriggerInteraction triggers)
        {
            int count = 0;
            if ((mask & 1) != 0 && (HitsCurb(a,radius) || HitsCurb(a+direction*distance,radius)))
                result[count++] = new RaycastHit { collider = Curb };
            foreach (Collider body in Bodies)
                if (Included(body,mask) && Hits(a,a+direction*distance,body,radius) && count < result.Length)
                    result[count++] = new RaycastHit { collider = body };
            return count;
        }
        private static bool Included(Collider body,int mask) => !body.Trigger && (mask & (1<<body.Layer)) != 0;
        private static bool HitsCurb(Vector3 center,float radius)
        {
            if (CurbHeight <= 0f) return false;
            float z = Math.Max(0f,center.z);
            float y = Math.Max(0f,center.y-(.14f+CurbHeight));
            return z*z+y*y < radius*radius-.000001f;
        }
        private static bool Hits(Vector3 a,Vector3 b,Collider body,float radius)
        {
            Vector3 d=b-a,p=body.transform.position-a;
            float l=d.x*d.x+d.z*d.z;
            float t=l>.00001f ? Math.Clamp((p.x*d.x+p.z*d.z)/l,0,1) : 0;
            float x=p.x-t*d.x,z=p.z-t*d.z;
            return x*x+z*z < (radius+body.Radius)*(radius+body.Radius)-.000001f;
        }
    }
}
