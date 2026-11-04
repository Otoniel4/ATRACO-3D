using System;
using UnityEngine;

namespace Alarma.Vehicles
{
    // Colores posibles de pintura y probabilidad de llevar acompañante; agregar un color es agregarlo aquí, sin tocar código.
    [CreateAssetMenu(menuName = "Alarma/Paleta de autos", fileName = "CarPalette")]
    public sealed class CarPalette : ScriptableObject
    {
        [SerializeField] private Color[] paints = Array.Empty<Color>();
        [SerializeField, Range(0f, 1f)] private float passengerChance = .35f;

        public float PassengerChance => passengerChance;
        public Color Paint(System.Random random) => paints.Length == 0 ? Color.white : paints[random.Next(paints.Length)];

        public void Configure(Color[] paintColors) => paints = paintColors;
    }
}
