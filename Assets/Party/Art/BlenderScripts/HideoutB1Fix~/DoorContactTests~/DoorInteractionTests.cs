// Se enlaza ReviewDoorInteraction.cs real. Motor, puerta y brazo son sustitutos controlados.
using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.City.Playtest;

namespace UnityEngine
{
    public sealed class DefaultExecutionOrder : Attribute { public DefaultExecutionOrder(int order) {} }
    public sealed class SerializeField : Attribute {}
    public class MonoBehaviour {}
    public static class Time { public static float time, deltaTime; }
    public static class Debug { public static readonly List<string> Warnings = new List<string>(); public static void LogWarning(string value) => Warnings.Add(value); }
    public struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public static Vector3 zero => default;
        public float sqrMagnitude => x*x + y*y + z*z;
        public Vector3 normalized => sqrMagnitude > 0 ? this * (1f / MathF.Sqrt(sqrMagnitude)) : zero;
        public static float Dot(Vector3 a, Vector3 b) => a.x*b.x + a.y*b.y + a.z*b.z;
        public static Vector3 operator +(Vector3 a, Vector3 b) => new Vector3(a.x+b.x, a.y+b.y, a.z+b.z);
        public static Vector3 operator -(Vector3 a, Vector3 b) => new Vector3(a.x-b.x, a.y-b.y, a.z-b.z);
        public static Vector3 operator *(Vector3 a, float b) => new Vector3(a.x*b, a.y*b, a.z*b);
    }
    public sealed class Transform
    {
        public Vector3 position, forward = new Vector3(0, 0, 1);
        private readonly Dictionary<Type, object> components = new Dictionary<Type, object>();
        public void Add<T>(T value) => components.Add(typeof(T), value);
        public T GetComponent<T>() => (T)components[typeof(T)];
    }
}

namespace Alarma.AI.CityLife
{
    public sealed class ShopDoor
    {
        public readonly Transform Gateway = new Transform();
        private readonly Transform contact = new Transform();
        public bool CanPass;
        public int Pushes;
        public string BlockingObstacle => "ninguno";
        public bool InReach(Vector3 point) => (Gateway.position - point).sqrMagnitude < 1.6f * 1.6f;
        public bool TryGetPushContact(Vector3 point, float radius, out Transform palm, out Vector3 stand, out Vector3 face)
        {
            palm = contact;
            face = new Vector3(0, 0, point.z <= Gateway.position.z ? 1 : -1);
            stand = Gateway.position - face * .4f;
            return true;
        }
        public void PushFrom(Vector3 point) => Pushes++;
    }
    public sealed class PedestrianReach
    {
        public bool HasContact, Reachable = true;
        public bool SurfaceReachable = true;
        public float ShoulderStandX;
        public Vector3 PalmPosition => Vector3.zero;
        public int Requests, Releases;
        public void ReachSurface(Transform target) => Requests++;
        public bool CanReach(Vector3 point, float tolerance = .04f) => Reachable;
        public bool CanReachSurface(Transform point, float tolerance = .005f) => SurfaceReachable;
        public Vector3 AlignSurfaceStand(Vector3 contact, Vector3 stand, Vector3 forward) => new Vector3(ShoulderStandX, stand.y, stand.z);
        public void Release(Transform target) => Releases++;
    }
}

namespace Alarma.City.Playtest
{
    public sealed class ReviewInput { public bool Active = true, InteractPressed; }
    public sealed class ReviewCharacterView { public PedestrianReach CurrentReach = new PedestrianReach(); }
    public sealed class ReviewSlidingDoor
    {
        public Transform Gateway = new Transform();
        public bool IsOpen;
        public int Pushes;
        public bool InReach(Vector3 point) => (Gateway.position - point).sqrMagnitude < 2.2f * 2.2f;
        public void KeepClearFor(Vector3 point) {}
        public void Push() => Pushes++;
    }
    public sealed class ReviewPlayerMotor
    {
        public Transform Body;
        public bool DoorInteractionActive, Blocked;
        public float BodyRadius => .24f;
        public Vector3 MoveDirection;
        public int Begins;
        public bool BeginDoorInteraction() { Begins++; DoorInteractionActive = true; return true; }
        public void EndDoorInteraction() => DoorInteractionActive = false;
        public void GuideDoorInteraction(Vector3 delta, Vector3 facing)
        {
            Body.forward = facing;
            if (!Blocked) Body.position += delta;
        }
    }
}

internal static class DoorInteractionTests
{
    private sealed class Fixture
    {
        public readonly Transform Player = new Transform();
        public readonly ReviewInput Input = new ReviewInput();
        public readonly ReviewCharacterView View = new ReviewCharacterView();
        public readonly ReviewPlayerMotor Motor = new ReviewPlayerMotor();
        public readonly ShopDoor Near = new ShopDoor(), Far = new ShopDoor();
        public readonly ReviewSlidingDoor Slider = new ReviewSlidingDoor();
        public readonly ReviewDoorInteraction Interaction = new ReviewDoorInteraction();
        public Fixture(float z = -.4f)
        {
            Time.time = 0;
            Time.deltaTime = .05f;
            Player.position = new Vector3(0, 0, z);
            Far.Gateway.position = new Vector3(.8f, 0, 0);
            Slider.Gateway.position = new Vector3(2.5f, 0, 0);
            Motor.Body = Player;
            Player.Add(Motor);
            Player.Add(View);
            Interaction.Configure(Input, Player, new[] { Far, Near }, new[] { Slider });
            Invoke("Awake");
        }
        public void Tick(bool key = false)
        {
            Input.InteractPressed = key;
            Invoke("Update");
            Time.time += Time.deltaTime;
        }
        private void Invoke(string method) => typeof(ReviewDoorInteraction).GetMethod(method,
            BindingFlags.NonPublic | BindingFlags.Instance).Invoke(Interaction, null);
    }

