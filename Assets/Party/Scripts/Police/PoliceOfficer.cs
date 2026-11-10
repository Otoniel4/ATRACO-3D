using System;
using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.Core.Contracts;
using Alarma.Core.Sets;

namespace Alarma.Police
{
    // Agente de policía a pie (Task 19). Es el contexto del patrón State: guarda el estado actual (PoliceStates.cs:
    // llegar, buscar, perseguir, apuntar, arrestar, caído, retirarse) y le ofrece lo que necesita: la percepción (a quién
    // ve), el movimiento (NpcFleeMotor), la postura (PoliceAnimator), la pistola (PoliceSidearm) y la caída (NpcRagdoll).
    // Encuentra a los sospechosos por el conjunto SuspectSet y los trata por sus interfaces (IDetectable, IArrestable):
    // no conoce al jugador. Con red, todo esto corre solo en el host.
    public sealed class PoliceOfficer : MonoBehaviour, IDamageable
    {
        private const int WorldMask = ~((1 << 29) | (1 << 30) | (1 << 31)); // lo que tapa la vista: todo menos personajes e interfaz
        private const float EyeHeight = 1.6f, LookInterval = .2f;
        [SerializeField] private PoliceSettings settings;
        [SerializeField] private NpcFleeMotor motor;
        [SerializeField] private PoliceAnimator body;
        [SerializeField] private NpcRagdoll ragdoll;
        [SerializeField] private PoliceSidearm sidearm;
        [SerializeField] private SuspectSet suspects;
        private PoliceState state;
        private IDetectable detectable;
        private float nextLook;

        public PoliceSettings Settings => settings;
        public NpcFleeMotor Motor => motor;
        public PoliceAnimator Body => body;
        public NpcRagdoll Ragdoll => ragdoll;
        public PoliceSidearm Sidearm => sidearm;
        // Sospechoso que persigue (el último que vio) y si lo está viendo ahora.
        public GameObject Suspect { get; private set; }
        public IArrestable Arrestable { get; private set; }
        public bool SuspectVisible { get; private set; }
        public Vector3 LastKnown { get; private set; }
        // Terminó su trabajo (arrestó o se cansó de buscar): la central lo devuelve a la reserva.
        public event Action<PoliceOfficer> Finished;

        public void Configure(PoliceSettings policeSettings, NpcFleeMotor movement, PoliceAnimator poses, NpcRagdoll fall, PoliceSidearm pistol, SuspectSet set)
        {
            settings = policeSettings; motor = movement; body = poses; ragdoll = fall; sidearm = pistol; suspects = set;
        }

        // Sale hacia el lugar de la denuncia.
        public void Dispatch(Vector3 reported)
        {
            SetSuspect(null);
            LastKnown = reported;
            Change(new ArriveState());
        }

        // Otra denuncia mientras trabaja: si no está viendo a nadie, va al lugar nuevo.
        public void Report(Vector3 position) { if (!SuspectVisible) LastKnown = position; }

        public void Change(PoliceState next)
        {
            state?.Exit(this);
            state = next;
            state.Enter(this);
        }

        public void Finish()
        {
            state?.Exit(this);
            state = null;
            motor.Stop();
            sidearm.Holster();
            Finished?.Invoke(this);
        }

        // Un disparo lo tumba (caída cómica) desde cualquier estado; en el suelo no recibe más.
        public void TakeDamage(float amount, GameObject instigator)
        {
            if (state == null || state is DownState) return;
            Change(new DownState(instigator != null ? instigator.transform.position : transform.position - transform.forward));
        }

        private void Update()
        {
            if (state == null) return;
            if (Time.time >= nextLook) { nextLook = Time.time + LookInterval; Look(); }
            state.Tick(this, Time.deltaTime);
        }

        // ---- Percepción ----

        // Sigue al que ya perseguía si lo ve; si no, al más cercano que vea.
        private void Look()
        {
            if (detectable != null && Sees(detectable)) { SuspectVisible = true; LastKnown = Suspect.transform.position; return; }
            SuspectVisible = false;
            float best = float.PositiveInfinity;
            GameObject found = null;
            if (suspects != null)
                foreach (var candidate in suspects.Items)
                {
                    if (candidate == null) continue;
                    var seen = candidate.GetComponent<IDetectable>();
                    float distance = (candidate.transform.position - transform.position).sqrMagnitude;
                    if (seen == null || distance >= best || !Sees(seen)) continue;
                    best = distance; found = candidate;
                }
            if (found == null) return;
            SetSuspect(found);
            SuspectVisible = true;
            LastKnown = found.transform.position;
        }

        private bool Sees(IDetectable target)
        {
            if (!target.IsDetectable) return false;
            Vector3 eye = transform.position + Vector3.up * EyeHeight, point = target.DetectionPoint.position;
            return (point - eye).sqrMagnitude <= settings.SightRange * settings.SightRange
                   && !Physics.Linecast(eye, point, WorldMask, QueryTriggerInteraction.Ignore);
        }

        private void SetSuspect(GameObject suspect)
        {
            Suspect = suspect;
            detectable = suspect != null ? suspect.GetComponent<IDetectable>() : null;
            Arrestable = suspect != null ? suspect.GetComponent<IArrestable>() : null;
            SuspectVisible = false;
        }

        // Sigue habiendo a quién buscar (no arrestado) y, si persigue a alguien, todavía se lo puede detectar.
        public bool SuspectAtLarge => detectable != null && Suspect != null && detectable.IsDetectable;
        public bool AnyoneAtLarge
        {
            get
            {
                if (suspects == null) return false;
                foreach (var candidate in suspects.Items)
                {
                    var seen = candidate != null ? candidate.GetComponent<IDetectable>() : null;
                    if (seen != null && seen.IsDetectable) return true;
                }
                return false;
            }
        }
        // Adónde apuntar: el pecho del sospechoso.
        public Vector3 AimPoint => detectable != null ? detectable.DetectionPoint.position : LastKnown + Vector3.up * 1.2f;

        // ---- Ayudas para los estados ----

        public float DistanceTo(Vector3 point)
        {
            Vector3 gap = point - transform.position;
            gap.y = 0f;
            return gap.magnitude;
        }

        public void Face(Vector3 point, float dt)
        {
            Vector3 to = point - transform.position;
            to.y = 0f;
            if (to.sqrMagnitude > .01f) transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(to), 360f * dt);
        }

    }
}
