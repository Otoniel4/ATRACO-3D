using System;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // El marcador Grip_R6 está en la palma. Los dos segmentos conservan su longitud.
    [DefaultExecutionOrder(100)]
    public sealed class PedestrianReach : MonoBehaviour
    {
        [SerializeField] private Transform upper, lower, grip, spine;
        private Transform target;
        private float until, weight;
        private bool surface;
        private float palmError = float.PositiveInfinity;
        // Abdomen y brazos recuperan la pose original antes de que el Animator escriba el fotograma siguiente.
        private Quaternion spinePose, upperPose, lowerPose;
        private bool adjusted;
        public bool HasContact => weight > .85f && palmError <= .035f;

        public void Configure(Transform hand)
        {
            grip = hand;
            upper = Bone(HumanBodyBones.RightUpperArm);
            lower = Bone(HumanBodyBones.RightLowerArm);
            spine = Bone(HumanBodyBones.Spine);
        }

        private Transform Bone(HumanBodyBones bone) => RigBones.Find(transform, bone)
            ?? throw new InvalidOperationException("Falta el hueso " + bone + " en " + name);

        public void Reach(Transform point, float seconds = .1f) => SetTarget(point, seconds, false);
        public void ReachSurface(Transform point) => SetTarget(point, .18f, true);
        public void Release(Transform point)
        {
            if (target == point) until = 0;
        }

        public bool CanReach(Vector3 point, float tolerance = .04f)
        {
            if (upper == null || lower == null || grip == null) return false;
            float length = Vector3.Distance(upper.position, lower.position) + Vector3.Distance(lower.position, grip.position);
            return Vector3.Distance(upper.position, point) <= length + tolerance;
        }

        private void SetTarget(Transform point, float seconds, bool doorSurface)
        {
            if (target != point) palmError = float.PositiveInfinity;
            target = point;
            surface = doorSurface;
            until = Time.time + seconds;
        }

        private void Update() => RestorePose();

        private void OnDisable()
        {
            RestorePose();
            target = null;
            weight = 0;
            palmError = float.PositiveInfinity;
        }

        private void RestorePose()
        {
            if (!adjusted) return;
            spine.localRotation = spinePose;
            upper.localRotation = upperPose;
            lower.localRotation = lowerPose;
            adjusted = false;
        }

        private void LateUpdate()
        {
            if (grip == null || upper == null || lower == null || spine == null || Time.deltaTime <= 0) return;
            bool active = target != null && Time.time <= until;
            weight = Mathf.MoveTowards(weight, active ? 1f : 0f, Time.deltaTime / (active ? .14f : .18f));
            if (target == null || weight <= 0)
            {
                palmError = float.PositiveInfinity;
                return;
            }
            spinePose = spine.localRotation;
            upperPose = upper.localRotation;
            lowerPose = lower.localRotation;
            adjusted = true;

            Vector3 direction = target.position - upper.position;
            direction.y = 0;
            if (direction.sqrMagnitude > .001f)
            {
                float lean = (surface ? 7f : 12f) * weight;
                spine.rotation = Quaternion.AngleAxis(lean, Vector3.Cross(Vector3.up, direction.normalized)) * spine.rotation;
            }
            SolveArm(target.position);
            palmError = Vector3.Distance(grip.position, target.position);
        }

        private void SolveArm(Vector3 point)
        {
            Vector3 shoulder = upper.position;
            Vector3 upperBone = lower.position - shoulder;
            float a = upperBone.magnitude;
            float b = Vector3.Distance(lower.position, grip.position);
            Vector3 reach = point - shoulder;
            if (a < .001f || b < .001f || reach.sqrMagnitude < .000001f) return;
            Vector3 direction = reach.normalized;
            float distance = Mathf.Clamp(reach.magnitude, Mathf.Abs(a - b) + .001f, a + b - .001f);
            float along = (a * a - b * b + distance * distance) / (2f * distance);
            Vector3 bend = Vector3.ProjectOnPlane(upperBone, direction);
            if (bend.sqrMagnitude < .0001f) bend = Vector3.ProjectOnPlane(Vector3.down + transform.right * .45f, direction);
            Vector3 elbow = shoulder + direction * along + bend.normalized * Mathf.Sqrt(Mathf.Max(0, a * a - along * along));

            Quaternion upperGoal = Quaternion.FromToRotation(upperBone, elbow - shoulder) * upper.rotation;
            upper.rotation = Quaternion.Slerp(upper.rotation, upperGoal, weight);
            Vector3 toPalm = grip.position - lower.position;
            Vector3 toPoint = point - lower.position;
            if (toPalm.sqrMagnitude < .000001f || toPoint.sqrMagnitude < .000001f) return;
            Quaternion lowerGoal = Quaternion.FromToRotation(toPalm, toPoint) * lower.rotation;
            lower.rotation = Quaternion.Slerp(lower.rotation, lowerGoal, weight);
        }
    }
}
