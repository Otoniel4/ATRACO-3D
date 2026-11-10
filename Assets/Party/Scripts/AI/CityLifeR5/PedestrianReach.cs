using System;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Resuelve el alcance sin estirar los huesos; las puertas usan una palma anatómica independiente del agarre de compras.
    [DefaultExecutionOrder(100)]
    public sealed class PedestrianReach : MonoBehaviour
    {
        [SerializeField] private Transform upper, lower, grip, spine;
        private Transform target;
        private float until, weight;
        private bool surface;
        private bool holding;
        private float commerceLean;
        private bool graspFromAbove;
        private Transform freeArm;
        private Quaternion freeArmPose;
        [SerializeField] private Transform purchaseGrip;
        private CommerceFingerPose purchaseFingers;
        public Transform PurchaseGrip => purchaseGrip != null ? purchaseGrip : grip;
        private SurfaceHandPose surfaceHand;
        private Quaternion wristPose;
        private float palmError = float.PositiveInfinity;
        // Abdomen y brazos recuperan la pose original antes de que el Animator escriba el fotograma siguiente.
        private Quaternion spinePose, upperPose, lowerPose;
        private bool adjusted;
        public bool HasContact => weight > .85f && palmError <= (surface ? .008f : .035f);
        public Vector3 PalmPosition => (surface || holding) && surfaceHand != null ? surfaceHand.Position
            : grip != null ? grip.position : transform.position;

        // La distancia lateral sale del rig real, no de un hombro supuesto a 22 cm del centro.
        public Vector3 AlignSurfaceStand(Vector3 contact, Vector3 stand, Vector3 forward)
        {
            if (upper == null) return stand;
            Vector3 side = Vector3.Cross(Vector3.up, forward).normalized;
            float correction = Vector3.Dot(contact - stand - (upper.position - transform.position), side);
            return stand + side * correction;
        }

        public void Configure(Transform hand)
        {
            grip = hand;
            upper = Bone(HumanBodyBones.RightUpperArm);
            lower = Bone(HumanBodyBones.RightLowerArm);
            spine = Bone(HumanBodyBones.Spine);
            foreach (var bone in transform.GetComponentsInChildren<Transform>(true))
                if (bone.name == "UpperArm.L" || bone.name == "LeftUpperArm") { freeArm = bone; break; }
            var wrist = RigBones.Find(transform, HumanBodyBones.RightHand);
            surfaceHand = wrist != null ? new SurfaceHandPose(wrist, grip) : null;
            if (surfaceHand != null)
            {
                if (purchaseGrip == null) purchaseGrip = new GameObject("Palma_Compra").transform;
                purchaseGrip.SetParent(wrist, false);
                purchaseGrip.position = surfaceHand.Position;
                purchaseFingers = new CommerceFingerPose(wrist);
            }
        }

        private Transform Bone(HumanBodyBones bone) => RigBones.Find(transform, bone)
            ?? throw new InvalidOperationException("Falta el hueso " + bone + " en " + name);

        private void Awake() { if (grip != null) Configure(grip); }

        public void Reach(Transform point, float seconds = .1f) => SetTarget(point, seconds, false);
        public void ReachSurface(Transform point) => SetTarget(point, .18f, true);
        public void ReachObject(Transform point, bool fromAbove = false)
        {
            SetTarget(point, .15f, false);
            holding = true;
            graspFromAbove = fromAbove;
        }
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

        // Una palma vertical requiere otra posición de muñeca que el marcador de llevar objetos.
        public bool CanReachSurface(Transform point, float tolerance = .005f)
        {
            if (point == null || upper == null || lower == null) return false;
            if (surfaceHand == null) return CanReach(point.position, tolerance);
            Quaternion rotation = surfaceHand.Rotation(point.forward);
            Vector3 wristTarget = surfaceHand.WristTarget(point.position, rotation);
            float length = Vector3.Distance(upper.position, lower.position)
                + Vector3.Distance(lower.position, surfaceHand.Wrist.position) - .001f;
            return Vector3.Distance(upper.position, wristTarget) <= length + tolerance;
        }

        private void SetTarget(Transform point, float seconds, bool doorSurface)
        {
            if (target != point) palmError = float.PositiveInfinity;
            target = point;
            surface = doorSurface;
            holding = false;
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
            purchaseFingers?.Restore();
            if (!adjusted) return;
            spine.localRotation = spinePose;
            upper.localRotation = upperPose;
            lower.localRotation = lowerPose;
            if (freeArm != null) freeArm.localRotation = freeArmPose;
            if (surfaceHand != null) surfaceHand.Wrist.localRotation = wristPose;
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
            if (freeArm != null) freeArmPose = freeArm.localRotation;
            Quaternion freeWorld = freeArm != null ? freeArm.rotation : Quaternion.identity;
            if (surfaceHand != null) wristPose = surfaceHand.Wrist.localRotation;
            adjusted = true;

            Vector3 direction = target.position - upper.position;
            direction.y = 0;
            if (direction.sqrMagnitude > .001f)
            {
                float desiredLean = 12f;
                if (holding && surfaceHand != null)
                {
                    Vector3 wrist = surfaceHand.WristTarget(target.position, ObjectRotation());
                    float length = Vector3.Distance(upper.position, lower.position)
                        + Vector3.Distance(lower.position, surfaceHand.Wrist.position) - .006f;
                    Vector3 axis = Vector3.Cross(Vector3.up, direction.normalized);
                    // Inclinar solamente lo necesario; nunca alargar los huesos ni mover los pies a través del mueble.
                    float nearest = float.PositiveInfinity;
                    for (float candidate = 12f; candidate <= 60f; candidate += 2f)
                    {
                        Vector3 shoulder = spine.position + Quaternion.AngleAxis(candidate, axis) * (upper.position - spine.position);
                        float distance = Vector3.Distance(shoulder, wrist);
                        if (distance < nearest) { nearest = distance; desiredLean = candidate; }
                        if (distance <= length) break;
                    }
                }
                commerceLean = Mathf.MoveTowards(commerceLean, desiredLean, Time.deltaTime * 75f);
                float lean = (surface ? 10f : holding ? commerceLean : 12f) * weight;
                spine.rotation = Quaternion.AngleAxis(lean, Vector3.Cross(Vector3.up, direction.normalized)) * spine.rotation;
                if (holding && freeArm != null) freeArm.rotation = freeWorld;
            }
            if ((surface || holding) && surfaceHand != null)
            {
                Quaternion before = surfaceHand.Wrist.rotation;
                Quaternion rotation = surface ? surfaceHand.Rotation(target.forward) : ObjectRotation();
                SolveArm(surfaceHand.WristTarget(target.position, rotation), surfaceHand.Wrist);
                surfaceHand.Wrist.rotation = Quaternion.Slerp(before, rotation, weight);
                if (holding) purchaseFingers?.Apply(weight);
            }
            else SolveArm(target.position, grip);
            palmError = Vector3.Distance(PalmPosition, target.position);
        }

        private Quaternion ObjectRotation() => graspFromAbove
            ? surfaceHand.GraspRotation(transform.forward) : surfaceHand.HoldingRotation(transform.forward);

        private void SolveArm(Vector3 point, Transform endpoint)
        {
            Vector3 shoulder = upper.position;
            Vector3 upperBone = lower.position - shoulder;
            float a = upperBone.magnitude;
            float b = Vector3.Distance(lower.position, endpoint.position);
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
            Vector3 toPalm = endpoint.position - lower.position;
            Vector3 toPoint = point - lower.position;
            if (toPalm.sqrMagnitude < .000001f || toPoint.sqrMagnitude < .000001f) return;
            Quaternion lowerGoal = Quaternion.FromToRotation(toPalm, toPoint) * lower.rotation;
            lower.rotation = Quaternion.Slerp(lower.rotation, lowerGoal, weight);
        }
    }
}
