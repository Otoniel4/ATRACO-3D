using System.Collections.Generic;
using UnityEngine;
using Alarma.AI.CityLife;

namespace Alarma.AI.Pathing
{
    // Buscador de caminos para los NPC que se mueven por código (civiles que huyen, guardias y policías), sin NavMesh.
    // Divide el suelo alrededor en casillas de 40 cm y prueba cada una con la física: tiene que haber suelo sin escalón
    // alto y caber una persona de pie sin tocar muebles ni paredes. Con eso busca el camino más corto (A*) y lo
    // simplifica para que no vaya en zigzag. Las puertas de los locales no cuentan como obstáculo: se abren al
    // empujarlas. Las casillas ya probadas se recuerdan unos segundos y las comparten todos los NPC.
    // Si no hay camino, lo dice: quien lo pidió decide (por ejemplo, quedarse agachado).
    public static class GridPathfinder
    {
        private const float Cell = .4f, BodyRadius = .28f, StepHeight = .4f, Remember = 4f;
        private const int World = ~((1 << 29) | (1 << 30) | (1 << 31)); // suelo y obstáculos: todo menos personajes e interfaz
        private const int MaxExpanded = 2600, MaxCached = 60000, MaxSearchesPerFrame = 3, SmoothAhead = 12;
        private static readonly (int x, int z, float cost)[] Steps =
        {
            (1, 0, 1f), (-1, 0, 1f), (0, 1, 1f), (0, -1, 1f), (1, 1, 1.4142f), (1, -1, 1.4142f), (-1, 1, 1.4142f), (-1, -1, 1.4142f),
        };
        private static readonly Dictionary<long, Probe> Probes = new Dictionary<long, Probe>();
        private static readonly Dictionary<long, Node> Nodes = new Dictionary<long, Node>();
        private static readonly List<(float score, long key)> Open = new List<(float, long)>();
        private static readonly List<Vector3> Raw = new List<Vector3>();
        private static readonly Collider[] Touching = new Collider[16];
        private static readonly RaycastHit[] Swept = new RaycastHit[16];
        private static int searchFrame, searches;

        private struct Probe { public bool Free; public float Y, Time; }
        private struct Node { public float Cost, Y; public long Parent; public bool Closed; }

        // Hay cupo para otra búsqueda en este cuadro (se reparten para no trabar el juego cuando reaccionan muchos a la vez).
        public static bool Ready => Time.frameCount != searchFrame || searches < MaxSearchesPerFrame;

        // Camino de «from» hasta quedar a «tolerance» metros de «to», sin alejarse más de «range» de la partida.
        public static bool TryFind(Vector3 from, Vector3 to, List<Vector3> path, float tolerance = .9f, float range = 40f)
        {
            path.Clear();
            if (Time.frameCount != searchFrame) { searchFrame = Time.frameCount; searches = 0; }
            searches++;
            if (Probes.Count > MaxCached) Probes.Clear();
            Nodes.Clear(); Open.Clear();
            int startX = Mathf.RoundToInt(from.x / Cell), startZ = Mathf.RoundToInt(from.z / Cell);
            int level = Mathf.RoundToInt(from.y / 3f); // piso: no mezcla lo recordado de la calle con un sótano
            long start = Key(startX, startZ);
            Nodes[start] = new Node { Cost = 0f, Y = from.y, Parent = start };
            Push(Distance(startX, startZ, to), start);
            int reach = Mathf.CeilToInt(range / Cell), expanded = 0;
            long goal = long.MinValue;
            while (Open.Count > 0 && expanded++ < MaxExpanded)
            {
                long key = Pop();
                var node = Nodes[key];
                if (node.Closed) continue;
                node.Closed = true; Nodes[key] = node;
                int x = X(key), z = Z(key);
                if (Distance(x, z, to) <= tolerance) { goal = key; break; }
                for (int i = 0; i < Steps.Length; i++)
                {
                    int nx = x + Steps[i].x, nz = z + Steps[i].z;
                    if (Mathf.Abs(nx - startX) > reach || Mathf.Abs(nz - startZ) > reach) continue;
                    long next = Key(nx, nz);
                    if (Nodes.TryGetValue(next, out var known) && known.Closed) continue;
                    if (!Free(nx, nz, level, node.Y, out float y)) continue;
                    // En diagonal no se roza la esquina de un mueble: los dos costados tienen que estar libres.
                    if (i >= 4 && (!Free(x + Steps[i].x, z, level, node.Y, out _) || !Free(x, z + Steps[i].z, level, node.Y, out _))) continue;
                    float cost = node.Cost + Steps[i].cost * Cell;
                    if (Nodes.TryGetValue(next, out known) && known.Cost <= cost) continue;
                    Nodes[next] = new Node { Cost = cost, Y = y, Parent = key };
                    Push(cost + Distance(nx, nz, to), next);
                }
            }
            if (goal == long.MinValue) return false;
            Raw.Clear();
            for (long key = goal; ; key = Nodes[key].Parent)
            {
                Raw.Add(new Vector3(X(key) * Cell, Nodes[key].Y, Z(key) * Cell));
                if (key == start) break;
            }
            Raw.Reverse();
            Raw[0] = from;
            Smooth(path);
            return true;
        }

