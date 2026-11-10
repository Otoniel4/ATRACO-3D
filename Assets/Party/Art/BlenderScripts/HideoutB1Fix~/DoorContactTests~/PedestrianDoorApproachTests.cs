using System;
using System.Collections.Generic;
using System.Reflection;
using Alarma.AI.CityLife;
using UnityEngine;

namespace UnityEngine
{
    public sealed class RequireComponent : Attribute { public RequireComponent(Type _) {} }
    public sealed class Min : Attribute { public Min(float _) {} }
    public sealed class CreateAssetMenu : Attribute { public string menuName; }
    public class ScriptableObject {}
    public partial class MonoBehaviour
    {
        public readonly Transform transform = new("Actor");
        public readonly Dictionary<Type, object> Components = new();
        public T GetComponent<T>() where T : class => Components[typeof(T)] as T;
    }
    public partial struct Vector3
    {
        public static Vector3 ClampMagnitude(Vector3 v, float limit) => v.magnitude > limit ? v.normalized * limit : v;
        public static Vector3 Lerp(Vector3 from, Vector3 to, float t) => from + (to - from) * Mathf.Clamp01(t);
    }
    public partial struct Quaternion
    {
        public static Quaternion RotateTowards(Quaternion from, Quaternion to, float _) => to;
    }
    public sealed partial class Transform
    {
        public Vector3 TransformPoint(Vector3 local) => position + rotation * local;
    }
    public static partial class Mathf
    {
        public static float Clamp01(float value) => Clamp(value, 0f, 1f);
        public static float Min(float a, float b) => MathF.Min(a, b);
    }
    public sealed class CapsuleCollider : Collider { public Vector3 center; public float height, radius; }
    public struct RaycastHit { public Collider collider; }
    public static partial class Physics
    {
        public static Collider CastBlocker, LandingBlocker;
        public static bool SaturateCast;
        public static readonly List<Vector3> TrafficCastOrigins = new();
        public static int CapsuleCastNonAlloc(Vector3 lower, Vector3 upper, float radius, Vector3 direction,
            RaycastHit[] hits, float distance, int mask, QueryTriggerInteraction query)
        {
            if (SaturateCast) return hits.Length;
            if (CastBlocker == null) return 0;
            hits[0].collider = CastBlocker;
            return 1;
        }
        public static int OverlapCapsuleNonAlloc(Vector3 lower, Vector3 upper, float radius, Collider[] hits,
            int mask, QueryTriggerInteraction query)
        {
            if (LandingBlocker == null) return 0;
            hits[0] = LandingBlocker;
            return 1;
        }
        public static bool CheckCapsule(Vector3 lower, Vector3 upper, float radius, int mask, QueryTriggerInteraction query) => false;
        public static bool CapsuleCast(Vector3 lower, Vector3 upper, float radius, Vector3 direction, float distance,
            int mask, QueryTriggerInteraction query)
        {
            TrafficCastOrigins.Add(lower);
            return false;
        }
    }
}

namespace UnityEngine.AI
{
    public sealed class NavMeshAgent { public bool enabled; }
}

internal static class PedestrianDoorApproachTests
{
    private static int passed;
    private static Vector3 Point(float z) => new(0, 0, z);
    private static CityPoint Goal(float z) => new(0, 0, z);
    private static bool Near(float a, float b) => MathF.Abs(a - b) < .0001f;
    private static void Expect(bool valid, string label)
    {
        if (!valid) throw new Exception(label);
        Console.WriteLine("PASS " + label);
        passed++;
    }

    private static CityTrafficController MakeTraffic(params TrafficCell[] cells)
    {
        var controller = new CityTrafficController();
        controller.Configure(new TrafficGraph { Cells = cells }, .75f);
        return controller;
    }

    private static TrafficCell Cell(float z, params int[] links) => new() { Position = Point(z), Links = links };

    private static PedestrianMovement Place(CityTrafficController controller, int id, float z)
    {
        var pawn = new PedestrianMovement();
        pawn.Components.Add(typeof(UnityEngine.AI.NavMeshAgent), new UnityEngine.AI.NavMeshAgent());
        pawn.Components.Add(typeof(CapsuleCollider), new CapsuleCollider {
            transform = pawn.transform, center = new Vector3(0, .85f, 0), height = 1.7f, radius = .23f
        });
        if (!pawn.Place(id, Point(z), controller)) throw new Exception("No se registró el peatón.");
        return pawn;
    }

    private static void Tick(CityTrafficController controller)
    {
        Time.deltaTime = .75f;
        foreach (string method in new[] { "Update", "LateUpdate" })
            typeof(CityTrafficController).GetMethod(method, BindingFlags.Instance | BindingFlags.NonPublic)
                .Invoke(controller, null);
    }

