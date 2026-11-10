using System.Collections.Generic;
using UnityEngine;
using Alarma.Core.Events;

namespace Alarma.Police
{
    // Central de policía: oye las denuncias (CrimeReportChannel), cuenta regresiva, y al terminar saca agentes de la
    // reserva y los hace aparecer en la calle cerca del lugar, fuera de la vista si puede. Avisa cada paso por
    // PoliceResponseChannel (la interfaz escucha). Cuando todos terminan, los devuelve a la reserva.
    // Con red, la central vive solo en el host.
    public sealed class PoliceDispatcher : MonoBehaviour
    {
        private const int WorldMask = ~((1 << 29) | (1 << 30) | (1 << 31));
        private const int Tries = 16;
        [SerializeField] private CrimeReportChannel reports;
        [SerializeField] private PoliceResponseChannel response;
        [SerializeField] private PoliceSettings settings;
        [SerializeField] private PoliceOfficerPool pool;
        private readonly List<PoliceOfficer> active = new List<PoliceOfficer>();
        private Vector3 scene;
        private float countdown = -1f;
        private int shown;

        public void Configure(CrimeReportChannel crimeReports, PoliceResponseChannel responseChannel, PoliceSettings policeSettings, PoliceOfficerPool officerPool)
        {
            reports = crimeReports; response = responseChannel; settings = policeSettings; pool = officerPool;
        }

        private void OnEnable() { if (reports != null) reports.Raised += OnReport; }
        private void OnDisable() { if (reports != null) reports.Raised -= OnReport; }

        private void OnReport(CrimeReport report)
        {
            scene = report.Position;
            if (active.Count > 0) { foreach (var officer in active) officer.Report(scene); return; } // ya están en la zona
            if (countdown >= 0f) return; // ya vienen
            countdown = settings.ResponseSeconds;
            shown = int.MaxValue;
        }

        private void Update()
        {
            if (countdown < 0f) return;
            countdown -= Time.deltaTime;
            int seconds = Mathf.CeilToInt(countdown);
            if (seconds != shown && seconds > 0) { shown = seconds; Announce(PoliceResponsePhase.OnTheWay, seconds); }
            if (countdown > 0f) return;
            countdown = -1f;
            Deploy();
        }

        private void Deploy()
        {
            for (int i = 0; i < settings.Officers; i++)
            {
                Vector3 spot = SpawnPoint();
                Vector3 toScene = scene - spot;
                toScene.y = 0f;
                var officer = pool.Get(spot, toScene.sqrMagnitude > .01f ? Quaternion.LookRotation(toScene) : Quaternion.identity);
                officer.Finished += OnFinished;
                active.Add(officer);
                officer.Dispatch(scene);
            }
            Announce(PoliceResponsePhase.OnScene);
        }

        private void OnFinished(PoliceOfficer officer)
        {
            officer.Finished -= OnFinished;
            active.Remove(officer);
            pool.Release(officer);
            if (active.Count == 0) Announce(PoliceResponsePhase.Withdrawn);
        }

        private void Announce(PoliceResponsePhase phase, int seconds = 0) { if (response != null) response.Raise(phase, seconds); }

        // Un punto en la calle alrededor del lugar: a nivel del suelo (un techo o un toldo no sirve), con espacio para una
        // persona y, si se puede, sin vista directa al lugar.
        private Vector3 SpawnPoint()
        {
            Vector3 fallback = scene;
            float start = Random.value * 360f;
            for (int i = 0; i < Tries; i++)
            {
                float distance = Random.Range(settings.SpawnDistance.x, settings.SpawnDistance.y);
                Vector3 around = scene + Quaternion.Euler(0f, start + i * (360f / Tries), 0f) * Vector3.forward * distance;
                if (!Physics.Raycast(around + Vector3.up * 40f, Vector3.down, out var ground, 60f, WorldMask, QueryTriggerInteraction.Ignore)) continue;
                if (Mathf.Abs(ground.point.y - scene.y) > 1.2f) continue;
                Vector3 foot = ground.point;
                if (Physics.CheckCapsule(foot + Vector3.up * .5f, foot + Vector3.up * 1.5f, .35f, WorldMask, QueryTriggerInteraction.Ignore)) continue;
                if (Physics.Linecast(foot + Vector3.up * 1.5f, scene + Vector3.up * 1.5f, WorldMask, QueryTriggerInteraction.Ignore)) return foot;
                fallback = foot;
            }
            return fallback;
        }
    }
}
