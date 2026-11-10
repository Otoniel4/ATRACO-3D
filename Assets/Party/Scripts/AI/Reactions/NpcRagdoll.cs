using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Caída con física (ragdoll): al recibir un disparo o el táser, el Animator se apaga y cada parte del cuerpo cae con
    // su peso y sus articulaciones, empujada desde donde vino el golpe. Al levantarse, el cuerpo se acomoda boca arriba o
    // boca abajo, vuelve el Animator con el clip de levantarse y la pose pasa de la caída al clip sin saltos.
    // Las partes las arma el editor sobre la pose de reposo (Build), así las articulaciones nacen con el cuerpo de pie.
    [DefaultExecutionOrder(200)] // después del Animator y del resto: la mezcla al levantarse tiene la última palabra
    public sealed class NpcRagdoll : MonoBehaviour
    {
        private const float BlendSeconds = .45f;
        [SerializeField] private Animator animator;
        [SerializeField, Tooltip("Cápsula del cuerpo de pie: se apaga mientras está en el suelo.")] private Collider standing;
        [SerializeField] private Rigidbody[] bodies = Array.Empty<Rigidbody>();
        [SerializeField] private Transform pelvis, head, chest;
        [SerializeField, Tooltip("Frente del cuerpo en ejes del pecho (para saber si cayó boca arriba).")] private Vector3 chestFront = Vector3.forward;
        private Transform[] bones = Array.Empty<Transform>();
        private Vector3[] fromPosition = Array.Empty<Vector3>();
        private Quaternion[] fromRotation = Array.Empty<Quaternion>();
        private bool[] moves = Array.Empty<bool>();
        private float blend = -1f;

        public bool Fallen { get; private set; }

        private void Awake()
        {
            bones = animator != null ? animator.GetComponentsInChildren<Transform>(true) : Array.Empty<Transform>();
            moves = bones.Select(b => b.name == "Body" || b.name == "Foot.L" || b.name == "Foot.R").ToArray();
            fromPosition = new Vector3[bones.Length];
            fromRotation = new Quaternion[bones.Length];
        }

        // Cae empujado por «impulse» en «point» (si el golpe vino de lejos, casi no empuja).
        public void Fall(Vector3 impulse, Vector3 point)
        {
            if (animator == null || bodies.Length == 0) return;
            blend = -1f;
            animator.enabled = false;
            if (standing != null) standing.enabled = false;
            foreach (var body in bodies)
            {
                body.isKinematic = false;
                body.interpolation = RigidbodyInterpolation.Interpolate;
                body.GetComponent<Collider>().enabled = true;
            }
            var hit = bodies.OrderBy(b => (b.worldCenterOfMass - point).sqrMagnitude).First();
            hit.AddForceAtPosition(impulse, point, ForceMode.Impulse);
            Fallen = true;
        }

        // Se acomoda para levantarse: true si quedó boca arriba (elige el clip). La raíz va bajo la cadera, mirando hacia
        // donde quedarán sus pies (boca arriba) o su cabeza (boca abajo), como empiezan los clips.
        public bool BeginGetUp()
        {
            for (int i = 0; i < bones.Length; i++) { fromPosition[i] = bones[i].position; fromRotation[i] = bones[i].rotation; }
            bool faceUp = chest.TransformDirection(chestFront).y > 0f;
            foreach (var body in bodies)
            {
                body.isKinematic = true;
                body.interpolation = RigidbodyInterpolation.None;
                body.GetComponent<Collider>().enabled = false;
            }
            Vector3 along = faceUp ? pelvis.position - head.position : head.position - pelvis.position;
            along.y = 0f;
            Vector3 floor = pelvis.position;
            if (Physics.Raycast(floor + Vector3.up, Vector3.down, out var ground, 3f, ~((1 << 29) | (1 << 30) | (1 << 31)), QueryTriggerInteraction.Ignore)) floor = ground.point;
            transform.SetPositionAndRotation(new Vector3(pelvis.position.x, floor.y, pelvis.position.z),
                along.sqrMagnitude > .001f ? Quaternion.LookRotation(along) : transform.rotation);
            blend = 0f;
            Fallen = false;
            return faceUp;
        }

        // Mezcla de la pose caída (guardada en el mundo) a la del clip, de padre a hijo, en BlendSeconds.
        private void LateUpdate()
        {
            if (blend < 0f) return;
            blend += Time.deltaTime / BlendSeconds;
            float t = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(blend));
            for (int i = 0; i < bones.Length; i++)
            {
                if (moves[i]) bones[i].position = Vector3.Lerp(fromPosition[i], bones[i].position, t);
                bones[i].rotation = Quaternion.Slerp(fromRotation[i], bones[i].rotation, t);
            }
            if (blend < 1f) return;
            blend = -1f;
            if (standing != null) standing.enabled = true;
        }

        // Lo llama el editor sobre la pose de reposo: una parte con peso, forma y articulación por zona del cuerpo
        // (pelvis, abdomen, pecho, cabeza, brazos, antebrazos, muslos, piernas y pies), todas quietas hasta caer.
        public void Build(Animator body, Collider capsule)
        {
            animator = body; standing = capsule;
            Transform Bone(string name) => body.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name)
                                           ?? throw new InvalidOperationException("Falta el hueso " + name + " en " + body.name);
            Vector3 right = body.transform.right;
            var parts = new List<Rigidbody>();
            Rigidbody Part(string bone, string tip, float radius, float mass, Rigidbody parent, Vector2 twist, float swing, Vector3 twistAxis)
            {
                var t = Bone(bone);
                var rigid = t.gameObject.AddComponent<Rigidbody>();
                rigid.mass = mass; rigid.isKinematic = true; rigid.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
                float scale = Mathf.Max(.0001f, t.lossyScale.x);
                if (tip == null)
                {
                    var ball = t.gameObject.AddComponent<SphereCollider>();
                    ball.radius = radius / scale; ball.center = t.InverseTransformDirection(Vector3.up) * (radius * .6f / scale); ball.enabled = false;
                }
                else
                {
                    Vector3 end = t.InverseTransformPoint(Bone(tip).position);
                    int axis = Mathf.Abs(end.x) > Mathf.Abs(end.y) ? (Mathf.Abs(end.x) > Mathf.Abs(end.z) ? 0 : 2) : (Mathf.Abs(end.y) > Mathf.Abs(end.z) ? 1 : 2);
                    var shape = t.gameObject.AddComponent<CapsuleCollider>();
                    shape.direction = axis; shape.center = end * .5f; shape.radius = radius / scale;
                    shape.height = Mathf.Abs(end[axis]) + 2f * radius / scale; shape.enabled = false;
                }
                if (parent != null)
                {
                    var joint = t.gameObject.AddComponent<CharacterJoint>();
                    joint.connectedBody = parent; joint.enableProjection = true;
                    joint.axis = t.InverseTransformDirection(twistAxis).normalized;
                    joint.swingAxis = t.InverseTransformDirection(Vector3.Cross(twistAxis, Vector3.up).sqrMagnitude > .01f ? Vector3.up : Vector3.forward).normalized;
                    joint.lowTwistLimit = new SoftJointLimit { limit = twist.x };
                    joint.highTwistLimit = new SoftJointLimit { limit = twist.y };
                    joint.swing1Limit = new SoftJointLimit { limit = swing };
                    joint.swing2Limit = new SoftJointLimit { limit = swing };
                }
                parts.Add(rigid);
                return rigid;
            }
            // Rodillas: doblar es girar positivo sobre el eje derecho del cuerpo; codos, negativo (regla de la mano izquierda).
            var hips = Part("Body", "Abdomen", .14f, 10f, null, Vector2.zero, 0f, right);
            var belly = Part("Abdomen", "Chest", .13f, 8f, hips, new Vector2(-20f, 20f), 15f, right);
            var torso = Part("Chest", "Neck", .15f, 10f, belly, new Vector2(-20f, 20f), 15f, right);
            Part("Head", null, .11f, 4f, torso, new Vector2(-35f, 35f), 30f, right);
            foreach (string side in new[] { "L", "R" })
            {
                var arm = Part("UpperArm." + side, "LowerArm." + side, .05f, 2f, torso, new Vector2(-60f, 60f), 75f, right);
                Part("LowerArm." + side, "Wrist." + side, .045f, 1.5f, arm, new Vector2(-130f, 5f), 10f, right);
                var thigh = Part("UpperLeg." + side, "LowerLeg." + side, .075f, 6f, hips, new Vector2(-40f, 90f), 35f, right);
                var shin = Part("LowerLeg." + side, "Foot." + side, .06f, 4f, thigh, new Vector2(-5f, 130f), 5f, right);
                Part("Foot." + side, null, .06f, 1f, shin, new Vector2(-30f, 30f), 20f, right);
            }
            bodies = parts.ToArray();
            pelvis = Bone("Body"); head = Bone("Head"); chest = Bone("Chest");
            chestFront = chest.InverseTransformDirection(body.transform.forward);
        }
    }
}