    private static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        CheckClosedDoorRouting();
        var traffic = MakeTraffic(Cell(0, 1), Cell(.60f, 0), Cell(1.50f, 3), Cell(.75f, 2));
        var actor = Place(traffic, 1, 0f);
        var nearby = Place(traffic, 2, 1.50f);
        var obstacle = nearby.GetComponent<CapsuleCollider>();
        Time.deltaTime = .1f;
        Physics.CastBlocker = obstacle;
        Expect(!actor.ApproachDoor(Point(2f)) && Near(actor.transform.position.z, 0),
            "La cáp­sula de otro peatón bloquea el acercamiento");
        Physics.CastBlocker = null;
        Physics.LandingBlocker = obstacle;
        Expect(!actor.ApproachDoor(Point(2f)) && !actor.HasDoorOffset,
            "Un destino ocupado no permite desplazar los pies");
        Physics.LandingBlocker = null;
        Physics.SaturateCast = true;
        Expect(!actor.ApproachDoor(Point(2f)), "Consulta de física llena conserva la posición");
        Physics.SaturateCast = false;
        Physics.CastBlocker = actor.GetComponent<CapsuleCollider>();
        Expect(actor.ApproachDoor(Point(2f)) && Near(actor.transform.position.z, .075f),
            "Ignora su propia cápsula y limita la velocidad de acercamiento");
        Physics.CastBlocker = null;
        for (int i = 0; i < 6; i++) actor.ApproachDoor(Point(2f));
        Expect(actor.AtStepEnd && actor.HasDoorOffset && Near(actor.transform.position.z, .48f),
            "El acercamiento no supera 48 cm desde la celda reservada");
        actor.Pin(true);
        nearby.MoveTo(Goal(.75f));
        Tick(traffic);
        Tick(traffic);
        Expect(Near(actor.transform.position.z, .48f) && actor.AtStepEnd,
            "Repetir la reserva conserva el desplazamiento");
        Expect(Near(nearby.transform.position.z, 1.5f),
            "La reserva de otro peatón respeta el cuerpo desplazado");
        actor.Pin(false);
        actor.MoveTo(Goal(.60f));
        Physics.TrafficCastOrigins.Clear();
        Tick(traffic);
        Expect(Physics.TrafficCastOrigins.Exists(origin => Near(origin.z, .48f)),
            "El barrido del próximo paso comienza en los pies reales");
        Expect(!actor.HasDoorOffset && !actor.AtStepEnd && Near(actor.transform.position.z, .48f),
            "Reservar otra celda mantiene continuidad sin regresar al centro");
        Expect(!actor.ApproachDoor(Point(.5f)), "No se inicia acercamiento en un paso sin terminar");
        Tick(traffic);
        Expect(actor.AtStepEnd && Near(actor.transform.position.z, .60f),
            "Tras liberar la puerta continúa la ruta hacia la celda vecina");
        var passage = typeof(CityTrafficController).GetMethod("CheckPassage", BindingFlags.Instance | BindingFlags.NonPublic);
        Physics.LandingBlocker = new CapsuleCollider { transform = new Transform("Peatón de acera") };
        Expect(!(bool)passage.Invoke(traffic, new object[]{0, 1}), "El visitante espera si la acera ocupa su siguiente celda");
        Physics.LandingBlocker = actor.GetComponent<CapsuleCollider>();
        Physics.LandingBlocker.Owner = actor;
        Expect((bool)passage.Invoke(traffic, new object[]{0, 1}), "La reserva local sigue controlando sus propios residentes");
        Physics.LandingBlocker = null;
        Console.WriteLine("PEDESTRIAN_DOOR_APPROACH_TESTS_PASSED " + passed);
    }

    private static void CheckClosedDoorRouting()
    {
        var graph = new TrafficGraph { Cells = new[] {
            Cell(0, 1), Cell(.5f, 0, 2), Cell(1f, 1, 3), Cell(1.5f, 2, 4), Cell(2f, 3)
        }};
        var traffic = new PedestrianTraffic(graph);
        traffic.TryAdd(1, 0);
        traffic.SetGoal(1, 4);
        bool open = false;
        bool Pass(int a, int b) => open || !(a == 2 && b == 3 || a == 3 && b == 2);
        traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 1, "Con la puerta cerrada inicia la marcha hacia el negocio");
        traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 2, "Llega a la última celda libre para poder alcanzar la manija");
        for (int i = 0; i < 12; i++) traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 2, "No atraviesa la puerta cerrada ni oscila entre celdas");
        traffic.Get(1).Pinned = true;
        traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 2, "Reserva sus pies mientras realiza el gesto");
        open = true;
        traffic.Get(1).Pinned = false;
        traffic.Step(Pass); traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 4, "Retoma la ruta al quedar libre la puerta sin una orden del jugador");
        open = false;
        traffic.SetGoal(1, 0);
        for (int i = 0; i < 12; i++) traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 3, "También se acerca desde dentro cuando la puerta vuelve a cerrarse");
        open = true;
        for (int i = 0; i < 4; i++) traffic.Step(Pass);
        Expect(traffic.Get(1).Cell == 0, "Puede volver a la acera después de abrir hacia fuera");

        // Si existe un camino libre más largo, conserva la preferencia por el desvío.
        var detour = new PedestrianTraffic(new TrafficGraph { Cells = new[] {
            Cell(0, 1, 3), Cell(.5f, 0, 2), Cell(1f, 1, 5),
            Cell(2f, 0, 4), Cell(2.5f, 3, 5), Cell(3f, 4, 2)
        }});
        detour.TryAdd(1,0); detour.SetGoal(1,2);
        detour.Step((a,b) => !(a==1 && b==2 || a==2 && b==1));
        Expect(detour.Get(1).Cell == 3, "Prefiere una ruta libre cuando existe un desvío completo");
        traffic.TryAdd(2, 4);
        traffic.SetGoal(1,4); traffic.SetGoal(2,0);
        open = false;
        for (int i = 0; i < 10; i++)
        {
            traffic.Step(Pass);
            if (traffic.Get(1).Cell == traffic.Get(2).Cell) throw new Exception("Reserva duplicada");
        }
        Expect(traffic.Get(1).Cell == 2 && traffic.Get(2).Cell == 3,
            "Dos clientes se acercan por lados opuestos sin compartir celda ni atravesar la hoja");
    }
}
