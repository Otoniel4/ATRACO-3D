using System.Collections.Generic;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.Pathing;

namespace Alarma.AI.Reactions
{
    // Mueve a un NPC sin NavMesh (doble de reacción, guardia, policía), caminando o corriendo. No va en línea recta:
    // pide un camino a GridPathfinder, que rodea muebles, paredes y autos, y lo sigue punto por punto pegado al suelo.
    // Tres formas de moverse: hacia un punto (MoveTowards), alejándose de una amenaza (MoveAwayFrom: elige un lugar
    // lejos al que sí se pueda llegar) y hasta la salida de un local para después alejarse (MoveThrough).
    // Si no hay camino queda quieto y lo avisa con «Blocked»: quien lo usa decide qué hacer (un civil se agacha).
    public sealed class NpcFleeMotor : MonoBehaviour
    {
        private enum Mode { Idle, Seek, Flee, Exit }

        private const float TurnSpeed = 420f, ArriveDistance = .3f, FleeStep = 12f;
        private const float DoorReach = 1.6f, DoorInterval = .2f;
        private static readonly Collider[] Nearby = new Collider[12];
        private const float SeekRepath = .6f, FleeRepath = 2.5f, BlockedRetry = 1.5f, RetargetDistance = 1f;
        private static readonly float[] Fan = { 0f, 40f, -40f, 80f, -80f, 120f, -120f, 165f }; // hacia dónde probar al huir
        [SerializeField, Tooltip("El suelo que se pisa: todo menos personajes (29, 30) e interfaz (31).")]
        private LayerMask ground = ~((1 << 29) | (1 << 30) | (1 << 31));
        private readonly List<Vector3> path = new List<Vector3>();
        private Mode mode;
        private Vector3 target, pathTarget, exit, avoid;
        private float speed, nextSearch, maxExitPath, avoidRadius;
        private int step;
        private float nextDoors;

        public bool Moving => speed > 0f && mode != Mode.Idle;
        // Todavía va hacia la salida del local que le dieron.
        public bool OnRoute => mode == Mode.Exit;
        // No encontró por dónde ir (encerrado, la salida tapada o demasiado lejos): está quieto.
        public bool Blocked { get; private set; }

        // Va hacia «point» rodeando lo que haya (quien lo llama decide cuándo llegó).
        public void MoveTowards(Vector3 point, float metersPerSecond)
        {
            if (mode != Mode.Seek) { mode = Mode.Seek; Restart(); }
            target = point; speed = Mathf.Max(0f, metersPerSecond);
        }

        // Se aleja de «point». Si está yendo a la salida de un local, primero termina de salir.
        public void MoveAwayFrom(Vector3 point, float metersPerSecond)
        {
            if (mode != Mode.Flee && mode != Mode.Exit) { mode = Mode.Flee; Restart(); }
            target = point; speed = Mathf.Max(0f, metersPerSecond);
        }

        // Va hasta el final de «points» (la acera frente a la puerta de un local) y después se aleja de «thenAwayFrom».
        // No sale si el camino mide más de «maxPath» metros o pasa a menos de «clearance» de la amenaza: queda Blocked.
        public void MoveThrough(Vector3[] points, Vector3 thenAwayFrom, float metersPerSecond, float maxPath = float.PositiveInfinity, float clearance = 0f)
        {
            mode = Mode.Exit; Restart();
            exit = points[points.Length - 1]; target = thenAwayFrom; speed = Mathf.Max(0f, metersPerSecond);
            maxExitPath = maxPath; avoid = thenAwayFrom; avoidRadius = clearance;
        }

        public void Stop() { mode = Mode.Idle; speed = 0f; path.Clear(); Blocked = false; }

        private void Restart() { path.Clear(); step = 0; nextSearch = 0f; Blocked = false; }

        private void Update()
        {
            if (!Moving) return;
            if (NeedsPath() && Time.time >= nextSearch && GridPathfinder.Ready) Search();
            if (step >= path.Count) return;
            Vector3 to = path[step] - transform.position;
            to.y = 0f;
            if (to.sqrMagnitude <= ArriveDistance * ArriveDistance)
            {
                if (++step >= path.Count && mode == Mode.Exit) { mode = Mode.Flee; Restart(); } // ya salió: ahora se aleja
                return;
            }
            Vector3 heading = to.normalized;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(heading), TurnSpeed * Time.deltaTime);
            Vector3 next = transform.position + heading * Mathf.Min(speed * Time.deltaTime, to.magnitude);
            if (Physics.Raycast(next + Vector3.up, Vector3.down, out var floor, 2.5f, ground, QueryTriggerInteraction.Ignore)) next.y = floor.point.y;
            // Algo se puso en el camino después de calcularlo (un auto, otro mueble): no lo atraviesa, busca de nuevo.
            if (!GridPathfinder.Fits(next)) { path.Clear(); step = 0; nextSearch = Time.time + .2f; return; }
            transform.position = next;
            if (Time.time >= nextDoors) { nextDoors = Time.time + DoorInterval; PushDoors(); }
        }

        // Empuja las puertas de los locales que tiene delante: el camino pasa por ellas como si estuvieran abiertas.
        private void PushDoors()
        {
            int count = Physics.OverlapSphereNonAlloc(transform.position + Vector3.up, DoorReach, Nearby, ~0, QueryTriggerInteraction.Collide);
            for (int i = 0; i < count; i++)
            {
                var door = Nearby[i].GetComponentInParent<ShopDoor>();
                if (door != null) door.PushFrom(transform.position);
            }
        }

        private bool NeedsPath()
        {
            if (step >= path.Count) return true; // sin camino o ya lo terminó
            if (mode == Mode.Seek) return (target - pathTarget).sqrMagnitude > RetargetDistance * RetargetDistance; // el blanco se movió
            return false;
        }

        private void Search()
        {
            bool found = mode == Mode.Seek ? GridPathfinder.TryFind(transform.position, target, path)
                       : mode == Mode.Exit ? FindExit()
                       : FindAway();
            step = found && path.Count > 1 ? 1 : 0; // el primer punto es donde ya está
            if (!found) path.Clear();
            pathTarget = target;
            Blocked = !found;
            nextSearch = Time.time + (found ? (mode == Mode.Seek ? SeekRepath : FleeRepath) : BlockedRetry) + Random.value * .2f;
        }

        private bool FindExit()
        {
            if (!GridPathfinder.TryFind(transform.position, exit, path, 1.2f)) return false;
            if (GridPathfinder.Length(path) > maxExitPath) return false; // está al fondo: no llega
            foreach (var point in path)
            {
                Vector3 gap = point - avoid;
                gap.y = 0f;
                if (gap.sqrMagnitude < avoidRadius * avoidRadius) return false; // la amenaza le tapa la salida
            }
            return true;
        }

        // Un lugar a FleeStep metros, primero derecho en contra de la amenaza y si no en abanico, al que se pueda llegar.
        private bool FindAway()
        {
            Vector3 away = transform.position - target;
            away.y = 0f;
            away = away.sqrMagnitude > .01f ? away.normalized : transform.forward;
            foreach (float angle in Fan)
            {
                Vector3 goal = transform.position + Quaternion.AngleAxis(angle, Vector3.up) * away * FleeStep;
                if (GridPathfinder.Standable(goal) && GridPathfinder.TryFind(transform.position, goal, path, 1.5f, FleeStep * 2f)) return true;
            }
            return false;
        }
    }
}
