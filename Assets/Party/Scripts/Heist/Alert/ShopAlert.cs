using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;

namespace Alarma.Heist.Alert
{
    // Alerta de un local en la escena (Task 15): junta la sospecha de lo que vigila dentro (ISuspicionSource: las
    // cámaras), oye las denuncias hechas en el local y el estado de la policía, se lo pasa a la máquina de alerta y
    // publica el resultado por AlertChannel. No conoce cámaras, policía ni interfaz. Con red, corre solo en el host.
    public sealed class ShopAlert : MonoBehaviour
    {
        private const float Step = .01f;
        [SerializeField] private AlertSettings settings;
        [SerializeField] private CrimeReportChannel reports;
        [SerializeField] private PoliceResponseChannel response;
        [SerializeField] private AlertChannel alerts;
        [SerializeField, Tooltip("Radio del local en metros, desde su centro.")] private float radius = 12f;
        private ISuspicionSource[] sources;
        private AlertMachine machine;
        private float shown;

        public AlertLevel Level => machine != null ? machine.Level : AlertLevel.Stealth;

        public void Configure(AlertSettings alertSettings, CrimeReportChannel crimeReports, PoliceResponseChannel policeResponse, AlertChannel alertChannel, float shopRadius)
        {
            settings = alertSettings; reports = crimeReports; response = policeResponse; alerts = alertChannel; radius = shopRadius;
        }

        private void Awake()
        {
            sources = GetComponentsInChildren<ISuspicionSource>(true);
            machine = new AlertMachine(settings.AlarmSeconds, settings.CalmSeconds);
            machine.LevelChanged += _ => Publish();
        }

        private void OnEnable()
        {
            if (reports != null) reports.Raised += OnReport;
            if (response != null) response.Raised += OnPolice;
        }

        private void OnDisable()
        {
            if (reports != null) reports.Raised -= OnReport;
            if (response != null) response.Raised -= OnPolice;
            machine.Reset();
            Publish();
        }

        private void Update()
        {
            float highest = 0f;
            foreach (var source in sources) highest = Mathf.Max(highest, source.Suspicion);
            machine.Tick(highest, Time.deltaTime);
            // Publica solo cuando el valor cambió lo suficiente para verse en el medidor, o llegó a un extremo.
            float value = machine.Suspicion;
            if (Mathf.Abs(value - shown) >= Step || (value != shown && (value <= 0f || value >= 1f))) Publish();
        }

        private void OnReport(CrimeReport report)
        {
            Vector3 to = report.Position - transform.position;
            to.y = 0f;
            float reach = radius + settings.Margin;
            if (to.sqrMagnitude <= reach * reach) machine.Report();
        }

        private void OnPolice(PoliceResponse state) => machine.PoliceUpdate(state.Phase);

        private void Publish()
        {
            shown = machine.Suspicion;
            if (alerts != null) alerts.Raise(gameObject, machine.Level, shown);
        }
    }
}
