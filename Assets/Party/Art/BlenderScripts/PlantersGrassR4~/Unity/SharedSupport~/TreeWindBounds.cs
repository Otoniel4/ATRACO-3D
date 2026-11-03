using UnityEngine;

namespace Alarma.City
{
    // El movimiento del shader necesita margen de descarte aunque la malla de reposo esté inmóvil.
    [ExecuteAlways]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
    public sealed class TreeWindBounds : MonoBehaviour
    {
        [SerializeField, Min(0f)] private float worldPadding = 1f;
        private MeshRenderer targetRenderer;

        private void OnEnable() => RefreshBounds();
        private void OnValidate() => RefreshBounds();

        public void RefreshBounds()
        {
            targetRenderer = GetComponent<MeshRenderer>();
            MeshFilter filter = GetComponent<MeshFilter>();
            if (targetRenderer == null || filter == null || filter.sharedMesh == null) return;

            Vector3 scale = transform.lossyScale;
            float smallestScale = Mathf.Max(0.001f,
                Mathf.Min(Mathf.Abs(scale.x), Mathf.Min(Mathf.Abs(scale.y), Mathf.Abs(scale.z))));
            Bounds paddedBounds = filter.sharedMesh.bounds;
            paddedBounds.Expand(2f * worldPadding / smallestScale);
            targetRenderer.localBounds = paddedBounds;
        }

        private void OnDisable()
        {
            if (targetRenderer != null) targetRenderer.ResetLocalBounds();
        }
    }
}
