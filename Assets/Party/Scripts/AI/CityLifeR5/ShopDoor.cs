using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Puerta de dos hojas que solo se abre cuando alguien la empuja: el jugador con E y el NPC con la mano al llegar.
    // Se cierra sola cuando nadie la sostiene.
    public sealed class ShopDoor : MonoBehaviour
    {
        private const float OpenAngle = 85f, Speed = 180f, HoldSeconds = 2.5f, ReachDistance = 2.2f;
        [SerializeField] private Transform left, right, threshold, handle;
        private Quaternion leftClosed, rightClosed;
        private float until, angle;
        private bool previewSaved;
        public bool HasCollision => left != null && right != null && left.GetComponent<Collider>() != null && right.GetComponent<Collider>() != null;
        public Transform Gateway => threshold;
        public Transform Handle => handle;
        public bool IsOpen => angle > 1f;

        public void Configure(Transform leftLeaf, Transform rightLeaf, Transform gateway)
        {
            left = leftLeaf; right = rightLeaf; threshold = gateway;
            // Altura de la manija: donde el NPC apoya la mano al empujar.
            handle = new GameObject("Manija").transform;
            handle.SetParent(threshold, false);
            handle.localPosition = Vector3.up * 1.05f;
            RememberClosed();
        }

        public bool InReach(Vector3 position)
        {
            if (threshold == null) return false;
            Vector3 difference = position - threshold.position;
            difference.y = 0;
            return difference.sqrMagnitude < ReachDistance * ReachDistance;
        }

        // Abre la puerta o la mantiene abierta mientras alguien sigue en el umbral.
        public void Push() => until = Time.time + HoldSeconds;

        public void PreviewOpen(bool open) { if (!previewSaved) { RememberClosed(); previewSaved = true; } angle = open ? OpenAngle : 0; ApplyPose(); }
        private void Awake() => RememberClosed();
        private void RememberClosed() { if (left != null) leftClosed = left.localRotation; if (right != null) rightClosed = right.localRotation; }

        private void Update()
        {
            angle = Mathf.MoveTowards(angle, Time.time < until ? OpenAngle : 0f, Speed * Time.deltaTime);
            ApplyPose();
        }

        private void ApplyPose()
        {
            if (left != null) left.localRotation = Quaternion.AngleAxis(-angle, ParentUp(left)) * leftClosed;
            if (right != null) right.localRotation = Quaternion.AngleAxis(angle, ParentUp(right)) * rightClosed;
        }

        private static Vector3 ParentUp(Transform leaf) => leaf.parent != null ? leaf.parent.InverseTransformDirection(Vector3.up).normalized : Vector3.up;
    }
}