        // Largo de un camino, en metros.
        public static float Length(List<Vector3> path)
        {
            float total = 0f;
            for (int i = 1; i < path.Count; i++) total += Vector3.Distance(path[i - 1], path[i]);
            return total;
        }

        // Se puede estar de pie en «point»: hay suelo debajo y cabe una persona. Sirve para descartar rápido un destino
        // que cae dentro de una pared antes de buscarle camino.
        public static bool Standable(Vector3 point)
            => Physics.Raycast(point + Vector3.up * 1.1f, Vector3.down, out var hit, 2.4f, World, QueryTriggerInteraction.Ignore) && Fits(hit.point);

        // Cabe una persona de pie en este punto (para no dar un paso dentro de algo que apareció después de calcular).
        public static bool Fits(Vector3 feet)
        {
            int count = Physics.OverlapCapsuleNonAlloc(feet + Vector3.up * (BodyRadius + .22f), feet + Vector3.up * 1.45f, BodyRadius, Touching, World, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++)
                if (Touching[i].GetComponentInParent<ShopDoor>() == null) return false;
            return true;
        }

        // Una casilla está libre si tiene suelo a la altura de la anterior (sin escalón alto) y cabe una persona de pie.
        private static bool Free(int x, int z, int level, float fromY, out float y)
        {
            long key = Key(x, z) ^ ((long)level << 56);
            if (Probes.TryGetValue(key, out var probe) && Time.time - probe.Time < Remember && Mathf.Abs(probe.Y - fromY) <= StepHeight * 2f)
            {
                y = probe.Y;
                return probe.Free && Mathf.Abs(y - fromY) <= StepHeight;
            }
            var point = new Vector3(x * Cell, fromY, z * Cell);
            bool ground = Physics.Raycast(point + Vector3.up * 1.1f, Vector3.down, out var hit, 2.4f, World, QueryTriggerInteraction.Ignore);
            y = ground ? hit.point.y : fromY;
            bool free = ground && Fits(new Vector3(point.x, y, point.z));
            Probes[key] = new Probe { Free = free, Y = y, Time = Time.time };
            return free && Mathf.Abs(y - fromY) <= StepHeight;
        }

        // Quita los puntos de más: desde cada punto salta al más lejano al que se llega derecho sin tocar nada.
        private static void Smooth(List<Vector3> path)
        {
            int i = 0;
            path.Add(Raw[0]);
            while (i < Raw.Count - 1)
            {
                int next = i + 1;
                for (int j = Mathf.Min(Raw.Count - 1, i + SmoothAhead); j > i + 1; j--)
                    if (Mathf.Abs(Raw[j].y - Raw[i].y) < .15f && Straight(Raw[i], Raw[j])) { next = j; break; }
                path.Add(Raw[next]);
                i = next;
            }
        }

        private static bool Straight(Vector3 a, Vector3 b)
        {
            Vector3 way = b - a;
            float distance = way.magnitude;
            if (distance < .01f) return true;
            int count = Physics.CapsuleCastNonAlloc(a + Vector3.up * (BodyRadius + .22f), a + Vector3.up * 1.45f, BodyRadius, way / distance, Swept, distance, World, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++)
                if (Swept[i].collider.GetComponentInParent<ShopDoor>() == null) return false;
            return true;
        }

        private static float Distance(int x, int z, Vector3 to)
        {
            float dx = x * Cell - to.x, dz = z * Cell - to.z;
            return Mathf.Sqrt(dx * dx + dz * dz);
        }

        private static long Key(int x, int z) => ((long)(x + 0x800000) << 24) | (long)(z + 0x800000);
        private static int X(long key) => (int)((key >> 24) & 0xFFFFFF) - 0x800000;
        private static int Z(long key) => (int)(key & 0xFFFFFF) - 0x800000;

        // Cola de prioridad mínima (montículo binario) sobre una lista.
        private static void Push(float score, long key)
        {
            Open.Add((score, key));
            int i = Open.Count - 1;
            while (i > 0)
            {
                int parent = (i - 1) / 2;
                if (Open[parent].score <= Open[i].score) break;
                (Open[parent], Open[i]) = (Open[i], Open[parent]);
                i = parent;
            }
        }

        private static long Pop()
        {
            long top = Open[0].key;
            int last = Open.Count - 1;
            Open[0] = Open[last];
            Open.RemoveAt(last);
            int i = 0;
            while (true)
            {
                int left = i * 2 + 1, right = left + 1, least = i;
                if (left < Open.Count && Open[left].score < Open[least].score) least = left;
                if (right < Open.Count && Open[right].score < Open[least].score) least = right;
                if (least == i) break;
                (Open[least], Open[i]) = (Open[i], Open[least]);
                i = least;
            }
            return top;
        }
    }
}
