using System.Collections.Generic;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;
using Alarma.AI.CityLife;

namespace Alarma.AI.Reactions
{
    public enum ReactionState { Cowering, Surrendered, OfferingWrists, Tied, Fleeing, Recording, Stunned, GettingUp, Leaving }

    // Cerebro del doble de reacción de un civil (Task 13 y parte de Task 18), con una máquina de estados:
    // - Oye un disparo o el grito de alguien a quien le apuntan: pierde valentía; si queda con poca se agacha pidiendo
    //   piedad, si no huye corriendo. Algunos, si están lejos, se quedan grabando con el celular y llaman a la
    //   policía: al terminar la llamada avisan por el canal de denuncias y huyen. Apuntarles o acercarse la corta.
    // - Le apuntan de frente: se arrodilla con las manos atrás y la cabeza gacha; de espaldas: huye. Si dejan de
    //   apuntarle, a los pocos segundos se levanta y escapa; antes si quien le apuntaba guardó el arma.
    // - Arrodillado o agachado acepta las bridas: junta las muñecas en la espalda, quien lo amarra se pone detrás y
    //   queda amarrado.
    // - Un disparo o el táser lo tumban con física (NpcRagdoll); aturdido un rato, se levanta y se va.
    // - Huir: si está dentro de un local sigue un camino por sus pasillos hasta la puerta y la calle, rodeando a la
    //   amenaza (ShopEscape), y recién ahí se aleja; si la amenaza tapa la salida, se aleja por dentro.
    // Percepción (ruido, mira, golpes), decisión (aquí), movimiento (NpcFleeMotor), postura (NpcReactionAnimator) y
    // caída (NpcRagdoll) están separados.
    public sealed class NpcReactions : MonoBehaviour, IIntimidatable, IDamageable, IItemTarget, IUseAnchor
    {
        private const string ZipTies = "bridas", Taser = "taser";
        private const float OfferSeconds = 4f, LeaveSeconds = 25f;
        [SerializeField] private NpcReactionSettings settings;
        [SerializeField] private NoiseChannel noise;
        [SerializeField] private NpcReactionAnimator body;
        [SerializeField] private NpcFleeMotor motor;
        [SerializeField] private NpcRagdoll ragdoll;
        [SerializeField] private CrimeReportChannel reports;
        [SerializeField] private WitnessPhone phone;
        private readonly HashSet<GameObject> aimers = new HashSet<GameObject>();
        private NpcBravery bravery;
        private Transform threat;
        private Vector3 threatPoint;
        private float timer, call;
        private bool reported;
        private IArmed armedThreat;
        private ShopDoor exitDoor;
        private bool tiedBeforeFall;

        public ReactionState State { get; private set; } = ReactionState.Leaving;

        public void Configure(NpcReactionSettings reactionSettings, NoiseChannel channel, NpcReactionAnimator animatorDriver, NpcFleeMotor flee, NpcRagdoll fall,
            CrimeReportChannel crimeReports, WitnessPhone witnessPhone)
        {
            settings = reactionSettings; noise = channel; body = animatorDriver; motor = flee; ragdoll = fall;
            reports = crimeReports; phone = witnessPhone;
        }

        private void Awake() => bravery = new NpcBravery(Random.Range(settings.BraveryRange.x, settings.BraveryRange.y), settings.CowerBelow);
        private void OnEnable() { if (noise != null) noise.Raised += Hear; }
        private void OnDisable() { if (noise != null) noise.Raised -= Hear; }

        // Copia la pose del civil que reemplaza (mismos huesos por nombre) para que el cambio no se note.
        public void CopyPose(Transform original)
        {
            var source = new Dictionary<string, Transform>();
            foreach (var t in original.GetComponentsInChildren<Transform>(true)) source[t.name] = t;
            foreach (var t in body.Body.GetComponentsInChildren<Transform>(true))
                if (t != body.Body.transform && source.TryGetValue(t.name, out var match)) t.SetPositionAndRotation(match.position, match.rotation);
        }

        // ---- Percepción ----

