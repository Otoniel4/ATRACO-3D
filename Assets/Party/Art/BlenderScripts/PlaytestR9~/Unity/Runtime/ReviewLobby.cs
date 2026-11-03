using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    // Puntos locales del escondite preparados para la posterior creación de jugadores de red.
    public sealed class ReviewLobby:MonoBehaviour
    {
        [SerializeField] private Transform[] spawnSlots=Array.Empty<Transform>();
        public Transform[] SpawnSlots=>spawnSlots;
        public void Configure(Transform[] slots){spawnSlots=slots;}
    }
}
