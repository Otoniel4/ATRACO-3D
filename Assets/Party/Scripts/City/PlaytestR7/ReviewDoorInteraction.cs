using System;
using UnityEngine;
using Alarma.AI.CityLife;

namespace Alarma.City.Playtest
{
    // Acercamiento, contacto y empuje. El motor conserva gravedad y colisión durante el gesto.
    [DefaultExecutionOrder(-80)]
    public sealed class ReviewDoorInteraction : MonoBehaviour
    {
        private enum Phase { Approach, Contact, Push }
        [SerializeField] private ReviewInput input;
        [SerializeField] private Transform player;
        [SerializeField] private ShopDoor[] doors = Array.Empty<ShopDoor>();
        [SerializeField] private ReviewSlidingDoor[] shutters = Array.Empty<ReviewSlidingDoor>();
        private ReviewPlayerMotor motor;
        private ReviewCharacterView view;
        private ShopDoor activeDoor, lastAdvanceDoor;
        private PedestrianReach arm;
        private Transform palmTarget;
        private Vector3 stand, facing;
        private Phase phase;
        private float deadline, pushStarted;
        public bool PromptVisible { get; private set; }

        public void Configure(ReviewInput controls, Transform observer, ShopDoor[] hinged, ReviewSlidingDoor[] sliding)
        {
            input = controls;
            player = observer;
            doors = hinged;
            shutters = sliding;
        }

        private void Awake()
        {
            if (player == null) return;
            motor = player.GetComponent<ReviewPlayerMotor>();
            view = player.GetComponent<ReviewCharacterView>();
        }

        private void Update()
        {
            PromptVisible = false;
            if (player == null || input == null || !input.Active)
            {
                EndGesture();
                return;
            }
            if (activeDoor != null)
            {
                AdvanceGesture();
                return;
            }
            Vector3 position = player.position;
            Vector3 move = motor != null ? motor.MoveDirection : Vector3.zero;
            if (move.sqrMagnitude < .1f || lastAdvanceDoor != null && !lastAdvanceDoor.InReach(position)) lastAdvanceDoor = null;
            ShopDoor door = null;
            float closest = float.PositiveInfinity;
            foreach (var candidate in doors)
            {
                if (candidate == null || candidate.CanPass || !candidate.InReach(position)) continue;
                float distance = Flat(candidate.Gateway.position - position).sqrMagnitude;
                if (distance >= closest) continue;
                closest = distance;
                door = candidate;
            }

            // E elige un solo acceso. Avanzar hacia una hoja a corta distancia también inicia el empuje.
            ReviewSlidingDoor shutter = null;
            foreach (var candidate in shutters)
            {
                if (candidate == null || candidate.Gateway == null || !candidate.InReach(position)) continue;
                if (candidate.IsOpen) { candidate.KeepClearFor(position); continue; }
                float distance = Flat(candidate.Gateway.position - position).sqrMagnitude;
                if (distance >= closest) continue;
                closest = distance;
                shutter = candidate;
            }
            PromptVisible = door != null || shutter != null;
            if (shutter != null)
            {
                if (input.InteractPressed) shutter.Push();
                return;
            }
            if (door == null) return;
            Vector3 towardGate = Flat(door.Gateway.position - position);
            bool advance = door != lastAdvanceDoor && closest < .68f * .68f && move.sqrMagnitude > .35f
                && Vector3.Dot(move.normalized, towardGate.normalized) > .45f;
            if ((input.InteractPressed || advance) && BeginGesture(door))
            {
                lastAdvanceDoor = door;
                AdvanceGesture();
            }
        }

        private bool BeginGesture(ShopDoor door)
        {
            arm = view != null ? view.CurrentReach : null;
            if (motor == null || arm == null || !door.TryGetPushContact(player.position, motor.BodyRadius,
                out palmTarget, out stand, out facing) || !motor.BeginDoorInteraction()) return false;
            activeDoor = door;
            phase = Phase.Approach;
            deadline = Time.time + 1.8f;
            return true;
        }

        private void AdvanceGesture()
        {
            if (arm == null || view == null || view.CurrentReach != arm || palmTarget == null
                || motor == null || !motor.DoorInteractionActive || !activeDoor.InReach(player.position)
                || Time.time > deadline || activeDoor.CanPass)
            {
                EndGesture();
                return;
            }
            if (phase == Phase.Approach)
            {
                Vector3 delta = Flat(stand - player.position);
                motor.GuideDoorInteraction(delta, facing);
                if (delta.sqrMagnitude > .075f * .075f || Vector3.Dot(player.forward, facing) < .82f) return;
                phase = Phase.Contact;
            }
            motor.GuideDoorInteraction(Vector3.zero, facing);
            if (phase == Phase.Contact)
            {
                arm.ReachSurface(palmTarget);
                if (!arm.HasContact)
                {
                    // Si la estatura deja la palma corta, acercar la cápsula sin atravesar la hoja.
                    if (!arm.CanReach(palmTarget.position, .02f))
                        motor.GuideDoorInteraction(facing * (.30f * Time.deltaTime), facing);
                    return;
                }
                // El giro comienza después de que la palma llegue a la superficie.
                activeDoor.PushFrom(player.position);
                phase = Phase.Push;
                pushStarted = Time.time;
                deadline = Time.time + 1.35f;
                return;
            }
            if (Time.time - pushStarted < .24f && arm.CanReach(palmTarget.position)) arm.ReachSurface(palmTarget);
            else arm.Release(palmTarget);
        }

        private void EndGesture()
        {
            if (activeDoor == null && palmTarget == null) return;
            if (arm != null) arm.Release(palmTarget);
            if (motor != null) motor.EndDoorInteraction();
            activeDoor = null;
            palmTarget = null;
            arm = null;
        }

        private void OnDisable() => EndGesture();
        private static Vector3 Flat(Vector3 value) { value.y = 0f; return value; }
    }
}
