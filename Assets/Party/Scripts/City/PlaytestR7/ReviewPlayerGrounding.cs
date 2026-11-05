using UnityEngine;

namespace Alarma.City.Playtest
{
    // Una única regla para validar el inicio en el editor y colocar los pies en Play.
    public static class ReviewPlayerGrounding
    {
        public const float FeetClearance = .035f;
        private const float ProbeAboveFeet = .28f;
        private const float MaximumDrop = .65f;
        private const int EnvironmentMask = ~((1 << 29) | (1 << 30) | (1 << 31));
        private static readonly Collider[] Obstructions = new Collider[1];

        public static bool TryResolve(PhysicsScene physics, Vector3 requestedFeet, float height, float radius,
            float slopeLimit, out Vector3 groundedFeet, out RaycastHit support)
        {
            groundedFeet = requestedFeet;
            support = default;
            if (!physics.IsValid() || height < radius * 2f || radius <= 0f) return false;
            // La sonda nace cerca de los pies: una losa o un toldo superior nunca se convierte en suelo inicial.
            if (!physics.Raycast(requestedFeet + Vector3.up * ProbeAboveFeet, Vector3.down, out support,
                ProbeAboveFeet + MaximumDrop, EnvironmentMask, QueryTriggerInteraction.Ignore)) return false;
            if (support.normal.y < Mathf.Cos(slopeLimit * Mathf.Deg2Rad)) return false;
            var candidate = support.point + Vector3.up * FeetClearance;
            int blocked = physics.OverlapCapsule(candidate + Vector3.up * radius,
                candidate + Vector3.up * (height - radius), radius, Obstructions,
                EnvironmentMask, QueryTriggerInteraction.Ignore);
            Obstructions[0] = null;
            if (blocked != 0) return false;
            groundedFeet = candidate;
            return true;
        }
    }
}
