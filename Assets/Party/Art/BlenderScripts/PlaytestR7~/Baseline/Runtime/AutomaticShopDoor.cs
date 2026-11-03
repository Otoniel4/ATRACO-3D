using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class AutomaticShopDoor : MonoBehaviour
    {
        [SerializeField] private Transform left, right, threshold;
        private Quaternion leftClosed, rightClosed;
        private float until, angle;
        public void Configure(Transform leftLeaf, Transform rightLeaf, Transform gateway)
        { left = leftLeaf; right = rightLeaf; threshold = gateway; RememberClosed(); }
        private void Awake() => RememberClosed();
        private void RememberClosed() { if (left != null) leftClosed = left.localRotation; if (right != null) rightClosed = right.localRotation; }
        public void RequestNear(Vector3 position)
        {
            if (threshold == null) return;
            Vector3 difference = position - threshold.position; difference.y = 0;
            if (difference.sqrMagnitude < 2.4f * 2.4f) until = Time.time + 1.2f;
        }
        private void Update()
        {
            angle = Mathf.MoveTowards(angle, Time.time < until ? 75f : 0f, 140f * Time.deltaTime);
            if (left != null) left.localRotation = Quaternion.AngleAxis(-angle, ParentUp(left)) * leftClosed;
            if (right != null) right.localRotation = Quaternion.AngleAxis(angle, ParentUp(right)) * rightClosed;
        }
        private static Vector3 ParentUp(Transform leaf) => leaf.parent != null ? leaf.parent.InverseTransformDirection(Vector3.up).normalized : Vector3.up;
    }
}
