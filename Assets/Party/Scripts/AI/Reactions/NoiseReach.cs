using UnityEngine;
using Alarma.Core.Events;

namespace Alarma.AI.Reactions
{
    // Hasta dónde llega un ruido para quien está en un lugar, según haya o no una pared en medio. El grito de alguien a
    // quien le apuntan es, en la práctica, ver la escena: con una pared de por medio (o la vitrina de un local) no llega.
    // Un disparo o un estallido sí cruzan, pero amortiguados. Lo usan el civil y su doble para decidir igual.
    internal static class NoiseReach
    {
        private const float WallMuffle = .4f; // parte del alcance que conserva un disparo al cruzar una pared
        private const int Walls = ~((1 << 29) | (1 << 30) | (1 << 31)); // todo menos personajes e interfaz

        public static float RadiusAt(NoiseEvent sound, Vector3 listener)
        {
            Vector3 ear = listener + Vector3.up * 1.5f, origin = sound.Position + Vector3.up * 1.2f;
            if (!Physics.Linecast(ear, origin, Walls, QueryTriggerInteraction.Ignore)) return sound.Radius;
            return sound.Kind == NoiseKind.Scream ? 0f : sound.Radius * WallMuffle;
        }
    }
}
