using UnityEngine;

namespace Alarma.Police
{
    // Patrón State: cada estado del agente es una clase con lo que hace al entrar, en cada cuadro y al salir, y decide
    // a cuál pasar. Agregar un comportamiento (por ejemplo, pedir refuerzos) es una clase nueva: no se toca PoliceOfficer.
    public abstract class PoliceState
    {
        public virtual void Enter(PoliceOfficer officer) { }
        public abstract void Tick(PoliceOfficer officer, float dt);
        public virtual void Exit(PoliceOfficer officer) { }
    }

    // Corre al lugar de la denuncia.
    public sealed class ArriveState : PoliceState
    {
        private const float ArriveDistance = 5f;

        public override void Enter(PoliceOfficer officer) => officer.Body.Show(PolicePose.Correr);

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (officer.SuspectVisible) { officer.Change(new ChaseState()); return; }
            if (officer.DistanceTo(officer.LastKnown) < ArriveDistance) { officer.Change(new SearchState()); return; }
            officer.Motor.MoveTowards(officer.LastKnown, officer.Settings.RunSpeed);
        }
    }

    // Camina por los alrededores del último lugar conocido; si pasa el tiempo o ya no queda a quién buscar, se retira.
    public sealed class SearchState : PoliceState
    {
        private const float PointSeconds = 5f;
        private float left, nextPoint;
        private Vector3 point;

        public override void Enter(PoliceOfficer officer)
        {
            left = officer.Settings.SearchSeconds;
            nextPoint = 0f;
            officer.Body.Show(PolicePose.Caminar);
        }

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (officer.SuspectVisible) { officer.Change(new ChaseState()); return; }
            left -= dt;
            nextPoint -= dt;
            if (left <= 0f || !officer.AnyoneAtLarge) { officer.Change(new LeaveState()); return; }
            if (nextPoint <= 0f || officer.DistanceTo(point) < 1f)
            {
                Vector2 offset = Random.insideUnitCircle * officer.Settings.SearchRadius;
                point = officer.LastKnown + new Vector3(offset.x, 0f, offset.y);
                nextPoint = PointSeconds;
            }
            officer.Motor.MoveTowards(point, officer.Settings.WalkSpeed);
        }
    }

    // Corre tras el sospechoso: si está derribado va a esposarlo; si lo tiene a tiro se detiene a apuntar; si lo pierde
    // de vista un rato, lo busca.
    public sealed class ChaseState : PoliceState
    {
        private float unseen;

        public override void Enter(PoliceOfficer officer) => officer.Body.Show(PolicePose.Correr);

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (!officer.SuspectAtLarge) { officer.Change(new SearchState()); return; }
            unseen = officer.SuspectVisible ? 0f : unseen + dt;
            if (unseen > officer.Settings.LoseSightSeconds) { officer.Change(new SearchState()); return; }
            float distance = officer.DistanceTo(officer.LastKnown);
            bool down = officer.Arrestable != null && officer.Arrestable.CanBeArrested;
            if (down && officer.SuspectVisible && distance <= officer.Settings.ArrestDistance) { officer.Change(new ArrestState()); return; }
            if (!down && officer.SuspectVisible && distance <= officer.Settings.ShootRange) { officer.Change(new AimState()); return; }
            officer.Motor.MoveTowards(officer.LastKnown, officer.Settings.RunSpeed);
        }
    }

    // Quieto, con la pistola en la mano: apunta un momento y dispara a intervalos mientras lo vea de pie y a tiro.
    public sealed class AimState : PoliceState
    {
        private const float RangeSlack = 1.25f, UnseenLimit = 1f;
        private float wait, unseen;

        public override void Enter(PoliceOfficer officer)
        {
            officer.Motor.Stop();
            officer.Body.Show(PolicePose.Apuntar);
            officer.Sidearm.AimAt(officer.AimPoint);
            officer.Sidearm.Draw();
            wait = officer.Settings.AimSeconds;
        }

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (!officer.SuspectAtLarge) { officer.Change(new SearchState()); return; }
            unseen = officer.SuspectVisible ? 0f : unseen + dt;
            bool down = officer.Arrestable != null && officer.Arrestable.CanBeArrested;
            if (down || unseen > UnseenLimit || officer.DistanceTo(officer.LastKnown) > officer.Settings.ShootRange * RangeSlack)
            {
                officer.Change(new ChaseState());
                return;
            }
            officer.Face(officer.LastKnown, dt);
            officer.Sidearm.AimAt(officer.AimPoint);
            wait -= dt;
            if (wait > 0f || !officer.SuspectVisible) return;
            officer.Sidearm.Fire(officer.gameObject);
            wait = officer.Settings.ShotInterval;
        }

        public override void Exit(PoliceOfficer officer) => officer.Sidearm.Holster();
    }

    // Junto al derribado: se arrodilla, lo esposa y lo arresta. Después se retira.
    public sealed class ArrestState : PoliceState
    {
        private float left;

        public override void Enter(PoliceOfficer officer)
        {
            officer.Motor.Stop();
            officer.Body.Show(PolicePose.Esposar);
            left = officer.Settings.ArrestSeconds;
        }

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (officer.Arrestable == null || !officer.Arrestable.CanBeArrested) { officer.Change(new ChaseState()); return; } // se levantó o lo arrestó otro
            officer.Face(officer.LastKnown, dt);
            left -= dt;
            if (left > 0f) return;
            officer.Arrestable.Arrest(officer.gameObject);
            officer.Change(new LeaveState());
        }
    }

    // Recibió un disparo: sale volando con física, queda un rato en el suelo, se levanta y sigue.
    public sealed class DownState : PoliceState
    {
        private readonly Vector3 from;
        private float left;
        private bool gettingUp;

        public DownState(Vector3 shotFrom) => from = shotFrom;

        public override void Enter(PoliceOfficer officer)
        {
            var settings = officer.Settings;
            officer.Motor.Stop();
            officer.Sidearm.Holster();
            Vector3 push = officer.transform.position - from;
            push.y = 0f;
            push = push.sqrMagnitude > .001f ? push.normalized : -officer.transform.forward;
            officer.Ragdoll.Fall((push + Vector3.up * settings.HitLift) * settings.HitImpulse, officer.transform.position + Vector3.up * 1.2f);
            left = Random.Range(settings.StunSeconds.x, settings.StunSeconds.y);
        }

        public override void Tick(PoliceOfficer officer, float dt)
        {
            left -= dt;
            if (left > 0f) return;
            if (!gettingUp)
            {
                gettingUp = true;
                left = officer.Settings.GetUpSeconds;
                officer.Body.Resume(officer.Ragdoll.BeginGetUp() ? PolicePose.LevantarseEspalda : PolicePose.LevantarseBoca);
                return;
            }
            if (officer.SuspectAtLarge) officer.Change(new ChaseState());
            else officer.Change(new SearchState());
        }
    }

    // Se aleja caminando y avisa que terminó; si en el camino ve a alguien buscado, vuelve a perseguir.
    public sealed class LeaveState : PoliceState
    {
        private float left;

        public override void Enter(PoliceOfficer officer)
        {
            left = officer.Settings.LeaveSeconds;
            officer.Body.Show(PolicePose.Caminar);
        }

        public override void Tick(PoliceOfficer officer, float dt)
        {
            if (officer.SuspectVisible && officer.SuspectAtLarge) { officer.Change(new ChaseState()); return; }
            officer.Motor.MoveAwayFrom(officer.LastKnown, officer.Settings.WalkSpeed);
            left -= dt;
            if (left <= 0f) officer.Finish();
        }
    }
}
