using UnityEngine;

namespace Alarma.AI.Street
{
    // Comprueba el apoyo y el volumen completo de cada peatón antes de moverlo.
    public static class SidewalkClearance
    {
        public const float Radius = .25f, BodyHeight = 1.7f, FeetGap = .035f;
        private const float MaximumStep = .18f;
        public const int StaticMask = ~((1 << 28) | (1 << 29) | (1 << 30) | (1 << 31));
        private const int BodyMask = ~(1 << 31);
        private static readonly Collider[] Overlaps = new Collider[32];
        private static readonly RaycastHit[] Casts = new RaycastHit[32];

        public static bool TryGround(Vector3 proposed, out Vector3 feet)
        {
            feet = proposed;
            if (!Physics.Raycast(proposed + Vector3.up * .3f, Vector3.down, out var hit, .7f,
                StaticMask, QueryTriggerInteraction.Ignore) || hit.normal.y < .65f) return false;
            feet.y = hit.point.y + FeetGap;
            return Mathf.Abs(feet.y - proposed.y) <= .28f;
        }

        public static bool IsFree(Vector3 feet, Transform self, float padding = 0f)
        {
            Physics.SyncTransforms();
            float radius = Radius + padding;
            int count = Physics.OverlapCapsuleNonAlloc(feet + Vector3.up * radius,
                feet + Vector3.up * (BodyHeight - radius), radius, Overlaps, BodyMask, QueryTriggerInteraction.Ignore);
            bool free = count < Overlaps.Length;
            for (int i = 0; i < count; i++)
            {
                Collider hit = Overlaps[i];
                Overlaps[i] = null;
                if (hit != null && (self == null || !hit.transform.IsChildOf(self))) free = false;
            }
            return free;
        }

        public static bool TryMove(Vector3 from, Vector3 proposed, Transform self, out Vector3 feet)
        {
            feet = from;
            if (!TryGround(proposed, out Vector3 destination)) return false;
            if (TravelIsFree(from, destination, self)) { feet = destination; return true; }
            Vector3 forward = destination - from;
            forward.y = 0f;
            if (forward.sqrMagnitude < .000001f) return false;
            Vector3 reach = forward.normalized * Radius;
            // En el descenso, el centro ya ve el piso bajo mientras la parte trasera aún apoya sobre el bordillo.
            float descent = from.y - destination.y;
            if (descent > .015f && descent <= MaximumStep && TryGround(destination - reach, out Vector3 behind)
                && behind.y > destination.y + .015f && behind.y <= from.y + .015f)
            {
                Vector3 supported = new Vector3(destination.x, Mathf.Max(behind.y, from.y), destination.z);
                if (TravelIsFree(from, supported, self)) { feet = supported; return true; }
            }
            if (!TryGround(destination + reach, out Vector3 ahead)
                || ahead.y <= destination.y + .015f || ahead.y - from.y > MaximumStep) return false;
            destination.y = ahead.y;
            if (!TravelIsFree(from, destination, self)) return false;
            feet = destination;
            return true;
        }

        private static bool TravelIsFree(Vector3 from, Vector3 destination, Transform self)
        {
            if (!IsFree(destination, self)) return false;
            // Subir antes del avance horizontal y bajar después permite salvar el bordillo sin cruzar su malla.
            float high = Mathf.Max(from.y, destination.y);
            Vector3 a = new Vector3(from.x, high, from.z), b = new Vector3(destination.x, high, destination.z);
            return Sweep(from, a, self) && Sweep(a, b, self) && Sweep(b, destination, self);
        }

        public static bool CrossingClear(Vector3 from, Vector3 to, bool checkApproach = true)
        {
            Physics.SyncTransforms();
            Vector3 direction = to - from;
            direction.y = 0;
            Vector3 lane = new Vector3(direction.z, 0f, -direction.x).normalized;
            Vector3 raise = Vector3.up * .7f;
            // Prolonga el margen de detección a ambos lados del paso, sin ocupar toda la esquina.
            int count = Physics.OverlapCapsuleNonAlloc(from + raise, to + raise,
                .85f, Overlaps, 1 << 28, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++) Overlaps[i] = null;
            if (count != 0 || !checkApproach) return count == 0;
            Vector3 middle = Vector3.Lerp(from, to, .5f) + raise;
            count = Physics.OverlapCapsuleNonAlloc(middle - lane * 5f, middle + lane * 5f,
                .75f, Overlaps, 1 << 28, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++) Overlaps[i] = null;
            return count == 0;
        }

        private static bool Sweep(Vector3 from, Vector3 to, Transform self)
        {
            Vector3 delta = to - from;
            float distance = delta.magnitude;
            if (distance < .00001f) return true;
            int count = Physics.CapsuleCastNonAlloc(from + Vector3.up * Radius,
                from + Vector3.up * (BodyHeight - Radius), Radius, delta / distance,
                Casts, distance, BodyMask, QueryTriggerInteraction.Ignore);
            if (count == Casts.Length) return false;
            for (int i = 0; i < count; i++)
            {
                Collider hit = Casts[i].collider;
                if (hit != null && (self == null || !hit.transform.IsChildOf(self))) return false;
            }
            return true;
        }
    }
}
