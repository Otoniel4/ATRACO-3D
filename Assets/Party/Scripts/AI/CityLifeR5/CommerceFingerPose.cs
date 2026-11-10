using System.Collections.Generic;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Flexión suave de apoyo: conserva la pose del Animator y la devuelve antes del fotograma siguiente.
    internal sealed class CommerceFingerPose
    {
        private readonly List<(Transform bone, Vector3 axis, float angle)> joints = new List<(Transform, Vector3, float)>();
        private readonly List<Quaternion> saved = new List<Quaternion>();

        public CommerceFingerPose(Transform wrist)
        {
            var bones = wrist.GetComponentsInChildren<Transform>(true);
            Transform Find(string name) => System.Array.Find(bones, bone => bone.name == name + ".R");
            var middle = Find("Middle2"); var index = Find("Index2"); var pinky = Find("Pinky2");
            if (middle == null || index == null || pinky == null) return;
            Vector3 normal = Vector3.Cross(index.position - pinky.position, middle.position - wrist.position).normalized;
            foreach (string finger in new[] { "Index", "Middle", "Ring", "Pinky", "Thumb" })
                for (int number = 2; number <= 3; number++)
                {
                    var bone = Find(finger + number); var next = Find(finger + (number + 1));
                    if (bone == null) continue;
                    Vector3 direction = next != null ? next.position - bone.position : bone.position - bone.parent.position;
                    Vector3 inward = finger == "Thumb" ? middle.position - bone.position : normal;
                    joints.Add((bone, bone.InverseTransformDirection(Vector3.Cross(direction, inward).normalized), finger == "Thumb" ? 16f : 22f));
                }
        }

        public void Apply(float weight)
        {
            saved.Clear();
            foreach (var joint in joints)
            {
                saved.Add(joint.bone.localRotation);
                joint.bone.localRotation *= Quaternion.AngleAxis(joint.angle * weight, joint.axis);
            }
        }

        public void Restore()
        {
            for (int i = 0; i < saved.Count; i++) joints[i].bone.localRotation = saved[i];
            saved.Clear();
        }
    }
}
