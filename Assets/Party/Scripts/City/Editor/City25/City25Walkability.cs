using System.Collections.Generic;
using UnityEngine;
using Alarma.AI.Street;

namespace Alarma.City.Editor
{
    // Verifica el plano contra la geometría importada antes de serializar la red peatonal.
    internal sealed class City25Walkability
    {
        private const float CorridorRadius = SidewalkGraph.LaneOffset + SidewalkClearance.Radius + .04f;
        private readonly Dictionary<MeshCollider, GroundTriangles> ground = new Dictionary<MeshCollider, GroundTriangles>();

        public bool HasSidewalk(Vector2 point, out float feetY)
        {
            if (!Support(point, false, out feetY)) return false;
            Vector3 feet = new Vector3(point.x, feetY, point.y);
            return !Physics.CheckCapsule(Bottom(feet), Top(feet), CorridorRadius,
                SidewalkClearance.StaticMask, QueryTriggerInteraction.Ignore);
        }

        public bool ClearSegment(Vector2 a, float ay, Vector2 b, float by, bool crossing)
            => ClearSegment(a, ay, b, by, crossing, false);

        public bool ClearApproach(Vector3 node, Vector3 marker, out Vector3 feet)
        {
            Vector2 a = new Vector2(node.x, node.z), b = new Vector2(marker.x, marker.z);
            feet = marker;
            if (!Support(b, false, out float height, true)) return false;
            feet.y = height;
            if (Physics.CheckCapsule(Bottom(feet), Top(feet), CorridorRadius, SidewalkClearance.StaticMask, QueryTriggerInteraction.Ignore))
                return false;
            if ((a - b).sqrMagnitude < .015f * .015f) return true;
            return ClearSegment(a, node.y, b, height, false, true);
        }

        private bool ClearSegment(Vector2 a, float ay, Vector2 b, float by, bool crossing, bool frontage)
        {
            Vector2 delta = b - a;
            float length = delta.magnitude;
            if (length < .015f) return false;
            Vector2 along = delta / length;
            Vector2 side = new Vector2(along.y, -along.x) * (SidewalkGraph.LaneOffset + SidewalkClearance.Radius);
            int samples = Mathf.CeilToInt(length / .8f);
            float highest = Mathf.Max(ay, by);
            for (int i = 0; i <= samples; i++)
            {
                Vector2 p = Vector2.Lerp(a, b, i / (float)samples);
                if (!Support(p, crossing, out float height, frontage) || !Support(p + side, crossing, out float right, frontage)
                    || !Support(p - side, crossing, out float left, frontage)) return false;
                highest = Mathf.Max(highest, Mathf.Max(height, Mathf.Max(right, left)));
            }
            Vector3 start = new Vector3(a.x, highest, a.y);
            return !Physics.CapsuleCast(Bottom(start), Top(start), CorridorRadius, new Vector3(along.x, 0f, along.y),
                length, SidewalkClearance.StaticMask, QueryTriggerInteraction.Ignore);
        }

        private bool Support(Vector2 point, bool crossing, out float feetY, bool frontage = false)
        {
            feetY = SidewalkGraph.Height;
            if (!Physics.Raycast(new Vector3(point.x, .475f, point.y), Vector3.down, out RaycastHit hit, .64f,
                SidewalkClearance.StaticMask, QueryTriggerInteraction.Ignore) || hit.normal.y < .65f
                || !(hit.collider is MeshCollider mesh) || hit.triangleIndex < 0) return false;
            if (!ground.TryGetValue(mesh, out GroundTriangles triangles))
                ground[mesh] = triangles = new GroundTriangles(mesh);
            if (!triangles.Allows(hit.triangleIndex, crossing, frontage)) return false;
            feetY = hit.point.y + SidewalkClearance.FeetGap;
            return true;
        }

        private static Vector3 Bottom(Vector3 feet) => feet + Vector3.up * CorridorRadius;
        private static Vector3 Top(Vector3 feet) => feet + Vector3.up * (SidewalkClearance.BodyHeight - CorridorRadius);

        private sealed class GroundTriangles
        {
            private readonly int[] ends;
            private readonly bool[] sidewalk, road, frontage;

            public GroundTriangles(MeshCollider collider)
            {
                Mesh mesh = collider.sharedMesh;
                var renderer = collider.GetComponent<MeshRenderer>();
                var materials = renderer != null ? renderer.sharedMaterials : System.Array.Empty<Material>();
                int count = mesh != null ? mesh.subMeshCount : 0;
                ends = new int[count]; sidewalk = new bool[count]; road = new bool[count]; frontage = new bool[count];
                int triangles = 0;
                for (int i = 0; i < count; i++)
                {
                    triangles += (int)(mesh.GetIndexCount(i) / 3);
                    ends[i] = triangles;
                    string name = i < materials.Length && materials[i] != null ? materials[i].name : string.Empty;
                    sidewalk[i] = name == "City25_Acera" || name == "City25_Bordillo";
                    road[i] = name == "City25_Asfalto" || name == "City25_LineaBlanca" || name == "City25_LineaAmarilla";
                    frontage[i] = name == "City25_Cesped" || name == "City25_Lote" || name == "City25_Concreto"
                        || name == "City25_Pavimento" || name == "City25_Alcantarilla";
                }
            }

            public bool Allows(int triangle, bool crossing, bool approach)
            {
                for (int i = 0; i < ends.Length; i++)
                    if (triangle < ends[i]) return sidewalk[i] || crossing && road[i] || approach && frontage[i];
                return false;
            }
        }
    }
}
