using System;
using System.Reflection;
using Alarma.AI.CityLife;
using UnityEngine;

internal static class Regression
{
    private static readonly FieldInfo Angle = typeof(ShopDoor).GetField("angle", BindingFlags.Instance | BindingFlags.NonPublic);
    private static readonly MethodInfo Update = typeof(ShopDoor).GetMethod("Update", BindingFlags.Instance | BindingFlags.NonPublic);
    private static int count;

    private static void Check(bool condition, string label)
    {
        if (!condition) throw new InvalidOperationException(label);
        count++;
        Console.WriteLine("PASS " + label);
    }

    private static void Tick(ShopDoor door, float dt)
    {
        Time.time += dt;
        Time.deltaTime = dt;
        Update.Invoke(door, null);
    }

    private static void TickMany(ShopDoor door, int frames, float dt = .02f)
    {
        for (int i = 0; i < frames; i++) Tick(door, dt);
    }

    private static float GetAngle(ShopDoor door) => (float)Angle.GetValue(door);
    private static void SetAngle(ShopDoor door, float value) => Angle.SetValue(door, value);

    private static Transform Leaf(Transform root, float hingeX, float inward, float length, string side)
    {
        var leaf = new Transform("DoorLeaf_" + side) { localPosition = new Vector3(hingeX, 0, 0) };
        leaf.SetParent(root, false);
        leaf.Component = new BoxCollider
        {
            transform = leaf,
            center = new Vector3(inward * length / 2f, 1f, 0),
            size = new Vector3(length, 2f, .10f)
        };
        var marker = new Transform("PushContact_" + side) { localPosition = new Vector3(inward * length * .8f, 1.2f, 0) };
        marker.SetParent(leaf, false);
        return leaf;
    }

    private static (ShopDoor door, Transform left, Transform right, Vector3 front, Vector3 back, Vector3 normal) Fixture(bool doubleLeaf, float yaw = 0f)
    {
        Time.time = 1f;
        Physics.Reset();
        var root = new Transform("PrefabRoot") { localRotation = Quaternion.AngleAxis(yaw, Vector3.up) };
        var threshold = new Transform("Umbral");
        threshold.SetParent(root, false);
        var left = Leaf(root, .72f, -1, doubleLeaf ? .71f : 1.4f, "L");
        var right = doubleLeaf ? Leaf(root, -.72f, 1, .71f, "R") : null;
        var door = new ShopDoor();
        door.Configure(left, right, threshold);
        Vector3 normal = root.rotation * Vector3.forward;
        return (door, left, right, normal * .75f, normal * -.75f, normal);
    }

    private static void OpeningDirections()
    {
        foreach (bool doubleLeaf in new[] { false, true })
            foreach (bool fromFront in new[] { false, true })
            {
                var f = Fixture(doubleLeaf, 35f);
                Vector3 actor = fromFront ? f.front : f.back;
                float sign = fromFront ? 1f : -1f;
                f.door.PushFrom(actor);
                Tick(f.door, .02f);
                Check(GetAngle(f.door) > 0 && !f.door.CanPass, "empuje inicia recorrido antes de autorizar paso");
                TickMany(f.door, 43);
                var left = f.left.GetComponent<BoxCollider>();
                var right = f.right?.GetComponent<BoxCollider>();
                Check(f.door.CanPass && Vector3.Dot(left.bounds.center, f.normal) * sign < -.2f
                    && (right == null || Vector3.Dot(right.bounds.center, f.normal) * sign < -.2f),
                    (doubleLeaf ? "puerta doble" : "portón simple") + (fromFront ? " desde frente" : " desde atrás") + " se abre alejándose");
            }
    }

