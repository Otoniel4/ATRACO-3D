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
                // Retroceder cancela el gesto sin esperar al temporizador.
                if (motor != null && Vector3.Dot(motor.MoveDirection, facing) < -.35f)
                {
                    EndGesture();
                    return;
                }
                AdvanceGesture();
                return;
            }
            if (palmTarget != null || arm != null) EndGesture();
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
                || activeDoor.CanPass)
            {
                EndGesture();
                return;
            }
            if (Time.time > deadline)
            {
                float error = (float)Math.Sqrt((arm.PalmPosition - palmTarget.position).sqrMagnitude);
                Debug.LogWarning($"Alarma: gesto de puerta cancelado en {phase}; distancia palma {error:F3} m; "
                    + $"obstáculo de hoja: {activeDoor.BlockingObstacle}. Movimiento liberado.");
                EndGesture();
                return;
            }
            if (phase == Phase.Approach)
            {
                // Orientar primero permite calcular el hombro en el marco real del personaje.
                if (Vector3.Dot(player.forward, facing) < .98f)
                {
                    motor.GuideDoorInteraction(Vector3.zero, facing);
                    return;
                }
                Vector3 aligned = arm.AlignSurfaceStand(palmTarget.position, stand, facing);
                Vector3 delta = Flat(aligned - player.position);
                motor.GuideDoorInteraction(delta, facing);
                if (delta.sqrMagnitude > .025f * .025f) return;
                phase = Phase.Contact;
                deadline = Time.time + 1.4f;
            }
            motor.GuideDoorInteraction(Vector3.zero, facing);
            if (phase == Phase.Contact)
            {
                arm.ReachSurface(palmTarget);
                if (!arm.HasContact)
                {
                    // Seguir corrigiendo la muñeca real: el agarre de objetos podía dar alcance válido
                    // mientras la palma vertical seguía separada de la puerta.
                    Vector3 correction = Flat(arm.AlignSurfaceStand(palmTarget.position, player.position, facing) - player.position);
                    if (!arm.CanReachSurface(palmTarget)) correction += facing * (.30f * Time.deltaTime);
                    motor.GuideDoorInteraction(correction, facing);
                    return;
                }
                // El giro comienza después de que la palma llegue a la superficie.
                activeDoor.PushFrom(player.position);
                phase = Phase.Push;
                pushStarted = Time.time;
                deadline = Time.time + 1.35f;
                return;
            }
            if (Time.time - pushStarted < .34f && arm.CanReachSurface(palmTarget, .015f)) arm.ReachSurface(palmTarget);
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
