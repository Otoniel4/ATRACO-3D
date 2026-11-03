using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class AutomaticShopDoor : MonoBehaviour
    {
        [SerializeField] private Transform left, right, threshold;
        private Quaternion leftClosed, rightClosed;
        private float until, angle;
        public bool HasCollision=>left!=null && right!=null && left.GetComponent<Collider>()!=null && right.GetComponent<Collider>()!=null;
        public Transform Gateway=>threshold;
        public void RequestPassage(){until=Time.time+1.5f;}
        private bool previewSaved;
        public void PreviewOpen(bool open){if(!previewSaved){RememberClosed();previewSaved=true;}angle=open?85:0;ApplyPose();}
        public void Configure(Transform leftLeaf, Transform rightLeaf, Transform gateway)
        { left = leftLeaf; right = rightLeaf; threshold = gateway; RememberClosed(); }
        private void Awake() => RememberClosed();
        private void RememberClosed() { if (left != null) leftClosed = left.localRotation; if (right != null) rightClosed = right.localRotation; }
        public void RequestNear(Vector3 position)
        {
            if (threshold == null) return;
            Vector3 difference = position - threshold.position; difference.y = 0;
            if (difference.sqrMagnitude < 3.5f * 3.5f) until = Time.time + 1.5f;
        }
        private void Update()
        {
            angle = Mathf.MoveTowards(angle, Time.time < until ? 85f : 0f, 180f * Time.deltaTime);ApplyPose();
        }
        private void ApplyPose()
        {
            if (left != null) left.localRotation = Quaternion.AngleAxis(-angle, ParentUp(left)) * leftClosed;
            if (right != null) right.localRotation = Quaternion.AngleAxis(angle, ParentUp(right)) * rightClosed;
        }
        private static Vector3 ParentUp(Transform leaf) => leaf.parent != null ? leaf.parent.InverseTransformDirection(Vector3.up).normalized : Vector3.up;
    }
}
