using System.Collections.Generic;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Calibra la orientación anatómica de la mano y flexiona sus articulaciones, sin deformar la malla.
    internal sealed class HandGripPose
    {
        private readonly Transform wrist;
        private readonly Quaternion localFrame;
        private readonly List<Joint> joints = new List<Joint>();
        private readonly List<(Transform bone, Quaternion rotation)> saved = new List<(Transform, Quaternion)>();
        private readonly bool right;
        public Transform Palm { get; }
        private struct Joint
        {
            public Transform Bone;
            public Vector3 Axis;
            public Quaternion Rest;
            public float Degrees;
            public bool Index;
        }

        public HandGripPose(Transform palm, bool rightHand)
        {
            right = rightHand;
            wrist = palm.parent;
            string suffix = right ? ".R" : ".L";
            Transform Find(string name)
            {
                foreach (var child in wrist.GetComponentsInChildren<Transform>(true))
                    if (child.name == name + suffix) return child;
                return null;
            }
            var middle = Find("Middle2");
            var index = Find("Index2");
            var pinky = Find("Pinky2");
            Vector3 forward = middle != null ? middle.position - wrist.position : palm.position - wrist.position;
            Vector3 across = index != null && pinky != null ? index.position - pinky.position : wrist.right;
            Vector3 normal = Vector3.Cross(across, forward) * (right ? 1f : -1f);
            if (normal.sqrMagnitude < .000001f) normal = wrist.up;
            normal.Normalize();
            // El marcador antiguo de bolsas está cerca de la muñeca. El agarre de objetos va en la palma distal.
            Palm = new GameObject(right ? "ItemPalm_R" : "ItemPalm_L").transform;
            Palm.SetParent(wrist, false);
            Palm.position = middle != null ? middle.position - forward.normalized * .025f + normal * .015f : palm.position;
            localFrame = Quaternion.Inverse(wrist.rotation) * Quaternion.LookRotation(forward, normal);
            foreach (string finger in new[] { "Index", "Middle", "Ring", "Pinky", "Thumb" })
            {
                bool thumb = finger == "Thumb";
                for (int number = thumb ? 1 : 2; number <= (thumb ? 3 : 4); number++)
                {
                    var bone = Find(finger + number);
                    var next = Find(finger + (number + 1));
                    if (bone == null) continue;
                    Vector3 direction = next != null ? next.position - bone.position : bone.position - bone.parent.position;
                    Vector3 inward = thumb && middle != null ? middle.position - bone.position : normal;
                    Vector3 axis = Vector3.Cross(direction, inward).normalized;
                    joints.Add(new Joint {
                        Bone = bone, Axis = bone.InverseTransformDirection(axis), Rest = bone.localRotation,
                        Degrees = thumb ? (number == 1 ? 18f : 35f) : (number == 2 ? 65f : number == 3 ? 85f : 45f),
                        Index = finger == "Index"
                    });
                }
            }
        }

        public Quaternion WristRotation(Quaternion item, Vector3 fingers, Vector3 normal)
            => item * Quaternion.LookRotation(fingers, normal) * Quaternion.Inverse(localFrame);

        public Quaternion ItemRotation(Vector3 fingers, Vector3 normal)
            => wrist.rotation * localFrame * Quaternion.Inverse(Quaternion.LookRotation(fingers, normal));

        public void Capture(Transform upper, Transform lower)
        {
            saved.Clear();
            foreach (var bone in new[] { upper, lower, wrist })
                if (bone != null) saved.Add((bone, bone.localRotation));
            foreach (var joint in joints) saved.Add((joint.Bone, joint.Bone.localRotation));
        }

        public void Curl(float weight, bool straightIndex)
        {
            foreach (var joint in joints)
            {
                float curl = straightIndex && right && joint.Index ? .08f : 1f;
                Quaternion grip = joint.Rest * Quaternion.AngleAxis(joint.Degrees * curl, joint.Axis);
                joint.Bone.localRotation = Quaternion.Slerp(joint.Bone.localRotation, grip, weight);
            }
        }

        public void Restore()
        {
            foreach (var pose in saved) if (pose.bone != null) pose.bone.localRotation = pose.rotation;
            saved.Clear();
        }

        public void Dispose()
        {
            Restore();
            if (Palm != null) Object.Destroy(Palm.gameObject);
        }
    }
}
