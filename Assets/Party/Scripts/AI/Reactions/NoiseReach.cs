using UnityEngine;
using Alarma.Core.Events;

namespace Alarma.AI.Reactions
{
    // Hasta dónde llega un ruido para quien está en un lugar, según haya o no una pared en medio. El grito de alguien a
    // quien le apuntan es, en la práctica, ver la escena: con una pared de por medio no llega, pero por la vidriera o la
    // puerta de vidrio de un local sí (Sightline): los de afuera ven el atraco. Un disparo o un estallido cruzan las
    // paredes, amortiguados. Lo usan el civil y su doble para decidir igual.
    internal static class NoiseReach
    {
        private const float WallMuffle = .4f; // parte del alcance que conserva un disparo al cruzar una pared

        public static float RadiusAt(NoiseEvent sound, Vector3 listener)
        {
            Vector3 ear = listener + Vector3.up * 1.5f, origin = sound.Position + Vector3.up * 1.2f;
            if (Sightline.Clear(ear, origin)) return sound.Radius;
            return sound.Kind == NoiseKind.Scream ? 0f : sound.Radius * WallMuffle;
        }
    }
}
