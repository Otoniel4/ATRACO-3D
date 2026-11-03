using UnityEngine;

namespace Alarma.AI.CityLife
{
    [CreateAssetMenu(menuName = "Alarma/Ciudad/Rutina de peatones R5")]
    public sealed class PedestrianSettings : ScriptableObject
    {
        [Min(1)] public int PopulationBudget = 24;
        [Range(1, 10)] public int PerDistrict = 8;
        [Min(10)] public float ActivationRadius = 120f;
        [Min(20)] public float DeactivationRadius = 180f;
        [Range(.5f, 2f)] public float WalkingSpeed = 1f;
        [Min(.1f)] public float BrowseSeconds = 3f;
        [Min(.1f)] public float PaySeconds = 2f;
        [Range(0f, 1f)] public float ShopperFraction = .65f;
        [Min(1f)] public float TravelTimeout = 80f;
        [Min(1f)] public float QueueTimeout = 80f;
        private void OnValidate() { DeactivationRadius = Mathf.Max(ActivationRadius + 10f, DeactivationRadius); }
    }
}
