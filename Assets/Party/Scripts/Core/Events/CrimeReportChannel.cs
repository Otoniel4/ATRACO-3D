using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    // Una denuncia: dónde está la amenaza y quién llamó.
    public readonly struct CrimeReport
    {
        public readonly Vector3 Position;
        public readonly GameObject Witness;

        public CrimeReport(Vector3 position, GameObject witness) { Position = position; Witness = witness; }
    }

    // Canal de denuncias (patrón Observer con ScriptableObject): los testigos avisan cuando terminan de llamar a la
    // policía y quien escucha (el aviso en pantalla y, más adelante, la policía y el nivel de búsqueda) reacciona.
    [CreateAssetMenu(menuName = "Alarma/Eventos/Canal de denuncias", fileName = "Denuncias")]
    public sealed class CrimeReportChannel : ScriptableObject
    {
        public event Action<CrimeReport> Raised;

        public void Raise(Vector3 position, GameObject witness) => Raised?.Invoke(new CrimeReport(position, witness));
    }
}
