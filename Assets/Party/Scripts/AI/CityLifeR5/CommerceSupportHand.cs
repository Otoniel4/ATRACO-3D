using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Apoyo izquierdo independiente: no escribe la columna ni modifica el alcance de puertas.
    [DefaultExecutionOrder(120)]
    public sealed class CommerceSupportHand : MonoBehaviour
    {
        private Transform upper, lower, wrist;
        private SurfaceHandPose palm;
        private CommerceFingerPose fingers;
        private Vector3 target, direction, normal, velocity, smoothed;
        private Quaternion upperPose, lowerPose, wristPose;
        private float until, weight, curl, doorUntil;
        private bool adjusted, tracking;
        private float[] angles;
        public bool Touches(Vector3 point) => palm != null && weight > .9f && Vector3.Distance(palm.Position, point) <= .025f;

        public void Follow(Vector3 point, Vector3 forward, Vector3 outward, float fingerCurl, float[] fingerAngles = null)
        {
            angles = fingerAngles;
            if (Time.time < doorUntil) return;
            if (palm == null)
            {
                upper = RigBones.Find(transform, HumanBodyBones.LeftUpperArm);
                lower = RigBones.Find(transform, HumanBodyBones.LeftLowerArm);
                wrist = RigBones.Find(transform, HumanBodyBones.LeftHand);
                if (upper == null || lower == null || wrist == null) return;
                palm = new SurfaceHandPose(wrist, wrist, true);
                fingers = new CommerceFingerPose(wrist, true);
            }
            if (!tracking) { smoothed = palm.Position; velocity = Vector3.zero; tracking = true; }
            target = point; direction = forward; normal = outward; curl = fingerCurl; until = Time.time + .08f;
        }

        public void ReachSurface(Transform point)
        {
            doorUntil = 0f;
            Follow(point.position, Vector3.up, -point.forward, 0f);
            doorUntil = Time.time + .08f;
        }

        private void Update() => Restore();
        private void Restore()
        {
            fingers?.Restore();
            if (!adjusted) return;
            upper.localRotation = upperPose; lower.localRotation = lowerPose; wrist.localRotation = wristPose;
            adjusted = false;
        }
        private void OnDisable() { Restore(); weight = 0f; until = 0f; tracking = false; }

        private void LateUpdate()
        {
            if (palm == null || Time.deltaTime <= 0f) return;
            bool active = Time.time < until;
            weight = Mathf.MoveTowards(weight, active ? 1f : 0f, Time.deltaTime / .18f);
            if (weight <= 0f) { tracking = false; return; }
            upperPose = upper.localRotation; lowerPose = lower.localRotation; wristPose = wrist.localRotation; adjusted = true;
            smoothed = Vector3.SmoothDamp(smoothed, target, ref velocity, .10f, 1.2f, Time.deltaTime);
            Quaternion rotation = palm.ObjectRotation(direction, normal);
            Vector3 point = palm.WristTarget(smoothed, rotation);
            Vector3 first = lower.position - upper.position, reach = point - upper.position;
            float a = first.magnitude, b = Vector3.Distance(lower.position, wrist.position);
            if (a < .001f || b < .001f || reach.sqrMagnitude < .000001f) return;
            Vector3 axis = reach.normalized;
            float distance = Mathf.Clamp(reach.magnitude, Mathf.Abs(a - b) + .001f, a + b - .001f);
            float along = (a * a - b * b + distance * distance) / (2f * distance);
            // Codo izquierdo abajo, algo afuera y atrás (igual criterio que el brazo derecho en PedestrianReach).
            Vector3 bend = Vector3.ProjectOnPlane(Vector3.down - transform.right * .45f - transform.forward * .25f, axis);
            if (bend.sqrMagnitude < .0001f) bend = Vector3.ProjectOnPlane(Vector3.down - transform.right * .45f, axis);
            Vector3 elbow = upper.position + axis * along + bend.normalized * Mathf.Sqrt(Mathf.Max(0f, a * a - along * along));
            Quaternion before = wrist.rotation;
            upper.rotation = Quaternion.Slerp(upper.rotation, Quaternion.FromToRotation(first, elbow - upper.position) * upper.rotation, weight);
            lower.rotation = Quaternion.Slerp(lower.rotation, Quaternion.FromToRotation(wrist.position - lower.position, point - lower.position) * lower.rotation, weight);
            wrist.rotation = Quaternion.Slerp(before, rotation, weight);
            fingers.Apply(weight, curl, angles);
        }
    }
}
