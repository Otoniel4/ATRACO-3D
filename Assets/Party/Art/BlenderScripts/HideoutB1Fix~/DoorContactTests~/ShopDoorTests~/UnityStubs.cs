using System;
using System.Collections.Generic;
using N = System.Numerics;

namespace UnityEngine
{
    public sealed class SerializeField : Attribute { }
    public sealed class DefaultExecutionOrder : Attribute { public DefaultExecutionOrder(int _) {} }
    public enum QueryTriggerInteraction { Ignore }
    public partial class MonoBehaviour { }

    public partial struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public static Vector3 zero => default;
        public static Vector3 up => new(0, 1, 0);
        public static Vector3 forward => new(0, 0, 1);
        public static Vector3 one => new(1, 1, 1);
        public float sqrMagnitude => x*x + y*y + z*z;
        public float magnitude => MathF.Sqrt(sqrMagnitude);
        public Vector3 normalized => magnitude > 1e-6f ? this * (1f / magnitude) : zero;
        internal N.Vector3 Numerics => new(x,y,z);
        internal static Vector3 From(N.Vector3 v) => new(v.X,v.Y,v.Z);
        public static Vector3 operator +(Vector3 a, Vector3 b) => From(a.Numerics + b.Numerics);
        public static Vector3 operator -(Vector3 a, Vector3 b) => From(a.Numerics - b.Numerics);
        public static Vector3 operator -(Vector3 a) => From(-a.Numerics);
        public static Vector3 operator *(Vector3 a, float b) => From(a.Numerics * b);
        public static Vector3 Scale(Vector3 a, Vector3 b) => From(a.Numerics * b.Numerics);
        public static Vector3 Cross(Vector3 a, Vector3 b) => From(N.Vector3.Cross(a.Numerics,b.Numerics));
        public static float Dot(Vector3 a, Vector3 b) => N.Vector3.Dot(a.Numerics,b.Numerics);
    }

    public partial struct Quaternion
    {
        private N.Quaternion value;
        private Quaternion(N.Quaternion value) { this.value = value; }
        public static Quaternion identity => new(N.Quaternion.Identity);
        public static Quaternion AngleAxis(float angle, Vector3 axis) =>
            new(N.Quaternion.CreateFromAxisAngle(axis.normalized.Numerics, angle * MathF.PI / 180f));
        public static Quaternion LookRotation(Vector3 direction) =>
            AngleAxis(MathF.Atan2(direction.x, direction.z) * 180f / MathF.PI, Vector3.up);
        public static Quaternion Inverse(Quaternion value) => new(N.Quaternion.Inverse(value.value));
        public static Quaternion operator *(Quaternion a, Quaternion b) => new(a.value * b.value);
        public static Vector3 operator *(Quaternion a, Vector3 b) => Vector3.From(N.Vector3.Transform(b.Numerics, a.value));
    }

    public sealed class GameObject
    {
        public Transform transform { get; }
        public GameObject(string name) { transform = new Transform(name); }
    }

    public sealed partial class Transform
    {
        public string name;
        public Transform parent;
        public Quaternion localRotation = Quaternion.identity;
        public Vector3 localPosition;
        public Vector3 lossyScale = Vector3.one;
        public Collider Component;
        readonly List<Transform> children = new();
        public Transform(string name) { this.name = name; }
        public Quaternion rotation
        {
            get => parent == null ? localRotation : parent.rotation * localRotation;
            set => localRotation = parent == null ? value : Quaternion.Inverse(parent.rotation) * value;
        }
        public Vector3 position
        {
            get => parent == null ? localPosition : parent.position + parent.rotation * localPosition;
            set => localPosition = parent == null ? value : Quaternion.Inverse(parent.rotation) * (value - parent.position);
        }
        public void SetParent(Transform value, bool preserve)
        {
            Vector3 before = position;
            parent?.children.Remove(this);
            parent = value;
            value?.children.Add(this);
            if (preserve) position = before;
        }
        public T GetComponent<T>() where T : class => Component as T;
        public T[] GetComponentsInChildren<T>(bool _) where T : class
        {
            var result = new List<T>();
            if (this is T match) result.Add(match);
            foreach (var child in children) result.AddRange(child.GetComponentsInChildren<T>(true));
            return result.ToArray();
        }
        public Transform Find(string name) => children.Find(t => t.name == name);
        public bool IsChildOf(Transform candidate) => this == candidate || (parent != null && parent.IsChildOf(candidate));
        public Vector3 InverseTransformDirection(Vector3 direction) => Quaternion.Inverse(rotation) * direction;
    }

    public class Collider
    {
        public Transform transform;
        public object Owner;
        public T GetComponentInParent<T>() where T : class => Owner as T ?? transform?.GetComponent<T>();
    }
    public struct Bounds { public Vector3 center; }
    public sealed class BoxCollider : Collider
    {
        public Vector3 center, size;
        public Bounds bounds => new() { center = transform.position + transform.rotation * center };
        public Vector3 ClosestPoint(Vector3 world)
        {
            var local = Quaternion.Inverse(transform.rotation) * (world - bounds.center);
            local.x = Math.Clamp(local.x, -size.x/2, size.x/2);
            local.y = Math.Clamp(local.y, -size.y/2, size.y/2);
            local.z = Math.Clamp(local.z, -size.z/2, size.z/2);
            return bounds.center + transform.rotation * local;
        }
    }

    public static class Time { public static float time, deltaTime; }
    public static partial class Mathf
    {
        public static float Abs(float a) => MathF.Abs(a);
        public static float Max(float a, float b) => MathF.Max(a,b);
        public static float Clamp(float value, float min, float max) => Math.Clamp(value,min,max);
        public static int CeilToInt(float value) => (int)MathF.Ceiling(value);
        public static float Lerp(float a,float b,float t) => a + (b-a)*t;
        public static float SmoothDampAngle(float current, float target, ref float velocity, float smooth, float speed, float dt)
        {
            // En la prueba solo se usa el intervalo de 0 a 85 grados.
            float omega = 2f / smooth;
            float x = omega * dt;
            float decay = 1f / (1f + x + .48f*x*x + .235f*x*x*x);
            float change = Clamp(current-target, -speed*smooth, speed*smooth);
            float goal = current - change;
            float temp = (velocity + omega*change)*dt;
            velocity = (velocity-omega*temp)*decay;
            float result = goal + (change+temp)*decay;
            if ((target-current > 0f) == (result > target))
            {
                result = target;
                velocity = 0f;
            }
            return result;
        }
    }

    public static partial class Physics
    {
        public const int ActorMask = (1 << 29) | (1 << 30);
        public static bool Occupant, AllSweepBlocked, Saturated;
        public static Vector3? BlockerPoint;
        public static Collider OwnLeaf;
        public static int SweepCalls;
        private static readonly Collider Blocker = new() { transform = new Transform("Obstruction") };
        public static void SyncTransforms() {}
        public static int OverlapBoxNonAlloc(Vector3 center, Vector3 half, Collider[] hits, Quaternion pose, int mask, QueryTriggerInteraction _)
        {
            if (mask == ActorMask)
            {
                if (Occupant) { hits[0] = Blocker; return 1; }
                return 0;
            }
            SweepCalls++;
            if (Saturated)
            {
                Array.Fill(hits, OwnLeaf);
                return hits.Length;
            }
            if (AllSweepBlocked || (BlockerPoint.HasValue && Inside(BlockerPoint.Value, center, half, pose)))
            {
                hits[0] = Blocker;
                return 1;
            }
            if (OwnLeaf != null) { hits[0] = OwnLeaf; return 1; }
            return 0;
        }
        private static bool Inside(Vector3 point, Vector3 center, Vector3 half, Quaternion pose)
        {
            Vector3 local = Quaternion.Inverse(pose) * (point-center);
            return MathF.Abs(local.x) <= half.x && MathF.Abs(local.y) <= half.y && MathF.Abs(local.z) <= half.z;
        }
        public static void Reset()
        {
            Occupant = AllSweepBlocked = Saturated = false;
            OwnLeaf = null;
            BlockerPoint = null;
            SweepCalls = 0;
        }
    }
}
