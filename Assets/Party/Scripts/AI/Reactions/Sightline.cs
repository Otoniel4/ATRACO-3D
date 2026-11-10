using System;
using UnityEngine;
using Alarma.AI.CityLife;

namespace Alarma.AI.Reactions
{
    // Línea de visión entre dos puntos: las paredes tapan, pero las vidrieras de los locales («Storefront» en
    // build_shops.py) y sus puertas de vidrio dejan ver. Así quien pasa por la acera ve lo que ocurre adentro.
    // Los autos tampoco tapan: se ve por encima o a través de sus ventanas.
    internal static class Sightline
    {
        private const int Walls = ~((1 << 28) | (1 << 29) | (1 << 30) | (1 << 31)); // todo menos autos, personajes e interfaz
        private const int MaxPanes = 4;      // vidrios que se pueden atravesar en una misma mirada
        private const float PastPane = .06f; // cuánto se avanza para pasar al otro lado de un vidrio

        public static bool Clear(Vector3 from, Vector3 to)
        {
            for (int pane = 0; pane <= MaxPanes; pane++)
            {
                if (!Physics.Linecast(from, to, out var hit, Walls, QueryTriggerInteraction.Ignore)) return true;
                if (!SeeThrough(hit.collider)) return false;
                from = hit.point + (to - from).normalized * PastPane;
            }
            return false;
        }

        private static bool SeeThrough(Collider piece)
            => piece.name.StartsWith("Storefront", StringComparison.Ordinal) || piece.GetComponentInParent<ShopDoor>() != null;
    }
}
