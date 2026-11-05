using System.Collections.Generic;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Vehicles;

namespace Alarma.Traffic
{
    // Conductor de un auto: sigue su carril, frena con calma antes de doblar o detenerse, pone el intermitente,
    // gira las ruedas delanteras en la curva y frena fuerte solo si algo se cruza (autos, peatones, jugador).
    [RequireComponent(typeof(Rigidbody))]
    public sealed class TrafficCar : MonoBehaviour, IVehicleState
    {
        private const float Acceleration = 2.2f, ComfortBrake = 2.8f, BrakeRate = 7f, StopWait = 1.2f, YieldSpeed = 4f;
        private const float TurnSpeed = 4.5f, MaxSteer = 32f, SignalDistance = 35f;
        private static readonly int Obstacles = (1 << 28) | (1 << 29) | (1 << 30); // autos, personajes y jugador

        [SerializeField] private Transform[] wheels = System.Array.Empty<Transform>();
        [SerializeField] private float wheelRadius = .34f;
        [SerializeField] private Vector3 halfSize = new Vector3(1f, .75f, 2.2f);

        private readonly List<Vector3> path = new List<Vector3>(32);
        private readonly Collider[] hits = new Collider[6];
        private Quaternion[] wheelRest;
        private bool[] frontWheel;
        private RoadNetwork network;
        private ITrafficSignals signals;
        private System.Random random;
        private Collider body;
        private int link, upcoming, index, turnSide;
        private bool turning, mustStop, obstacle;
        private float speed, waited, nextScan, remaining, spin, steer;

        public bool Braking { get; private set; }
        // El intermitente se enciende en los últimos metros antes de doblar y durante la curva.
        public int TurnSignal => turning || remaining < SignalDistance ? turnSide : 0;

        public void Configure(Transform[] wheelTransforms, Vector3 bodyHalfSize, float radius)
        {
            wheels = wheelTransforms; halfSize = bodyHalfSize; wheelRadius = radius;
        }

        private void Awake()
        {
            // Pose de cada rueda respecto del auto, para girarla (avance) y doblarla (dirección) sin acumular errores.
            wheelRest = new Quaternion[wheels.Length]; frontWheel = new bool[wheels.Length];
            for (int i = 0; i < wheels.Length; i++)
            {
                wheelRest[i] = Quaternion.Inverse(transform.rotation) * wheels[i].rotation;
                frontWheel[i] = transform.InverseTransformPoint(wheels[i].position).z > 0f;
            }
        }

        public void Begin(RoadNetwork roads, ITrafficSignals lights, int startLink, int startPoint, int seed)
        {
            network = roads; signals = lights; random = new System.Random(seed);
            body = GetComponent<Collider>();
            speed = 0f; steer = 0f;
            obstacle = false; nextScan = 0f; Braking = false;
            Follow(startLink, Mathf.Clamp(startPoint, 0, network.PointCount(startLink) - 2));
            transform.SetPositionAndRotation(path[index - 1], Quaternion.LookRotation(path[index] - path[index - 1]));
        }

        private void Follow(int newLink, int fromPoint)
        {
            link = newLink; turning = false; mustStop = false; waited = 0f;
            path.Clear();
            for (int i = fromPoint; i < network.PointCount(link); i++) path.Add(network.Point(link, i));
            index = 1;
            upcoming = network.Next(link, random.Next(network.NextCount(link)));
            int last = network.PointCount(link) - 1;
            Vector3 dirIn = network.Point(link, last) - network.Point(link, last - 1), dirOut = network.Point(upcoming, 1) - network.Point(upcoming, 0);
            float side = (dirIn.z * dirOut.x - dirIn.x * dirOut.z) / Mathf.Max(.001f, dirIn.magnitude * dirOut.magnitude);
            turnSide = side > .35f ? 1 : side < -.35f ? -1 : 0;
        }

        // Curva dentro del cruce desde la línea de parada hasta el inicio del enlace siguiente.
        private void Turn()
        {
            Vector3 a = path[path.Count - 1], dirIn = (a - path[path.Count - 2]).normalized;
            Vector3 b = network.Point(upcoming, 0), dirOut = (network.Point(upcoming, 1) - b).normalized;
            Vector3 control = Vector3.Dot(dirIn, dirOut) > .95f ? (a + b) * .5f : Crossing(a, dirIn, b, dirOut);
            path.Clear();
            for (int i = 0; i <= 16; i++) { float t = i / 16f; path.Add((1 - t) * (1 - t) * a + 2 * (1 - t) * t * control + t * t * b); }
            index = 1; turning = true;
        }

        private static Vector3 Crossing(Vector3 a, Vector3 da, Vector3 b, Vector3 db)
        {
            float denominator = da.x * db.z - da.z * db.x;
            if (Mathf.Abs(denominator) < 1e-4f) return (a + b) * .5f;
            float t = ((b.x - a.x) * db.z - (b.z - a.z) * db.x) / denominator;
            Vector3 point = a + da * Mathf.Clamp(t, 0f, Vector3.Distance(a, b));
            point.y = a.y;
            return point;
        }

