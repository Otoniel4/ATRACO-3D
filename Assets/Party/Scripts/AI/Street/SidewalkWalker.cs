using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.AI.Street
{
    // Peatón que pasea por la red de aceras: sigue tramos al azar sin volver atrás y, ante un paso con semáforo,
    // espera a que la vía que va a cruzar esté en rojo con tiempo suficiente para llegar al otro lado.
    public sealed class SidewalkWalker : MonoBehaviour
    {
        private static readonly int SpeedParameter = Animator.StringToHash("Speed");
        private const float WalkSpeed = 1.4f, AnimatorWalk = 1.6f, TurnSpeed = 300f, CrossingMargin = 2f;

        [SerializeField] private Animator animator;
        private SidewalkGraph graph;
        private ITrafficSignals signals;
        private System.Random random;
        private int previous, current, next, edge;
        private float lateral;
        private bool waiting;
        private Vector3 target;

        public void Configure(Animator body) => animator = body;

        public void Begin(SidewalkGraph network, ITrafficSignals lights, int node, int seed)
        {
            graph = network; signals = lights; random = new System.Random(seed);
            lateral = (float)(random.NextDouble() * 1.2 - .6); // cada uno camina por su carril de la acera
            previous = -1; current = node;
            transform.position = graph.Position(node);
            ChooseNext();
            if (next >= 0) transform.rotation = Quaternion.LookRotation(Flat(target - transform.position));
        }

        private void ChooseNext()
        {
            int start = graph.EdgeStart(current), count = graph.EdgeEnd(current) - start;
            next = -1;
            if (count == 0) return;
            // Se evita volver por donde vino salvo en un callejón sin salida.
            int pick = random.Next(count);
            for (int i = 0; i < count; i++)
            {
                int e = start + (pick + i) % count;
                if (count == 1 || graph.Target(e) != previous) { edge = e; break; }
            }
            next = graph.Target(edge);
            target = graph.Position(next);
            if (graph.Signal(edge) == SidewalkGraph.Sidewalk)
            {
                Vector3 along = Flat(target - graph.Position(current));
                target += new Vector3(along.z, 0f, -along.x) * lateral;
            }
            waiting = graph.Signal(edge) >= 0;
        }

        private void Update()
        {
            if (graph == null || next < 0) { animator.SetFloat(SpeedParameter, 0f); return; }
            Vector3 position = transform.position;
            Vector3 toTarget = Flat(target - position);
            if (waiting)
            {
                float crossing = toTarget.magnitude / WalkSpeed + CrossingMargin;
                int s = graph.Signal(edge), a = graph.Axis(edge);
                waiting = !(signals.Light(s, a) == SignalLight.Red && signals.SecondsUntilGreen(s, a) > crossing);
                if (waiting) { Turn(toTarget); animator.SetFloat(SpeedParameter, 0f); return; }
            }
            float step = WalkSpeed * Time.deltaTime;
            if (toTarget.magnitude <= step)
            {
                transform.position = new Vector3(target.x, SidewalkGraph.Height, target.z);
                previous = current; current = next;
                ChooseNext();
            }
            else
            {
                transform.position = position + toTarget.normalized * step;
                Turn(toTarget);
            }
            animator.SetFloat(SpeedParameter, AnimatorWalk);
        }

        private void Turn(Vector3 direction)
        {
            if (direction.sqrMagnitude < .0001f) return;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(direction), TurnSpeed * Time.deltaTime);
        }

        private static Vector3 Flat(Vector3 v) { v.y = 0f; return v; }
    }
}
