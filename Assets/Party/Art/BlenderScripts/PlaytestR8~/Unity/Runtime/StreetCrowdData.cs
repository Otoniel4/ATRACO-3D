using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    [Serializable] public sealed class StreetRoute
    {
        public Vector3 Center;
        public Vector3[] Points=Array.Empty<Vector3>();
    }
    public sealed class StreetCrowdData:ScriptableObject
    {
        public StreetRoute[] Routes=Array.Empty<StreetRoute>();
    }
}