        private void Update()
        {
            if (network == null) return;
            float dt = Time.deltaTime;
            // Una espera larga no desactiva la detección. El auto vuelve a avanzar al despejarse el carril.
            if (Time.time >= nextScan)
            {
                nextScan = Time.time + .1f;
                obstacle = Blocked();
            }
            remaining = turning ? 0f : Remaining();
            float cruise = network.Speed(link);
            float target = turning ? (turnSide != 0 ? TurnSpeed : cruise * .8f) : cruise;
            // Reduce de a poco para llegar a la curva a velocidad de giro, como un conductor real.
            if (!turning && turnSide != 0) target = Mathf.Min(target, Mathf.Sqrt(TurnSpeed * TurnSpeed + 2f * ComfortBrake * remaining));
            if (!turning) target = Mathf.Min(target, LineSpeed(dt));
            if (obstacle) target = 0f;
            float rate = target > speed ? Acceleration : (obstacle || speed - target > 2.5f ? BrakeRate : ComfortBrake);
            speed = Mathf.MoveTowards(speed, target, rate * dt);
            Braking = target < speed - .05f || (speed < .3f && target < .1f);
            Advance(speed * dt);
            AnimateWheels(dt);
        }

        // Velocidad para detenerse con suavidad en la línea de parada cuando hace falta.
        private float LineSpeed(float dt)
        {
            var control = network.Control(link);
            if (control == LinkControl.Free) return float.MaxValue;
            if (control == LinkControl.Yield) return Mathf.Max(YieldSpeed, Mathf.Sqrt(2f * ComfortBrake * remaining));
            if (control == LinkControl.Signal)
            {
                // Frena si puede detenerse antes de la línea; en amarillo pide holgura, y si ya no alcanza, pasa.
                var light = signals.Light(network.Signal(link), network.Axis(link));
                float braking = speed * speed / (2f * BrakeRate);
                mustStop = light == SignalLight.Red ? remaining + .1f > braking : light == SignalLight.Yellow && remaining > braking + 1f;
            }
            else if (control == LinkControl.Stop)
            {
                mustStop = waited < StopWait;
                if (remaining < .4f && speed < .1f) waited += dt;
            }
            return mustStop ? Mathf.Sqrt(2f * ComfortBrake * Mathf.Max(0f, remaining - .3f)) : float.MaxValue;
        }

        private float Remaining()
        {
            float total = Vector3.Distance(transform.position, path[index]);
            for (int i = index; i < path.Count - 1; i++) total += Vector3.Distance(path[i], path[i + 1]);
            return total;
        }

        private void Advance(float distance)
        {
            Vector3 position = transform.position;
            while (distance > 0f)
            {
                Vector3 toNext = path[index] - position;
                float length = toNext.magnitude;
                if (length > distance) { position += toNext / length * distance; break; }
                position = path[index]; distance -= length; index++;
                if (index < path.Count) continue;
                if (turning) Follow(upcoming, 0);
                else if (mustStop) { index = path.Count - 1; break; }
                else Turn();
            }
            transform.position = position;
            // Mira hacia un punto un poco más adelante del camino: el giro del auto queda suave y sin saltos.
            Vector3 ahead = AheadPoint(position, 2.2f + speed * .35f) - position;
            ahead.y = 0f;
            if (ahead.sqrMagnitude > .01f)
            {
                float angle = Vector3.SignedAngle(transform.forward, ahead, Vector3.up);
                steer = Mathf.Lerp(steer, Mathf.Clamp(angle * 2.5f, -MaxSteer, MaxSteer), 6f * Time.deltaTime);
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(ahead), 5f * Time.deltaTime);
            }
        }

        private Vector3 AheadPoint(Vector3 from, float distance)
        {
            Vector3 previous = from;
            for (int i = Mathf.Min(index, path.Count - 1); i < path.Count; i++)
            {
                float step = Vector3.Distance(previous, path[i]);
                if (step >= distance) return previous + (path[i] - previous) * (distance / step);
                distance -= step; previous = path[i];
            }
            // Al final de la curva se mira hacia el enlace siguiente; al final del carril, de frente.
            return turning ? network.Point(upcoming, Mathf.Min(1, network.PointCount(upcoming) - 1)) : previous + transform.forward * distance;
        }

        private void AnimateWheels(float dt)
        {
            spin = Mathf.Repeat(spin + speed * dt / wheelRadius * Mathf.Rad2Deg, 360f);
            for (int i = 0; i < wheels.Length; i++)
                wheels[i].rotation = transform.rotation * Quaternion.Euler(0f, frontWheel[i] ? steer : 0f, 0f) * Quaternion.Euler(spin, 0f, 0f) * wheelRest[i];
        }

        private bool Blocked()
        {
            float look = 2.5f + speed * 1.3f;
            Vector3 center = transform.position + transform.forward * (halfSize.z + look / 2f) + Vector3.up * .9f;
            int count = Physics.OverlapBoxNonAlloc(center, new Vector3(halfSize.x * .8f, .7f, look / 2f), hits, transform.rotation, Obstacles, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++) if (hits[i] != body) return true;
            return false;
        }
    }
}
