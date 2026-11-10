using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Mueve al doble de reacción sin NavMesh: corre o camina alejándose de la amenaza, esquiva paredes y autos tanteando
    // con rayos en abanico (a la altura de la cintura y de la canilla, para ver también muebles bajos) y se pega al
    // suelo sin subirse a nada más alto que un escalón.
    public sealed class NpcFleeMotor : MonoBehaviour
    {
        private const float ProbeHeight = .9f, LowProbeHeight = .3f, ProbeDistance = 1.8f, TurnSpeed = 300f, StepHeight = .35f;
        private static readonly float[] Fan = { 0f, 35f, -35f, 70f, -70f, 110f, -110f, 150f, -150f };
        [SerializeField, Tooltip("Lo que se esquiva y el suelo que se pisa: todo menos personajes (29, 30) e interfaz (31).")]
        private LayerMask obstacles = ~((1 << 29) | (1 << 30) | (1 << 31));
        private Vector3 awayFrom;
        private float speed;

        public bool Moving => speed > 0f;

        public void MoveAwayFrom(Vector3 point, float metersPerSecond) { awayFrom = point; speed = Mathf.Max(0f, metersPerSecond); }
        public void Stop() => speed = 0f;

        private void Update()
        {
            if (speed <= 0f) return;
            Vector3 want = transform.position - awayFrom;
            want.y = 0f;
            want = want.sqrMagnitude > .01f ? want.normalized : transform.forward;
            want = FreeDirection(want);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(want), TurnSpeed * Time.deltaTime);
            Vector3 next = transform.position + transform.forward * (speed * Time.deltaTime);
            if (Physics.Raycast(next + Vector3.up, Vector3.down, out var ground, 2.5f, obstacles, QueryTriggerInteraction.Ignore))
            {
                if (ground.point.y - transform.position.y > StepHeight) return; // un mueble o un mostrador: no se sube, sigue girando
                next.y = ground.point.y;
            }
            transform.position = next;
        }

        // La primera dirección del abanico sin obstáculo cerca; si todo está tapado, da la vuelta.
        private Vector3 FreeDirection(Vector3 want)
        {
            foreach (float angle in Fan)
            {
                Vector3 direction = Quaternion.AngleAxis(angle, Vector3.up) * want;
                if (!Blocked(ProbeHeight, direction) && !Blocked(LowProbeHeight, direction)) return direction;
            }
            return -want;
        }

        private bool Blocked(float height, Vector3 direction)
            => Physics.Raycast(transform.position + Vector3.up * height, direction, ProbeDistance, obstacles, QueryTriggerInteraction.Ignore);
    }
}
