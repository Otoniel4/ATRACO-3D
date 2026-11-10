using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.Core.Contracts;
using Alarma.Core.Events;
using Alarma.Core.Sets;

namespace Alarma.AI.Security
{
    // Guardia de un local (Task 14): cuida su puesto y, si ve a alguien con un arma en la mano o hay disparos o gritos
    // cerca, lo persigue y le pega con la porra; nunca dispara. Es el contexto del patrón State (GuardStates.cs: en el
    // puesto, perseguir, golpear, caído, volver). Encuentra a los sospechosos por SuspectSet y los trata por sus
    // interfaces (IDetectable, IArmed, IDamageable, IArrestable). Si un disparo lo deja inconsciente, su radio avisa a
    // la policía por el canal de denuncias. Con red, corre solo en el host.
    public sealed class SecurityGuard : MonoBehaviour, IDamageable
    {
        private const float LookInterval = .25f, EyeHeight = 1.6f;
        [SerializeField] private GuardSettings settings;
        [SerializeField] private NpcFleeMotor motor;
        [SerializeField] private GuardBody body;
        [SerializeField] private NpcRagdoll ragdoll;
        [SerializeField] private SentryLook sentry;
        [SerializeField] private SuspectSet suspects;
        [SerializeField] private NoiseChannel noise;
        [SerializeField] private CrimeReportChannel reports;
        private GuardState state;
        private IDetectable detectable;
        private float nextLook;

        public GuardSettings Settings => settings;
        public NpcFleeMotor Motor => motor;
        public GuardBody Body => body;
        public NpcRagdoll Ragdoll => ragdoll;
        public SentryLook Sentry => sentry;
        public Vector3 Post { get; private set; }
        public Quaternion PostFacing { get; private set; }
        public GameObject Suspect { get; private set; }
        public IDamageable Victim { get; private set; }
        public IArrestable Arrestable { get; private set; }

        public void Configure(GuardSettings guardSettings, NpcFleeMotor movement, GuardBody visual, NpcRagdoll fall, SentryLook look,
            SuspectSet set, NoiseChannel noiseChannel, CrimeReportChannel crimeReports)
        {
            settings = guardSettings; motor = movement; body = visual; ragdoll = fall; sentry = look; suspects = set; noise = noiseChannel; reports = crimeReports;
        }

        private void Start()
        {
            Post = transform.position;
            PostFacing = transform.rotation;
            Change(new PostState());
        }

        private void OnEnable() { if (noise != null) noise.Raised += Hear; }
        private void OnDisable() { if (noise != null) noise.Raised -= Hear; }

        public void Change(GuardState next)
        {
            state?.Exit(this);
            state = next;
            state.Enter(this);
        }

        private void Update()
        {
            if (state == null) return;
            if (state.Watches && Time.time >= nextLook) { nextLook = Time.time + LookInterval; Watch(); }
            state.Tick(this, Time.deltaTime);
        }

        // Un disparo lo deja inconsciente; en el suelo no recibe más.
        public void TakeDamage(float amount, GameObject instigator)
        {
            if (state == null || state is GuardDownState) return;
            if (instigator != null && instigator.GetComponent<IDetectable>() != null) Engage(instigator);
            if (reports != null) reports.Raise(transform.position, gameObject, CrimeReportSource.Guard); // el radio avisa: guardia caído
            Change(new GuardDownState(instigator != null ? instigator.transform.position : transform.position - transform.forward));
        }

        // ---- Percepción ----

        // En el puesto: a quien vea con un arma en la mano, lo enfrenta.
        private void Watch()
        {
            if (suspects == null) return;
            foreach (var candidate in suspects.Items)
            {
                if (candidate == null) continue;
                var armed = candidate.GetComponent<IArmed>();
                var seen = candidate.GetComponent<IDetectable>();
                if (armed == null || !armed.WeaponDrawn || seen == null || !seen.IsDetectable) continue;
                Vector3 eye = transform.position + Vector3.up * EyeHeight, point = seen.DetectionPoint.position;
                if ((point - eye).sqrMagnitude > settings.SightRange * settings.SightRange || !Sightline.Clear(eye, point)) continue;
                Engage(candidate);
                Change(new GuardChaseState());
                return;
            }
        }

        // Disparos y gritos cerca de su puesto: va por quien los causó.
        private void Hear(NoiseEvent sound)
        {
            if (state == null || !state.Watches || sound.Source == null) return;
            if ((sound.Position - Post).sqrMagnitude > settings.HearRange * settings.HearRange) return;
            var seen = sound.Source.GetComponent<IDetectable>();
            if (seen == null || !seen.IsDetectable) return; // un agente de policía disparando no es un sospechoso
            Engage(sound.Source);
            Change(new GuardChaseState());
        }

        private void Engage(GameObject suspect)
        {
            Suspect = suspect;
            detectable = suspect.GetComponent<IDetectable>();
            Victim = suspect.GetComponent<IDamageable>();
            Arrestable = suspect.GetComponent<IArrestable>();
        }

        // Sigue habiendo a quién enfrentar: detectable, de pie y sin haberse ido demasiado lejos del local.
        public bool SuspectActive
            => Suspect != null && detectable != null && detectable.IsDetectable && !(Arrestable != null && Arrestable.CanBeArrested)
               && (Suspect.transform.position - Post).sqrMagnitude <= settings.LeashDistance * settings.LeashDistance;

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
            if (to.sqrMagnitude > .01f) transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(to), 420f * dt);
        }

    }
}
