using UnityEngine;
using Alarma.AI.Reactions;
using Alarma.Core.Contracts;
using Alarma.Core.Events;
using Alarma.Core.Sets;

namespace Alarma.AI.Security
{
    // Cámara de seguridad de un local (Task 15): barre de lado a lado y, si dentro de su cono ve a alguien con un arma
    // en la mano (IArmed, con línea de visión), lo sigue y va llenando su sospecha; al completarse avisa por el canal de
    // denuncias, que oyen la policía y la interfaz. La luz del cono muestra qué mira y cuánto sospecha: verde, amarillo,
    // rojo. Encuentra a los sospechosos por SuspectSet, igual que guardias y policías. Con red, decide solo el host.
    public sealed class SecurityCamera : MonoBehaviour, ISuspicionSource
    {
        private const float LookInterval = .2f;
        private static readonly Color Calm = new Color(.3f, 1f, .45f), Alert = new Color(1f, .25f, .2f), Wary = new Color(1f, .85f, .25f);
        [SerializeField] private SecurityCameraSettings settings;
        [SerializeField, Tooltip("Parte que gira (el lente mira hacia su +Z).")] private Transform head;
        [SerializeField, Tooltip("Luz del cono de visión.")] private Light beam;
        [SerializeField] private SuspectSet suspects;
        [SerializeField] private CrimeReportChannel reports;
        private Quaternion rest;
        private Transform watched;
        private float suspicion, phase, nextLook, nextReport;

        // Sospecha de 0 a 1: la lee la alerta del local (ShopAlert) por ISuspicionSource.
        public float Suspicion => suspicion;

        public void Configure(SecurityCameraSettings cameraSettings, Transform turningHead, Light cone, SuspectSet set, CrimeReportChannel crimeReports)
        {
            settings = cameraSettings; head = turningHead; beam = cone; suspects = set; reports = crimeReports;
        }

        private void Awake()
        {
            rest = head.localRotation;
            phase = Random.value * settings.Period;
            if (beam != null) { beam.range = settings.Range; beam.spotAngle = settings.HalfAngle * 2f; }
        }

        private void Update()
        {
            if (Time.time >= nextLook) { nextLook = Time.time + LookInterval; watched = Find(); }
            float dt = Time.deltaTime;
            suspicion = Mathf.Clamp01(suspicion + (watched != null ? dt / settings.DetectSeconds : -dt / settings.ForgetSeconds));
            if (watched != null)
            {
                // Lo sigue con el lente en vez de seguir barriendo.
                Vector3 to = watched.position - head.position;
                if (to.sqrMagnitude > .01f) head.rotation = Quaternion.RotateTowards(head.rotation, Quaternion.LookRotation(to), 90f * dt);
                if (suspicion >= 1f && Time.time >= nextReport)
                {
                    nextReport = Time.time + settings.ReportCooldown;
                    if (reports != null) reports.Raise(watched.position, gameObject, CrimeReportSource.Camera);
                }
            }
            else
            {
                float turn = Mathf.Sin((Time.time + phase) / settings.Period * Mathf.PI * 2f) * settings.Sweep;
                // El giro es alrededor de la vertical del mundo aunque el lente mire inclinado hacia abajo.
                Quaternion sweep = head.parent.rotation * Quaternion.Euler(0f, turn, 0f) * rest;
                head.rotation = Quaternion.RotateTowards(head.rotation, sweep, 60f * dt);
            }
            if (beam != null) beam.color = suspicion < .5f ? Color.Lerp(Calm, Wary, suspicion * 2f) : Color.Lerp(Wary, Alert, suspicion * 2f - 1f);
        }

        // El punto del cuerpo del primer sospechoso armado que cae dentro del cono, a la vista.
        private Transform Find()
        {
            if (suspects == null) return null;
            foreach (var candidate in suspects.Items)
            {
                if (candidate == null) continue;
                var armed = candidate.GetComponent<IArmed>();
                var seen = candidate.GetComponent<IDetectable>();
                if (armed == null || !armed.WeaponDrawn || seen == null || !seen.IsDetectable) continue;
                Vector3 to = seen.DetectionPoint.position - head.position;
                // Mientras lo sigue, el cono es un poco más ancho: no lo pierde por un paso al costado.
                float angle = settings.HalfAngle * (watched != null ? 1.3f : 1f);
                if (to.sqrMagnitude > settings.Range * settings.Range || Vector3.Angle(head.forward, to) > angle) continue;
                if (Sightline.Clear(head.position, seen.DetectionPoint.position)) return seen.DetectionPoint;
            }
            return null;
        }
    }
}
