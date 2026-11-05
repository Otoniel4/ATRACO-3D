using System;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // La hoja gira sobre su bisagra y conserva la colisión durante todo el recorrido.
    [DefaultExecutionOrder(-120)]
    public sealed class ShopDoor : MonoBehaviour
    {
        private const float OpenAngle = 85f;
        private const float HoldSeconds = 1.1f;
        private const float ReachDistance = 1.6f;
        private const int ActorMask = (1 << 29) | (1 << 30);
        private const int SolidMask = ~(1 << 31);
        [SerializeField] private Transform left, right, threshold, handle;
        private Quaternion leftClosed, rightClosed;
        private BoxCollider leftBox, rightBox;
        private Transform leftFront, leftBack, rightFront, rightBack;
        private float until, angle, angularVelocity;
        private float leftSign = -1f, rightSign = 1f;
        private bool previewSaved;
        private readonly Collider[] overlaps = new Collider[32];

        public bool HasCollision => left != null && left.GetComponent<Collider>() != null
            && (right == null || right.GetComponent<Collider>() != null);
        public Transform Gateway => threshold;
        public Transform Handle => handle;
        public bool IsOpen => CanPass;
        public bool CanPass => angle >= (right == null ? 82f : 70f);

        public void Configure(Transform leftLeaf, Transform rightLeaf, Transform gateway)
        {
            left = leftLeaf;
            right = rightLeaf;
            threshold = gateway;
            RememberClosed();
            PrepareContacts();
        }

        public bool InReach(Vector3 position) => threshold != null
            && Mathf.Abs(position.y - threshold.position.y) < .65f
            && Flat(position - threshold.position).sqrMagnitude < ReachDistance * ReachDistance;

        public void Push() => until = Time.time + HoldSeconds;

        public void PushFrom(Vector3 actor)
        {
            if (!InReach(actor)) return;
            if (angle < 1f && Time.time >= until)
            {
                leftSign = OpeningSign(left, leftBox, leftClosed, actor);
                rightSign = OpeningSign(right, rightBox, rightClosed, actor);
            }
            Push();
        }

        // El punto de contacto es hijo de la hoja y se desplaza con ella.
        public bool TryGetPushContact(Vector3 actor, float actorRadius, out Transform contact, out Vector3 stand, out Vector3 towardDoor)
        {
            contact = null;
            stand = actor;
            towardDoor = Vector3.zero;
            if (!InReach(actor) || left == null) return false;
            if (leftFront == null) PrepareContacts();
            if (leftFront == null) return false;

            Vector3 normal = ClosedNormal(left, leftBox, leftClosed);
            bool front = Vector3.Dot(actor - threshold.position, normal) >= 0f;
            Vector3 outward = front ? normal : -normal;
            Vector3 tangent = Vector3.Cross(Vector3.up, outward).normalized;
            var leftPoint = front ? leftFront : leftBack;
            var rightPoint = front ? rightFront : rightBack;
            Vector3 shoulder = actor - tangent * .22f;
            contact = rightPoint != null && Flat(rightPoint.position - shoulder).sqrMagnitude < Flat(leftPoint.position - shoulder).sqrMagnitude
                ? rightPoint : leftPoint;
            float sideSpace = Mathf.Max(0f, OpeningWidth() * .5f - actorRadius - .08f);
            float lateral = Vector3.Dot(contact.position - threshold.position, tangent) + .22f;
            stand = threshold.position + outward * Mathf.Max(.40f, actorRadius + .13f)
                + tangent * Mathf.Clamp(lateral, -sideSpace, sideSpace);
            stand.y = actor.y;
            towardDoor = -outward;
            handle = contact;
            return true;
        }

        public void PreviewOpen(bool open)
        {
            if (!previewSaved) { RememberClosed(); previewSaved = true; }
            angle = open ? OpenAngle : 0;
            ApplyPose(angle);
        }

        private void Awake()
        {
            RememberClosed();
            PrepareContacts();
        }

        private void RememberClosed()
        {
            if (left != null) { leftClosed = left.localRotation; leftBox = left.GetComponent<BoxCollider>(); }
            if (right != null) { rightClosed = right.localRotation; rightBox = right.GetComponent<BoxCollider>(); }
        }

        private void PrepareContacts()
        {
            Physics.SyncTransforms();
            Vector3 normal = ClosedNormal(left, leftBox, leftClosed);
            CreateContacts(left, leftBox, "PushContact_L", normal, out leftFront, out leftBack);
            CreateContacts(right, rightBox, "PushContact_R", normal, out rightFront, out rightBack);
            handle = leftFront;
        }

        private void CreateContacts(Transform leaf, BoxCollider box, string marker, Vector3 normal, out Transform front, out Transform back)
        {
            front = back = null;
            if (leaf == null || box == null) return;
            Vector3 center = box.bounds.center;
            Vector3 p = right == null ? center : leaf.position + Flat(center - leaf.position) * 1.55f;
            p.y = threshold != null ? threshold.position.y + 1.15f : center.y;
            foreach (var t in leaf.GetComponentsInChildren<Transform>(true))
                if (t.name == marker || t.name.StartsWith(marker + ".", StringComparison.Ordinal))
                {
                    p = t.position;
                    break;
                }
            // Cada cara conserva su ancla. Otro actor no puede desplazar la que ya está usando una mano.
            front = PlaceContact(leaf, "DoorPalmFront", box.ClosestPoint(p + normal * .17f));
            back = PlaceContact(leaf, "DoorPalmBack", box.ClosestPoint(p - normal * .17f));
        }

        private static Transform PlaceContact(Transform leaf, string name, Vector3 point)
        {
            var contact = leaf.Find(name);
            if (contact == null)
            {
                contact = new GameObject(name).transform;
                contact.SetParent(leaf, false);
            }
            contact.position = point;
            return contact;
        }

        private void Update()
        {
            if (left == null || threshold == null) return;
            bool requested = Time.time < until;
            if (!requested && angle <= .001f) return;
            Physics.SyncTransforms();
            bool hold = requested || (angle > 1f && Occupied());
            float target = hold ? OpenAngle : 0f;
            float velocity = angularVelocity;
            float proposed = Mathf.SmoothDampAngle(angle, target, ref velocity,
                hold ? .19f : .45f, hold ? 160f : 90f, Time.deltaTime);
            if (Mathf.Abs(proposed - target) < .03f) proposed = target;
            float difference = Mathf.Abs(proposed - angle);
            if (difference < .001f) return;

            // Un grado por muestra cubre el arco de la hoja, incluidos los cambios de fotograma grandes.
            int samples = Mathf.CeilToInt(difference);
            for (int i = 1; i <= samples; i++)
                if (!PoseClear(Mathf.Lerp(angle, proposed, (float)i / samples)))
                {
                    angularVelocity = 0;
                    if (!hold) until = Mathf.Max(until, Time.time + .25f);
                    return;
                }
            angle = proposed;
            angularVelocity = velocity;
            ApplyPose(angle);
        }

        private bool Occupied()
        {
            Quaternion orientation = Quaternion.LookRotation(ClosedNormal(left, leftBox, leftClosed));
            int count = Physics.OverlapBoxNonAlloc(threshold.position + Vector3.up * .95f,
                new Vector3(OpeningWidth() * .5f + .15f, 1.0f, .62f), overlaps, orientation, ActorMask, QueryTriggerInteraction.Ignore);
            ClearOverlaps(count);
            return count > 0;
        }

        private bool PoseClear(float value) => LeafClear(left, leftBox, leftClosed, leftSign * value)
            && LeafClear(right, rightBox, rightClosed, rightSign * value);

        private bool LeafClear(Transform leaf, BoxCollider box, Quaternion closed, float angleValue)
        {
            if (leaf == null || box == null) return true;
            Quaternion local = Quaternion.AngleAxis(angleValue, ParentUp(leaf)) * closed;
            Quaternion world = leaf.parent != null ? leaf.parent.rotation * local : local;
            Vector3 scale = leaf.lossyScale;
            Vector3 center = leaf.position + world * Vector3.Scale(box.center, scale);
            Vector3 half = Vector3.Scale(box.size, new Vector3(Mathf.Abs(scale.x), Mathf.Abs(scale.y), Mathf.Abs(scale.z))) * .5f;
            half = new Vector3(Mathf.Max(.008f, half.x - .012f), Mathf.Max(.008f, half.y - .012f), Mathf.Max(.008f, half.z - .012f));
            int count = Physics.OverlapBoxNonAlloc(center, half, overlaps, world, SolidMask, QueryTriggerInteraction.Ignore);
            bool clear = count < overlaps.Length;
            for (int i = 0; i < count; i++)
            {
                Collider c = overlaps[i];
                if (c != null && !c.transform.IsChildOf(left) && !(right != null && c.transform.IsChildOf(right))) clear = false;
            }
            ClearOverlaps(count);
            return clear;
        }

        private void ClearOverlaps(int count)
        {
            for (int i = 0; i < count; i++) overlaps[i] = null;
        }

        private void ApplyPose(float value)
        {
            if (left != null) left.localRotation = Quaternion.AngleAxis(leftSign * value, ParentUp(left)) * leftClosed;
            if (right != null) right.localRotation = Quaternion.AngleAxis(rightSign * value, ParentUp(right)) * rightClosed;
            Physics.SyncTransforms();
        }

        private float OpeningWidth() => right != null ? Flat(right.position - left.position).magnitude
            : leftBox != null ? Flat(leftBox.bounds.center - left.position).magnitude * 2f : 1.2f;

        private static float OpeningSign(Transform leaf, BoxCollider box, Quaternion closed, Vector3 actor)
        {
            if (leaf == null || box == null) return 1f;
            return Vector3.Dot(ClosedNormal(leaf, box, closed), actor - leaf.position) >= 0f ? -1f : 1f;
        }

        private static Vector3 ClosedNormal(Transform leaf, BoxCollider box, Quaternion closed)
        {
            if (leaf == null || box == null) return Vector3.forward;
            Quaternion parent = leaf.parent != null ? leaf.parent.rotation : Quaternion.identity;
            Vector3 radial = parent * closed * Vector3.Scale(box.center, leaf.lossyScale);
            Vector3 normal = Vector3.Cross(Vector3.up, Flat(radial)).normalized;
            return normal.sqrMagnitude > .1f ? normal : Vector3.forward;
        }

        private static Vector3 Flat(Vector3 value) { value.y = 0f; return value; }
        private static Vector3 ParentUp(Transform leaf) => leaf.parent != null
            ? leaf.parent.InverseTransformDirection(Vector3.up).normalized : Vector3.up;
    }
}
