using UnityEngine;

namespace Alarma.Player.Items
{
    // IK de dos huesos (brazo y antebrazo) que lleva la palma a un punto conservando el largo de cada hueso.
    // El codo se dobla hacia «bend» (por ejemplo, abajo y afuera).
    internal static class TwoBoneIk
    {
        public static void Solve(Transform upper, Transform lower, Transform palm, Vector3 target, Vector3 bend, float weight)
        {
            if (weight <= 0f || upper == null || lower == null || palm == null) return;
            Vector3 shoulder = upper.position;
            Vector3 upperBone = lower.position - shoulder;
            float a = upperBone.magnitude, b = Vector3.Distance(lower.position, palm.position);
            Vector3 reach = target - shoulder;
            if (a < .001f || b < .001f || reach.sqrMagnitude < .000001f) return;
            Vector3 direction = reach.normalized;
            float distance = Mathf.Clamp(reach.magnitude, Mathf.Abs(a - b) + .001f, a + b - .001f);
            float along = (a * a - b * b + distance * distance) / (2f * distance);
            Vector3 side = Vector3.ProjectOnPlane(bend, direction);
            if (side.sqrMagnitude < .0001f) side = Vector3.ProjectOnPlane(upperBone, direction);
            if (side.sqrMagnitude < .0001f) side = Vector3.Cross(direction, Vector3.up);
            if (side.sqrMagnitude < .0001f) side = Vector3.Cross(direction, Vector3.right);
            Vector3 elbow = shoulder + direction * along + side.normalized * Mathf.Sqrt(Mathf.Max(0f, a * a - along * along));
            upper.rotation = Quaternion.Slerp(upper.rotation, Quaternion.FromToRotation(upperBone, elbow - shoulder) * upper.rotation, weight);
            Vector3 toPalm = palm.position - lower.position, toTarget = target - lower.position;
            if (toPalm.sqrMagnitude < .000001f || toTarget.sqrMagnitude < .000001f) return;
            lower.rotation = Quaternion.Slerp(lower.rotation, Quaternion.FromToRotation(toPalm, toTarget) * lower.rotation, weight);
        }

        // Resolver hasta la muñeca descontando la palma ya orientada evita mover el agarre al girar la mano.
        public static void SolveHand(Transform upper, Transform lower, Transform palm, Vector3 target,
            Quaternion wristRotation, Vector3 bend, float weight)
        {
            if (palm == null || palm.parent == null) return;
            Transform wrist = palm.parent;
            Vector3 offset = Quaternion.Inverse(wrist.rotation) * (palm.position - wrist.position);
            Quaternion before = wrist.rotation;
            Solve(upper, lower, wrist, target - wristRotation * offset, bend, weight);
            wrist.rotation = Quaternion.Slerp(before, wristRotation, weight);
        }
    }
}
