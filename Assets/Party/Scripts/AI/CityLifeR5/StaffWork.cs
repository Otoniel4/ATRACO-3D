using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Trabajo de un empleado en su puesto: cada tanto lleva la mano a uno de sus puntos de trabajo (teclado, plancha,
    // estante, vitrina) y, si está de pie, usa el gesto de manipular. Se pausa mientras atiende a un cliente.
    public sealed class StaffWork : MonoBehaviour
    {
        private static readonly int Browse = Animator.StringToHash("Browse");
        [SerializeField] private Transform[] points = System.Array.Empty<Transform>();
        [SerializeField] private PedestrianReach reach;
        [SerializeField] private Animator animator;
        [SerializeField] private bool gesture;
        [SerializeField, Min(.2f)] private float reachSeconds = 1.2f;
        [SerializeField, Min(0f)] private float restMin = 1.5f, restMax = 4f;
        private System.Random random;
        private float until, next;
        private int current;

        public bool Paused { get; set; }

        public void Configure(Transform[] work, PedestrianReach hand, Animator body, bool useGesture, float seconds, float minRest, float maxRest)
        {
            points = work; reach = hand; animator = body; gesture = useGesture;
            reachSeconds = seconds; restMin = minRest; restMax = Mathf.Max(minRest, maxRest);
        }

        private void OnEnable()
        {
            random = new System.Random(GetInstanceID());
            next = Time.time + Rest();
        }

        private void Update()
        {
            bool working = false;
            if (!Paused && points.Length > 0 && reach != null)
            {
                if (Time.time >= next)
                {
                    current = random.Next(points.Length);
                    until = Time.time + reachSeconds;
                    next = until + Rest();
                }
                working = Time.time < until;
                if (working) reach.Reach(points[current], .15f);
            }
            if (gesture && animator != null && animator.enabled) animator.SetBool(Browse, working);
        }

        private float Rest() => restMin + (float)random.NextDouble() * (restMax - restMin);
    }
}
