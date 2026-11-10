using UnityEngine;

namespace Alarma.AI.Security
{
    // Patrón State: cada estado del guardia es una clase con lo que hace al entrar, en cada cuadro y al salir, y decide
    // a cuál pasar. «Watches»: en ese estado atiende lo que ve y oye para salir a enfrentar a alguien.
    public abstract class GuardState
    {
        public virtual bool Watches => false;
        public virtual void Enter(SecurityGuard guard) { }
        public abstract void Tick(SecurityGuard guard, float dt);
        public virtual void Exit(SecurityGuard guard) { }
    }

    // En su puesto, mirando a los lados (SentryLook), con la porra enfundada.
    public sealed class PostState : GuardState
    {
        public override bool Watches => true;

        public override void Enter(SecurityGuard guard)
        {
            guard.Motor.Stop();
            guard.Body.DrawBaton(false);
            guard.Body.Show(GuardPose.Quieto);
            if (guard.Sentry != null) guard.Sentry.enabled = true;
        }

        public override void Tick(SecurityGuard guard, float dt) { }

        public override void Exit(SecurityGuard guard) { if (guard.Sentry != null) guard.Sentry.enabled = false; }
    }

    // Corre con la porra en la mano hacia el sospechoso; a distancia de golpe, golpea. Si lo pierde (se rindió en el
    // suelo, lo arrestaron o se alejó del local), vuelve a su puesto.
    public sealed class GuardChaseState : GuardState
    {
        private const float GiveUp = 4f;
        private float blocked; // segundos seguidos sin encontrar por dónde llegar

        public override void Enter(SecurityGuard guard)
        {
            guard.Body.DrawBaton(true);
            guard.Body.Show(GuardPose.Correr);
        }

        public override void Tick(SecurityGuard guard, float dt)
        {
            if (!guard.SuspectActive) { guard.Change(new ReturnState()); return; }
            Vector3 target = guard.Suspect.transform.position;
            if (guard.DistanceTo(target) <= guard.Settings.StrikeDistance) { guard.Change(new StrikeState()); return; }
            guard.Motor.MoveTowards(target, guard.Settings.RunSpeed);
            blocked = guard.Motor.Blocked ? blocked + dt : 0f;
            if (blocked > GiveUp) guard.Change(new ReturnState()); // no hay camino: vuelve a cuidar la puerta
        }
    }

    // Un golpe de porra: levanta, baja y, si el blanco sigue al alcance en el momento justo, le quita vida.
    public sealed class StrikeState : GuardState
    {
        private float time;
        private bool landed;

        public override void Enter(SecurityGuard guard)
        {
            guard.Motor.Stop();
            guard.Body.Show(GuardPose.Golpear);
        }

        public override void Tick(SecurityGuard guard, float dt)
        {
            var settings = guard.Settings;
            if (guard.Suspect != null) guard.Face(guard.Suspect.transform.position, dt);
            time += dt / settings.StrikeSeconds;
            guard.Body.Swing(time, settings.HitAt);
            if (!landed && time >= settings.HitAt)
            {
                landed = true;
                if (guard.SuspectActive && guard.DistanceTo(guard.Suspect.transform.position) <= settings.StrikeReach)
                    guard.Victim?.TakeDamage(settings.Damage, guard.gameObject);
            }
            if (time >= 1f) guard.Change(new GuardChaseState());
        }

        public override void Exit(SecurityGuard guard) => guard.Body.RestBaton();
    }

    // Recibió un disparo: cae con física, queda inconsciente, se levanta y sigue (o vuelve al puesto).
    public sealed class GuardDownState : GuardState
    {
        private readonly Vector3 from;
        private float left;
        private bool gettingUp;

        public GuardDownState(Vector3 shotFrom) => from = shotFrom;

        public override void Enter(SecurityGuard guard)
        {
            var settings = guard.Settings;
            guard.Motor.Stop();
            guard.Body.DrawBaton(false);
            if (guard.Sentry != null) guard.Sentry.enabled = false;
            Vector3 push = guard.transform.position - from;
            push.y = 0f;
            push = push.sqrMagnitude > .001f ? push.normalized : -guard.transform.forward;
            guard.Ragdoll.Fall((push + Vector3.up * .15f) * settings.HitImpulse, guard.transform.position + Vector3.up * 1.2f);
            left = Random.Range(settings.StunSeconds.x, settings.StunSeconds.y);
        }

        public override void Tick(SecurityGuard guard, float dt)
        {
            left -= dt;
            if (left > 0f) return;
            if (!gettingUp)
            {
                gettingUp = true;
                left = guard.Settings.GetUpSeconds;
                guard.Body.Resume(guard.Ragdoll.BeginGetUp() ? GuardPose.LevantarseEspalda : GuardPose.LevantarseBoca);
                return;
            }
            if (guard.SuspectActive) guard.Change(new GuardChaseState());
            else guard.Change(new ReturnState());
        }
    }

    // Camina de vuelta a su puesto; atento por si vuelve a ver u oír algo.
    public sealed class ReturnState : GuardState
    {
        private const float Arrived = .6f, GiveUp = 5f;
        private float blocked;

        public override bool Watches => true;

        public override void Enter(SecurityGuard guard)
        {
            guard.Body.DrawBaton(false);
            guard.Body.Show(GuardPose.Caminar);
        }

        public override void Tick(SecurityGuard guard, float dt)
        {
            if (guard.DistanceTo(guard.Post) > Arrived)
            {
                guard.Motor.MoveTowards(guard.Post, guard.Settings.WalkSpeed);
                blocked = guard.Motor.Blocked ? blocked + dt : 0f;
                if (blocked > GiveUp) guard.Change(new PostState()); // no puede volver: vigila desde donde quedó
                return;
            }
            guard.Motor.Stop();
            guard.transform.rotation = guard.PostFacing;
            guard.Change(new PostState());
        }
    }
}
