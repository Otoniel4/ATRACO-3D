using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

namespace Alarma.City.Editor
{
    // Guardias en la puerta de los locales que vale la pena robar y policías en la entrada de las comisarías.
    internal static class City25Security
    {
        // Tipo de lugar → cuántos y si son policías (con pistola) o guardias (con porra).
        private static readonly Dictionary<string, (int count, bool police)> Posts = new Dictionary<string, (int, bool)>
        {
            ["banco"] = (2, false), ["joyeria"] = (1, false), ["supermercado"] = (1, false), ["comisaria"] = (2, true),
        };

        public static int Place(City25World.Result world, GameObject guard, GameObject police)
        {
            int placed = 0;
            Physics.SyncTransforms();
            foreach (var (data, instance) in world.Places)
            {
                if (!Posts.TryGetValue(data.place.kind, out var post)) continue;
                // Junto a la puerta, al centro de la fachada (frente +Z), mirando a la calle.
                float front = data.size[1] / 2f + .9f;
                for (int i = 0; i < post.count; i++)
                {
                    float side = post.count == 1 ? 2.4f : (i == 0 ? -2.4f : 2.4f);
                    Vector3 spot = instance.transform.TransformPoint(new Vector3(side, 0f, front));
                    if (Physics.Raycast(spot + Vector3.up * 1.5f, Vector3.down, out var hit, 4f,  // bajo el toldo
                         ~((1 << 28) | (1 << 29) | (1 << 30)), QueryTriggerInteraction.Ignore))
                        spot.y = hit.point.y;
                    var person = (GameObject)PrefabUtility.InstantiatePrefab(post.police ? police : guard, instance.transform);
                    person.transform.SetPositionAndRotation(spot, instance.transform.rotation);
                    placed++;
                }
            }
            return placed;
        }
    }
}
