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
        // Giro actual de la mano: Z hacia las puntas de los dedos, Y saliendo de la palma.
        public Quaternion Frame => Wrist.rotation * frame;

        public SurfaceHandPose(Transform wrist, Transform fallback, bool left = false)
        {
            Wrist = wrist;
            Transform Find(string name)
            {
                foreach (var bone in wrist.GetComponentsInChildren<Transform>(true))
                    if (bone.name == name + (left ? ".L" : ".R")) return bone;
                return null;
            }
            var middle = Find("Middle2");
            var index = Find("Index2");
            var pinky = Find("Pinky2");
            Vector3 fingers = middle != null ? middle.position - wrist.position : fallback.position - wrist.position;
            if (fingers.sqrMagnitude < .000001f) fingers = wrist.forward;
            Vector3 across = index != null && pinky != null ? index.position - pinky.position : wrist.right;
            // Hacia donde mira la palma. Unity usa ejes zurdos: Cross(across, fingers), que en Blender da la palma, acá
            // da el dorso. Con el dorso la mano quedaba del otro lado del objeto y el brazo se retorcía para llegar.
            Vector3 normal = Vector3.Cross(fingers, across).normalized;
            if (left) normal = -normal;
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
        public Quaternion ObjectRotation(Vector3 fingers, Vector3 normal)
            => Quaternion.LookRotation(fingers, normal) * Quaternion.Inverse(frame);
        public Vector3 WristTarget(Vector3 point, Quaternion rotation) => point - rotation * offset;
        // Dónde queda la palma con la muñeca en ese punto y ese giro (lo inverso de WristTarget).
        public Vector3 PalmAt(Vector3 wrist, Quaternion rotation) => wrist + rotation * offset;
    }
}