        public void Hear(NoiseEvent sound)
        {
            float distance = Vector3.Distance(sound.Position, transform.position);
            float radius = NoiseReach.RadiusAt(sound, transform.position); // con una pared en medio llega menos o nada
            if (distance > radius || State == ReactionState.Tied || State == ReactionState.Stunned || State == ReactionState.GettingUp) return;
            bravery.Frighten(NpcBravery.FearAt(distance, radius, sound.Kind == NoiseKind.Scream ? settings.AimFear : settings.GunshotFear));
            threatPoint = sound.Position;
            if (sound.Source != null) threat = sound.Source.transform;
            if (State == ReactionState.Surrendered || State == ReactionState.OfferingWrists) return; // ya está rendido
            if (State == ReactionState.Fleeing) { timer = settings.FleeSeconds; return; }
            if (State == ReactionState.Recording) return; // sigue grabando
            // Testigo: no se acobardó, está lejos y todavía no denunció. Graba y llama en vez de huir.
            bool films = !reported && distance >= settings.WitnessMinDistance && Random.value < settings.WitnessChance;
            // Ver que le apuntan a otro no paraliza a nadie: todos corren (o graban de lejos). Agacharse suplicando queda
            // para los disparos.
            bool freezes = sound.Kind != NoiseKind.Scream && bravery.Cowers;
            Enter(freezes ? ReactionState.Cowering : films ? ReactionState.Recording : ReactionState.Fleeing);
        }

        public void BeginIntimidation(GameObject instigator)
        {
            if (instigator == null || !aimers.Add(instigator)) return;
            threat = instigator.transform;
            threatPoint = threat.position;
            armedThreat = instigator.GetComponentInParent<IArmed>();
            bravery.Frighten(settings.AimFear);
            if (State == ReactionState.Tied || State == ReactionState.Stunned || State == ReactionState.GettingUp
                || State == ReactionState.OfferingWrists || State == ReactionState.Surrendered) return;
            Vector3 toAimer = instigator.transform.position - transform.position;
            toAimer.y = 0f;
            bool front = Vector3.Angle(transform.forward, toAimer) <= settings.FrontAngle;
            // De frente o ya agachado: se arrodilla mirando a quien le apunta. De espaldas: sale corriendo.
            if (front || State == ReactionState.Cowering)
            {
                if (toAimer.sqrMagnitude > .01f) transform.rotation = Quaternion.LookRotation(toAimer);
                Enter(ReactionState.Surrendered);
            }
            else Enter(ReactionState.Fleeing);
            // Grita: los civiles cercanos se enteran (huyen, se agachan o graban).
            if (noise != null) noise.Raise(transform.position, settings.AimAlarmRadius, NoiseKind.Scream, instigator);
        }

        public void EndIntimidation(GameObject instigator)
        {
            if (!aimers.Remove(instigator) || aimers.Count > 0) return;
            if (State == ReactionState.Surrendered) timer = settings.SurrenderSeconds;
        }

        public void TakeDamage(float amount, GameObject instigator) => Stun(instigator, settings.HitImpulse, settings.StunSeconds);

        public bool Accepts(string itemId)
            => itemId == Taser ? State != ReactionState.Stunned
             : itemId == ZipTies && (State == ReactionState.Surrendered || State == ReactionState.Cowering || State == ReactionState.OfferingWrists);

        public string UseItem(string itemId, GameObject user)
        {
            if (!Accepts(itemId)) return itemId == ZipTies ? "Tiene que estar rendido para amarrarlo" : "";
            if (itemId == Taser) { Stun(user, settings.HitImpulse * .3f, settings.TaserSeconds); return "Aturdido con el táser"; }
            Enter(ReactionState.Tied);
            return "Amarrado";
        }

        // Antes de amarrarlo: lleva las manos a la espalda y pide que lo amarren desde atrás, mirando hacia donde mira él.
        public bool PrepareUse(string itemId, GameObject user, out Pose standAt)
        {
            standAt = default;
            if (itemId != ZipTies || !Accepts(itemId)) return false;
            standAt = new Pose(transform.position - transform.forward * settings.TieDistance, transform.rotation);
            Enter(ReactionState.OfferingWrists);
            return true;
        }

        // ---- Decisión ----

        private void Stun(GameObject instigator, float impulse, Vector2 seconds)
        {
            if (State != ReactionState.Stunned) tiedBeforeFall = State == ReactionState.Tied;
            Vector3 from = instigator != null ? instigator.transform.position : transform.position - transform.forward;
            Vector3 push = transform.position - from;
            push.y = 0f;
            Vector3 hit = transform.position + Vector3.up * 1.2f;
            motor.Stop();
            if (phone != null) phone.Hide();
            ragdoll.Fall((push.sqrMagnitude > .001f ? push.normalized : -transform.forward) * impulse + Vector3.up * impulse * .15f, hit);
            if (instigator != null) threat = instigator.transform;
            aimers.Clear();
            State = ReactionState.Stunned;
            timer = Random.Range(seconds.x, seconds.y);
        }

        // Empieza a correr: dentro de un local, primero por un camino hasta la calle que no pase junto a la amenaza.
        private void RunAway()
        {
            exitDoor = null;
            if (ShopEscape.TryFind(transform.position, ThreatPosition, out var route, out var door))
            {
                exitDoor = door;
                motor.MoveThrough(route, ThreatPosition, settings.RunSpeed);
            }
            else motor.MoveAwayFrom(ThreatPosition, settings.RunSpeed);
        }