    private static void Anchors()
    {
        var f = Fixture(false, 35f);
        Check(f.door.TryGetPushContact(f.front, .27f, out var front, out var stand, out var toward), "contacto frontal disponible");
        Check(front.parent == f.left && MathF.Abs(front.position.y - 1.2f) < .001f
            && MathF.Abs(Vector3.Dot(front.position, f.normal) - .05f) < .001f,
            "contacto frontal sobre la cara de la hoja a altura del marcador");
        Vector3 initial = front.position;
        Check(f.door.TryGetPushContact(f.back, .27f, out var back, out _, out _)
            && back != front && (front.position-initial).magnitude < .001f
            && MathF.Abs(Vector3.Dot(back.position, f.normal) + .05f) < .001f,
            "caras independientes conservan el contacto frontal");
        Check(Vector3.Dot(toward, f.normal) < -.99f && Vector3.Dot(stand, f.normal) > .35f
            && MathF.Abs(Vector3.Dot(stand, Vector3.Cross(Vector3.up, f.normal))) < .40f,
            "posición de empuje deja margen para la cápsula");
        f.door.PushFrom(f.front);
        TickMany(f.door, 28);
        Check((front.position-initial).magnitude > .10f && front.parent == f.left, "ancla sigue la hoja durante el giro");
        Check(!f.door.TryGetPushContact(new Vector3(0, .8f, 0), .27f, out _, out _, out _), "rechaza contacto desde otra altura");
        var doubleDoor = Fixture(true);
        Check(doubleDoor.door.TryGetPushContact(new Vector3(-.4f, 0, .75f), .27f, out var nearest, out _, out _)
            && nearest.parent == doubleDoor.right, "doble hoja selecciona la cara más cercana");
    }

    private static void PassageThresholds()
    {
        foreach (bool doubleLeaf in new[] { false, true })
        {
            var f = Fixture(doubleLeaf);
            float allowed = doubleLeaf ? 70f : 82f;
            SetAngle(f.door, allowed - .01f);
            Check(!f.door.CanPass && !f.door.IsOpen, "rechaza paso antes de " + allowed);
            SetAngle(f.door, allowed);
            Check(f.door.CanPass && f.door.IsOpen, "autoriza paso desde " + allowed);
        }
    }

    private static void OccupancyAndSweep()
    {
        var f = Fixture(false);
        Physics.OwnLeaf = f.left.GetComponent<BoxCollider>();
        f.door.PushFrom(f.front);
        TickMany(f.door, 50);
        Check(f.door.CanPass, "su propio collider no bloquea la apertura");
        Physics.Occupant = true;
        TickMany(f.door, 85);
        Check(GetAngle(f.door) >= 84f, "ocupante del umbral mantiene abierta la puerta tras vencer la petición");
        Physics.Occupant = false;
        Physics.AllSweepBlocked = true;
        float held = GetAngle(f.door);
        Tick(f.door, .10f);
        Check(MathF.Abs(GetAngle(f.door)-held) < .001f, "cierre detenido ante un obstáculo en el barrido");
        Physics.AllSweepBlocked = false;
        TickMany(f.door, 200);
        Check(GetAngle(f.door) < .04f && !f.door.CanPass, "cierra al quedar libre");

        f = Fixture(false);
        Physics.BlockerPoint = f.left.position + Quaternion.AngleAxis(-20f, Vector3.up) * new Vector3(-1.15f, 1f, 0f);
        f.door.PushFrom(f.front);
        Tick(f.door, 1f);
        Check(GetAngle(f.door) == 0f && Physics.SweepCalls > 10, "fotograma largo detecta bloqueo intermedio en arco");
        f = Fixture(false);
        Physics.Saturated = true;
        f.door.PushFrom(f.front);
        Tick(f.door, .10f);
        Check(GetAngle(f.door) == 0f, "saturación de consulta conserva la pose");
    }

    private static void Main()
    {
        OpeningDirections();
        Anchors();
        PassageThresholds();
        OccupancyAndSweep();
        Console.WriteLine("PASS " + count + " comprobaciones con ShopDoor.cs real y física simulada");
    }
}
