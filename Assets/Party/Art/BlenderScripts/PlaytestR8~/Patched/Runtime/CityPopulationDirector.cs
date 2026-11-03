using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Pool;

namespace Alarma.AI.CityLife
{
    public sealed class CityPopulationDirector : MonoBehaviour
    {
        [SerializeField] private PedestrianSettings settings;
        [SerializeField] private PedestrianActor[] variants = Array.Empty<PedestrianActor>();
        [SerializeField] private ShopActivity[] shops = Array.Empty<ShopActivity>();
        [SerializeField] private Transform[] observers = Array.Empty<Transform>();
        [SerializeField] private CityLifeAuthority authority;
        [SerializeField] private int activeCount;
        private readonly Dictionary<int, ObjectPool<PedestrianActor>> pools = new Dictionary<int, ObjectPool<PedestrianActor>>();
        private readonly List<Resident> active = new List<Resident>();
        private readonly HashSet<int> usedVariants = new HashSet<int>();
        private int serial, nextVariant;
        private float nextUpdate;
        private bool warnedLegacy;
        [SerializeField] private CityTrafficController traffic;
        private sealed class Resident { public PedestrianActor Actor; public ShopActivity Shop; public int Variant; }
        public int ActiveCount => activeCount;

        public void Configure(PedestrianSettings data, PedestrianActor[] prefabs, ShopActivity[] districts, Transform observer, CityLifeAuthority owner,CityTrafficController movement)
        { settings = data; variants = prefabs; shops = districts; observers = new[] { observer }; authority = owner;traffic=movement; }

        private void Update()
        {
            if (Time.unscaledTime < nextUpdate) return;
            nextUpdate = Time.unscaledTime + .5f;
            if (settings == null || authority == null || !authority.CanSimulate || observers.Length == 0)
            { ReleaseAll(); return; }
            for (int i = active.Count - 1; i >= 0; i--)
                if (active[i].Actor.Failed || Distance(active[i].Actor.transform.position) > settings.DeactivationRadius) Release(i);
            while(active.Count>Mathf.Max(0,settings.PopulationBudget))Release(active.Count-1);
            foreach (ShopActivity shop in shops)
            {
                if(shop!=null && !shop.IsConfigured){if(!warnedLegacy){Debug.LogWarning("La escena R5 requiere regeneración: Alarma/Ciudad/Crear demo local R6.",this);warnedLegacy=true;}continue;}
                if (shop == null || shop.WalkRoute.Length == 0 || Distance(shop.transform.position) > settings.ActivationRadius) continue;
                usedVariants.Clear();
                usedVariants.Add(shop.ReservedVariant);
                foreach (Resident resident in active) if (resident.Shop == shop) usedVariants.Add(resident.Variant);
                int count = usedVariants.Count - 1;
                while (count < settings.PerDistrict && active.Count < settings.PopulationBudget)
                {
                    int variant = ChooseVariant();
                    if (variant < 0) break;
                    usedVariants.Add(variant); count++;
                    int start = (serial * 3 + variant) % shop.WalkRoute.Length;
                    PedestrianActor actor = Pool(variant).Get(); actor.gameObject.SetActive(true);
                    // Secuencia distribuida; evita que todos los primeros residentes sean compradores.
                    bool shopper = ((serial * 37) % 100) < Mathf.RoundToInt(settings.ShopperFraction * 100);
                    int id = ++serial;
                    Vector3 spawn = shop.WalkRoute[start].position + Vector3.right * (.65f * ((count - 1) / shop.WalkRoute.Length));
                    if (!actor.Begin(id, spawn, shop, settings, shopper, start,shop.Traffic!=null?shop.Traffic:traffic))
                    { Pool(variant).Release(actor); continue; }
                    active.Add(new Resident { Actor = actor, Shop = shop, Variant = variant });
                }
            }
            activeCount = active.Count;
        }

        private int ChooseVariant()
        {
            for (int i = 0; i < variants.Length; i++)
            {
                int index = nextVariant++ % variants.Length;
                if (variants[index] != null && !usedVariants.Contains(index)) return index;
            }
            return -1;
        }
        private float Distance(Vector3 position)
        {
            float nearest = float.PositiveInfinity;
            foreach (Transform observer in observers) if (observer != null) nearest = Mathf.Min(nearest, Vector3.Distance(position, observer.position));
            return nearest;
        }
        private ObjectPool<PedestrianActor> Pool(int variant)
        {
            if (pools.TryGetValue(variant, out ObjectPool<PedestrianActor> pool)) return pool;
            pool = new ObjectPool<PedestrianActor>(
                () => { PedestrianActor actor = Instantiate(variants[variant], transform); actor.gameObject.SetActive(false); return actor; },
                null,
                actor => { actor.Suspend(); actor.gameObject.SetActive(false); },
                actor => { if (actor != null) Destroy(actor.gameObject); },
                true, 2, Mathf.Max(1, settings.PopulationBudget));
            pools.Add(variant, pool); return pool;
        }
        private void Release(int index) { Resident resident = active[index]; active.RemoveAt(index); Pool(resident.Variant).Release(resident.Actor); }
        private void ReleaseAll() { for (int i = active.Count - 1; i >= 0; i--) Release(i); activeCount = 0; }
        private void OnDisable() => ReleaseAll();
        private void OnDestroy() { ReleaseAll(); foreach (ObjectPool<PedestrianActor> pool in pools.Values) pool.Clear(); pools.Clear(); }
    }
}
