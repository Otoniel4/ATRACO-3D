using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    // Quién da el aviso: un testigo con su celular, una cámara de seguridad o el radio de un guardia caído.
    public enum CrimeReportSource { Witness, Camera, Guard }

    // Una denuncia: dónde está la amenaza, quién llamó y por qué medio.
    public readonly struct CrimeReport
    {
        public readonly Vector3 Position;
        public readonly GameObject Witness;
        public readonly CrimeReportSource Source;

        public CrimeReport(Vector3 position, GameObject witness, CrimeReportSource source) { Position = position; Witness = witness; Source = source; }
    }

    // Canal de denuncias (patrón Observer con ScriptableObject): los testigos avisan cuando terminan de llamar a la
    // policía (y las cámaras y los guardias dan su aviso) y quien escucha (el aviso en pantalla y la central) reacciona.
    [CreateAssetMenu(menuName = "Alarma/Eventos/Canal de denuncias", fileName = "Denuncias")]
    public sealed class CrimeReportChannel : ScriptableObject
    {
        public event Action<CrimeReport> Raised;

        public void Raise(Vector3 position, GameObject witness, CrimeReportSource source = CrimeReportSource.Witness)
            => Raised?.Invoke(new CrimeReport(position, witness, source));
    }
}
