using UnityEngine;

namespace Alarma.City.Playtest
{
    // Hoja corrediza: una persiana que sube o un portón que se corre de lado.
    public sealed class ReviewSlidingDoor : MonoBehaviour
    {
        private const float Lift = 3.2f, HoldSeconds = 3.5f, ReachDistance = 2.2f;
        [SerializeField] private Transform leaf, threshold;
        [SerializeField] private Vector3 travel = Vector3.up * Lift; // Espacio del padre de la hoja.
        [SerializeField] private bool rollsIntoHousing;
        private BoxCollider box;
        private Vector3 closed, closedBoxCenter, closedBoxSize;
        private MeshRenderer[] slats;
        private float[] slatBottoms;
        private float until, amount, velocity;
        private readonly Collider[] overlaps = new Collider[24];
        public bool IsOpen => amount > .05f;
        public Transform Gateway => threshold;

        public void Configure(Transform panel, Transform gateway) => Configure(panel, gateway, Vector3.up * Lift);
        public void Configure(Transform panel, Transform gateway, Vector3 localTravel, bool rollUp = false)
        {
            leaf = panel;
            threshold = gateway;
            travel = localTravel;
            rollsIntoHousing = rollUp;
            RememberClosed();
        }

        private void Awake() => RememberClosed();
        private void RememberClosed()
        {
            if (leaf == null) return;
            closed = leaf.localPosition;
            box = leaf.GetComponent<BoxCollider>();
            if (box != null) { closedBoxCenter = box.center; closedBoxSize = box.size; }
            if (!rollsIntoHousing) return;
            slats = leaf.GetComponentsInChildren<MeshRenderer>(true);
            slatBottoms = new float[slats.Length];
            for (int i = 0; i < slats.Length; i++) slatBottoms[i] = slats[i].bounds.min.y - leaf.position.y;
        }
        public bool InReach(Vector3 position) => threshold != null
            && Mathf.Abs(position.y - threshold.position.y) < .65f
            && Flat(position - threshold.position).sqrMagnitude < ReachDistance * ReachDistance;
        public void Push() => until = Time.time + HoldSeconds;

        public void KeepClearFor(Vector3 position)
        {
            if (threshold == null || leaf == null) return;
            Vector3 tangent = Flat(WorldVector(travel)).normalized;
            if (tangent.sqrMagnitude < .01f) tangent = Flat(leaf.right).normalized;
            Vector3 normal = Vector3.Cross(Vector3.up, tangent);
            Vector3 relative = Flat(position - threshold.position);
            float halfWidth = box != null && box.enabled ? Mathf.Max(box.bounds.extents.x, box.bounds.extents.z) : 1.8f;
            if (Mathf.Abs(Vector3.Dot(relative, normal)) < .68f
                && Mathf.Abs(Vector3.Dot(relative, tangent)) < halfWidth + .24f)
                until = Mathf.Max(until, Time.time + .45f);
        }

        private void Update()
        {
            if (leaf == null || Time.time >= until && amount <= .001f) return;
            // El FBX puede usar escala en el padre: la velocidad se mide en metros del mundo.
            float length = WorldVector(travel).magnitude;
            if (length <= .001f) return;
            bool opening = Time.time < until;
            float target = opening ? length : 0f;
            float nextVelocity = velocity;
            float next = Mathf.SmoothDamp(amount, target, ref nextVelocity, opening ? .24f : .42f,
                opening ? 2.5f : 1.65f, Time.deltaTime);
            if (Mathf.Abs(next - target) < .005f) next = target;
            if (Mathf.Abs(next - amount) <= .001f) return;
            Vector3 local = closed + travel * (next / length);
            Vector3 delta = WorldVector(local - leaf.localPosition);
            Physics.SyncTransforms();
            if (!ClearTravel(delta, next, length))
            {
                velocity = 0f;
                if (!opening) until = Mathf.Max(until, Time.time + .5f);
                return;
            }
            amount = next;
            velocity = nextVelocity;
            leaf.localPosition = local;
            if (rollsIntoHousing)
            {
                if (box != null)
                {
                    DoorBox(amount, out Vector3 center, out Vector3 size);
                    box.enabled = amount < length - .01f;
                    box.center = center;
                    box.size = size;
                }
                for (int i = 0; i < slats.Length; i++) slats[i].enabled = slatBottoms[i] + amount < length;
            }
            Physics.SyncTransforms();
        }

        private bool ClearTravel(Vector3 delta, float next, float length)
        {
            if (box == null) return true;
            Vector3 scale = leaf.lossyScale;
            scale = Absolute(scale);
            int steps = Mathf.Max(1, Mathf.CeilToInt(delta.magnitude / .025f));
            for (int i = 1; i <= steps; i++)
            {
                float fraction = i / (float)steps;
                float lift = Mathf.Lerp(amount, next, fraction);
                if (rollsIntoHousing && lift >= length - .01f) continue;
                DoorBox(lift, out Vector3 center, out Vector3 size);
                Vector3 half = Vector3.Scale(size, scale) * .5f;
                half = new Vector3(Mathf.Max(.008f, half.x - .012f), Mathf.Max(.008f, half.y - .012f), Mathf.Max(.008f, half.z - .012f));
                int count = Physics.OverlapBoxNonAlloc(leaf.TransformPoint(center) + delta * fraction, half, overlaps,
                    leaf.rotation, ~(1 << 31), QueryTriggerInteraction.Ignore);
                bool clear = count < overlaps.Length;
                for (int hit = 0; hit < count; hit++)
                {
                    if (overlaps[hit] != null && !overlaps[hit].transform.IsChildOf(leaf)) clear = false;
                    overlaps[hit] = null;
                }
                if (!clear) return false;
            }
            return true;
        }

        private void DoorBox(float lift, out Vector3 center, out Vector3 size)
        {
            Vector3 cut = rollsIntoHousing ? leaf.InverseTransformVector(Vector3.up * lift) : Vector3.zero;
            center = closedBoxCenter - cut * .5f;
            size = Vector3.Max(closedBoxSize - Absolute(cut), closedBoxSize * .001f);
        }

        private static Vector3 Absolute(Vector3 v) => new Vector3(Mathf.Abs(v.x), Mathf.Abs(v.y), Mathf.Abs(v.z));
        private Vector3 WorldVector(Vector3 vector) => leaf.parent != null ? leaf.parent.TransformVector(vector) : vector;
        private static Vector3 Flat(Vector3 value) { value.y = 0f; return value; }
    }
}