        private void Face(Vector3 point, float dt)
        {
            Vector3 to = point - transform.position;
            to.y = 0f;
            if (to.sqrMagnitude > .01f) transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(to), 240f * dt);
        }

        private void Enter(ReactionState next)
        {
            if (State == ReactionState.Recording && next != ReactionState.Recording && phone != null) phone.Hide();
            State = next;
            switch (next)
            {
                case ReactionState.Cowering:
                    motor.Stop(); body.Show(ReactionPose.Suplicar);
                    timer = Random.Range(settings.CowerSeconds.x, settings.CowerSeconds.y);
                    break;
                case ReactionState.Surrendered:
                    motor.Stop(); body.Show(ReactionPose.Rendido);
                    timer = aimers.Count > 0 ? float.PositiveInfinity : settings.SurrenderSeconds; // mientras le apunten, espera
                    break;
                case ReactionState.OfferingWrists:
                case ReactionState.Tied:
                    motor.Stop(); body.Show(ReactionPose.Amarrado); timer = OfferSeconds;
                    break;
                case ReactionState.Fleeing:
                    RunAway(); body.Show(ReactionPose.Correr); timer = settings.FleeSeconds;
                    break;
                case ReactionState.Recording:
                    motor.Stop(); body.Show(ReactionPose.Grabar); call = 0f; timer = float.PositiveInfinity;
                    break;
                case ReactionState.Leaving:
                    motor.MoveAwayFrom(ThreatPosition, settings.WalkSpeed); body.Show(ReactionPose.Caminar); timer = LeaveSeconds;
                    break;
            }
        }

        private Vector3 ThreatPosition => threat != null ? threat.position : threatPoint;

        private void Update()
        {
            float dt = Time.deltaTime;
            timer -= dt;
            switch (State)
            {
                case ReactionState.Cowering:
                    if (timer <= 0f) Enter(bravery.Cowers && Near(12f) ? ReactionState.Cowering : ReactionState.Leaving);
                    break;
                case ReactionState.Surrendered:
                    if (aimers.Count > 0) break;
                    bravery.Recover(settings.BraveryRecovery * dt);
                    // Ya no le apuntan: espera y escapa. Si el arma ya no está a la vista, le basta con menos espera.
                    bool armed = armedThreat != null && armedThreat.WeaponDrawn;
                    if (timer <= (armed ? 0f : settings.SurrenderSeconds - settings.SurrenderSecondsUnarmed)) Enter(ReactionState.Fleeing);
                    break;
                case ReactionState.OfferingWrists:
                    if (timer <= 0f) Enter(ReactionState.Surrendered); // nadie lo amarró
                    break;
                case ReactionState.Fleeing:
                    motor.MoveAwayFrom(ThreatPosition, settings.RunSpeed);
                    if (exitDoor != null) exitDoor.PushFrom(transform.position); // abre la puerta al llegar
                    if (timer <= 0f) Enter(ReactionState.Leaving);
                    break;
                case ReactionState.Recording:
                    Face(ThreatPosition, dt);
                    if (Near(settings.WitnessMinDistance * .5f)) { Enter(ReactionState.Fleeing); break; } // la amenaza se le viene encima: corta y corre
                    call += dt / settings.CallSeconds;
                    if (phone != null) phone.Show(call);
                    if (call < 1f) break;
                    reported = true;
                    if (reports != null) reports.Raise(ThreatPosition, gameObject);
                    Enter(ReactionState.Fleeing);
                    break;
                case ReactionState.Stunned:
                    if (timer > 0f) break;
                    State = ReactionState.GettingUp;
                    timer = settings.GetUpSeconds;
                    body.Resume(ragdoll.BeginGetUp() ? ReactionPose.LevantarseEspalda : ReactionPose.LevantarseBoca);
                    break;
                case ReactionState.GettingUp:
                    if (timer <= 0f) Enter(tiedBeforeFall ? ReactionState.Tied : ReactionState.Leaving);
                    break;
                case ReactionState.Leaving:
                    if (exitDoor != null) exitDoor.PushFrom(transform.position);
                    if (timer <= 0f || !Near(settings.DespawnDistance)) Destroy(gameObject);
                    break;
                case ReactionState.Tied:
                    if (!Near(settings.DespawnDistance * 1.5f)) Destroy(gameObject);
                    break;
            }
        }

        private bool Near(float meters) => threat != null && (threat.position - transform.position).sqrMagnitude < meters * meters;
    }
}
