using System;
using UnityEngine;

namespace Alarma.Core.Events
{
    // Scream: el grito de alguien a quien le apuntan; asusta menos que un disparo y se oye más cerca.
    public enum NoiseKind { Gunshot, Explosion, Scream }

    // Un ruido fuerte en el mundo: dónde, hasta dónde se oye y quién lo hizo.
    public readonly struct NoiseEvent
    {
        public readonly Vector3 Position;
        public readonly float Radius;
        public readonly NoiseKind Kind;
        public readonly GameObject Source;

        public NoiseEvent(Vector3 position, float radius, NoiseKind kind, GameObject source)
        {
            Position = position; Radius = radius; Kind = kind; Source = source;
        }
    }

    // Canal de eventos (patrón Observer con ScriptableObject): las armas avisan los disparos y quien escucha (civiles,
    // y más adelante guardias y alerta) reacciona, sin referencias directas entre sistemas.
    [CreateAssetMenu(menuName = "Alarma/Eventos/Canal de ruido", fileName = "Ruido")]
    public sealed class NoiseChannel : ScriptableObject
    {
        public event Action<NoiseEvent> Raised;

        public void Raise(Vector3 position, float radius, NoiseKind kind, GameObject source)
        {
            if (radius > 0f) Raised?.Invoke(new NoiseEvent(position, radius, kind, source));
        }
    }
}
