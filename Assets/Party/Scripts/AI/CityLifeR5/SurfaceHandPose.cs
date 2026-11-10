using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Calibra la palma anatómica para apoyar una mano abierta sobre una superficie.
    // El marcador de bolsa se conserva: pertenece a las interacciones de compra.
    internal sealed class SurfaceHandPose
    {
        public Transform Wrist { get; }
        private readonly Vector3 offset;
        private readonly Quaternion frame;
        public Vector3 Position => Wrist.position + Wrist.rotation * offset;

        public SurfaceHandPose(Transform wrist, Transform fallback)
        {
            Wrist = wrist;
            Transform Find(string name)
            {
                foreach (var bone in wrist.GetComponentsInChildren<Transform>(true))
                    if (bone.name == name + ".R") return bone;
                return null;
            }
            var middle = Find("Middle2");
            var index = Find("Index2");
            var pinky = Find("Pinky2");
            Vector3 fingers = middle != null ? middle.position - wrist.position : fallback.position - wrist.position;
            if (fingers.sqrMagnitude < .000001f) fingers = wrist.forward;
            Vector3 across = index != null && pinky != null ? index.position - pinky.position : wrist.right;
            Vector3 normal = Vector3.Cross(across, fingers).normalized;
            if (normal.sqrMagnitude < .000001f) normal = wrist.up;
            Vector3 palm = middle != null ? middle.position - fingers.normalized * .025f + normal * .015f : fallback.position;
            offset = Quaternion.Inverse(wrist.rotation) * (palm - wrist.position);
            frame = Quaternion.Inverse(wrist.rotation) * Quaternion.LookRotation(fingers, normal);
        }

        public Quaternion Rotation(Vector3 outward)
            => Quaternion.LookRotation(Vector3.up, -outward) * Quaternion.Inverse(frame);
        public Quaternion HoldingRotation(Vector3 forward)
            => Quaternion.LookRotation(forward, Vector3.up) * Quaternion.Inverse(frame);
        public Quaternion GraspRotation(Vector3 forward)
            => Quaternion.LookRotation(forward, Vector3.down) * Quaternion.Inverse(frame);
        public Vector3 WristTarget(Vector3 point, Quaternion rotation) => point - rotation * offset;
    }
}