    private static int passed;
    private static void Check(bool result, string label)
    {
        if (!result) throw new InvalidOperationException(label);
        passed++;
        Console.WriteLine("PASS " + label);
    }

    public static int Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        var contact = new Fixture();
        contact.Tick(true);
        Check(contact.Motor.DoorInteractionActive && contact.View.CurrentReach.Requests > 0 && contact.Near.Pushes == 0,
            "E solicita palma antes de mover hoja");
        contact.Tick();
        Check(contact.Near.Pushes == 0 && contact.Far.Pushes == 0, "ninguna hoja abre antes de confirmar contacto");
        contact.View.CurrentReach.HasContact = true;
        contact.Tick();
        contact.Tick();
        Check(contact.Near.Pushes == 1 && contact.Far.Pushes == 0, "solo se empuja una vez el acceso más cercano");
        contact.Near.CanPass = true;
        contact.Tick();
        Check(!contact.Motor.DoorInteractionActive && contact.View.CurrentReach.Releases > 0, "paso libre devuelve locomoción y suelta palma");

        var advance = new Fixture();
        advance.Motor.MoveDirection = new Vector3(0, 0, 1);
        advance.View.CurrentReach.HasContact = true;
        advance.Tick();
        Check(advance.Near.Pushes == 1, "avanzar cerca del umbral activa empuje sin repetir E");
        for (int i = 0; i < 36; i++) advance.Tick();
        Check(!advance.Motor.DoorInteractionActive && advance.Motor.Begins == 1, "mantener W tras atasco no repite el gesto");
        advance.Tick(true);
        Check(advance.Motor.Begins == 2, "E permite reintentar un empuje fallido");

        var blocked = new Fixture(-1f);
        blocked.Motor.Blocked = true;
        blocked.View.CurrentReach.HasContact = true;
        blocked.Tick(true);
        for (int i = 0; i < 40; i++) blocked.Tick();
        Check(!blocked.Motor.DoorInteractionActive && blocked.Near.Pushes == 0, "obstáculo en acercamiento cancela antes del empuje");

        var changed = new Fixture();
        changed.Tick(true);
        changed.View.CurrentReach = new PedestrianReach();
        changed.Tick();
        Check(!changed.Motor.DoorInteractionActive && changed.Near.Pushes == 0, "cambiar de rol cancela gesto anterior");

        var paused = new Fixture();
        paused.Tick(true);
        paused.Input.Active = false;
        paused.Tick();
        Check(!paused.Motor.DoorInteractionActive, "abrir menú libera el bloqueo");

        var slider = new Fixture();
        slider.Slider.Gateway.position = new Vector3(0, 0, -.35f);
        slider.Tick(true);
        Check(slider.Slider.Pushes == 1 && slider.Motor.Begins == 0, "portón corredizo más cercano recibe E solo");

        var waiting = new Fixture();
        waiting.Tick();
        Check(waiting.Near.Pushes == 0 && waiting.Motor.Begins == 0, "estar quieto junto al local no inicia el empuje");

        var shoulder = new Fixture();
        shoulder.View.CurrentReach.ShoulderStandX = -.23f;
        shoulder.Tick(true);
        shoulder.Tick();
        Check(MathF.Abs(shoulder.Player.position.x + .23f) < .001f,
            "E alinea el hombro real del jugador antes de empujar");

        var shortPalm = new Fixture(-.47f);
        shortPalm.View.CurrentReach.Reachable = true;
        shortPalm.View.CurrentReach.SurfaceReachable = false;
        shortPalm.Tick(true);
        for (int i = 0; i < 8; i++) shortPalm.Tick();
        Check(shortPalm.Player.position.z > -.37f && shortPalm.Near.Pushes == 0,
            "La palma vertical corta sigue acercándose aunque el agarre de objetos dé alcance válido");
        shortPalm.View.CurrentReach.HasContact = true;
        shortPalm.Tick();
        Check(shortPalm.Near.Pushes == 1, "E abre después de completar el ajuste de muñeca");
        shortPalm.Near.CanPass = true;
        shortPalm.Tick();
        Check(!shortPalm.Motor.DoorInteractionActive, "Cruce libre devuelve el control para salir");

        var inside = new Fixture(.4f);
        inside.Player.forward = new Vector3(0, 0, -1);
        inside.View.CurrentReach.HasContact = true;
        inside.Tick(true);
        Check(inside.Near.Pushes == 1 && inside.Player.forward.z < 0, "E abre también desde dentro de la guarida");

        var retreat = new Fixture();
        retreat.Tick(true);
        retreat.Motor.MoveDirection = new Vector3(0, 0, -1);
        retreat.Tick();
        Check(!retreat.Motor.DoorInteractionActive && retreat.Near.Pushes == 0,
            "Retroceder cancela de inmediato el contacto sin abrir la hoja");

        var unreachable = new Fixture();
        unreachable.View.CurrentReach.SurfaceReachable = false;
        unreachable.Motor.Blocked = true;
        int warnings = Debug.Warnings.Count;
        unreachable.Tick(true);
        for (int i = 0; i < 40; i++) unreachable.Tick();
        Check(!unreachable.Motor.DoorInteractionActive && unreachable.Near.Pushes == 0,
            "Contacto imposible libera movimiento sin atravesar la puerta");
        Check(Debug.Warnings.Count == warnings + 1 && Debug.Warnings[Debug.Warnings.Count - 1].Contains("Contact"),
            "Un fallo informa su fase una vez sin inundar Console");

        Console.WriteLine("DOOR_INTERACTION_TESTS_PASSED " + passed);
        return 0;
    }
}
