using System.Collections.Generic;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Cierra los dedos sobre lo que sujeta la mano: conserva la pose del Animator y la devuelve antes del fotograma
    // siguiente. Con una pose (HandPose.Angles) cada articulación va a su ángulo; sin pose usa un cierre parejo.
    internal sealed class CommerceFingerPose
    {
        private const int JointsPerFinger = 3;
        // Grados por segundo con que los dedos pasan de una pose a otra.
        private const float Speed = 320f;
        private static readonly string[] Names = { "Thumb", "Index", "Middle", "Ring", "Pinky" };
        // slot = dedo × 3 + articulación: el lugar de su ángulo dentro de la pose.
        private readonly List<(Transform bone, Vector3 axis, float fallback, int slot)> joints = new List<(Transform, Vector3, float, int)>();
        private readonly List<Quaternion> saved = new List<Quaternion>();
        private readonly List<float> current = new List<float>();

        public CommerceFingerPose(Transform wrist, bool left = false)
        {
            var bones = wrist.GetComponentsInChildren<Transform>(true);
            Transform Find(string name) => System.Array.Find(bones, bone => bone.name == name + (left ? ".L" : ".R"));
            var middle = Find("Middle2"); var index = Find("Index2"); var pinky = Find("Pinky2");
            if (middle == null || index == null || pinky == null) return;
            // Hacia donde mira la palma. El orden del producto importa: con los operandos al revés apunta al dorso y los
            // dedos se cerraban hacia atrás.
            Vector3 normal = Vector3.Cross(middle.position - wrist.position, index.position - pinky.position).normalized;
            if (left) normal = -normal;
            for (int finger = 0; finger < Names.Length; finger++)
            {
                bool thumb = finger == 0;
                // El pulgar se dobla desde su base (1 a 3); los demás desde el nudillo (2 a 4).
                int first = thumb ? 1 : 2;
                for (int joint = 0; joint < JointsPerFinger; joint++)
                {
                    var bone = Find(Names[finger] + (first + joint)); var next = Find(Names[finger] + (first + joint + 1));
                    if (bone == null) continue;
                    Vector3 direction = next != null ? next.position - bone.position : bone.position - bone.parent.position;
                    Vector3 inward = thumb ? middle.position - bone.position : normal;
                    // Sin pose: cierre parejo de las dos primeras articulaciones del dedo y de las dos últimas del pulgar.
                    float fallback = thumb ? (joint == 0 ? 0f : 16f) : (joint == 2 ? 0f : 22f);
                    joints.Add((bone, bone.InverseTransformDirection(Vector3.Cross(direction, inward).normalized), fallback, finger * JointsPerFinger + joint));
                    current.Add(0f);
                }
            }
        }

        public void Apply(float weight, float curl = 1f, float[] pose = null)
        {
            saved.Clear();
            for (int i = 0; i < joints.Count; i++)
            {
                var joint = joints[i];
                float wanted = pose != null && joint.slot < pose.Length ? pose[joint.slot] : joint.fallback * curl;
                current[i] = Mathf.MoveTowards(current[i], wanted, Speed * Time.deltaTime);
                saved.Add(joint.bone.localRotation);
                joint.bone.localRotation *= Quaternion.AngleAxis(current[i] * weight, joint.axis);
            }
        }

        public void Restore()
        {
            for (int i = 0; i < saved.Count; i++) joints[i].bone.localRotation = saved[i];
            saved.Clear();
        }
    }
}
