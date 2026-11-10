using System.Collections.Generic;
using UnityEngine;

namespace Alarma.Police
{
    // Reserva de agentes (patrones Factory y Object Pool): crea un agente solo cuando no hay uno libre (Create es la
    // fábrica) y los reutiliza en vez de destruirlos, para no pagar la creación en plena persecución.
    public sealed class PoliceOfficerPool : MonoBehaviour
    {
        [SerializeField] private PoliceOfficer prefab;
        private readonly Stack<PoliceOfficer> idle = new Stack<PoliceOfficer>();
        private int created;

        public void Configure(PoliceOfficer officerPrefab) => prefab = officerPrefab;

        public PoliceOfficer Get(Vector3 position, Quaternion rotation)
        {
            var officer = idle.Count > 0 ? idle.Pop() : Create();
            officer.transform.SetPositionAndRotation(position, rotation);
            officer.gameObject.SetActive(true);
            return officer;
        }

        public void Release(PoliceOfficer officer)
        {
            officer.gameObject.SetActive(false);
            idle.Push(officer);
        }

        private PoliceOfficer Create()
        {
            var officer = Instantiate(prefab, transform);
            officer.name = "Agente " + ++created;
            officer.gameObject.SetActive(false);
            return officer;
        }
    }
}
