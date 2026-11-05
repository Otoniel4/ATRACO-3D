using System;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using Alarma.City.Playtest;

namespace Alarma.City.Editor
{
    // Comprobaciones antes de guardar la escena: todo el plano colocado, suelo con colisión, escondite pisable y locales en su sitio.
    internal static class City25Acceptance
    {
        [Serializable]
        private sealed class Evidence
        {
            public int objects, groundSectors, places;
            public float spawnGroundHeight;
            public Vector3 spawnPosition;
            public bool spawnFree, play_tested;
        }

        public static string Validate(Scene scene, City25World.Result world, CityObjects city, ReviewPlayerMotor player)
        {
            int expected = city.objects.Count(o => o.kit != "Lot" && o.kit != "Sewer");
            if (world.Placed != expected) throw new InvalidOperationException($"Se colocaron {world.Placed} de {expected} objetos del plano.");
            if (world.Ground.Any(g => !g.GetComponentsInChildren<MeshCollider>(true).Any(c => c.sharedMesh != null))) throw new InvalidOperationException("Hay sectores de suelo sin colisión.");
            Physics.SyncTransforms();
            var physics = scene.GetPhysicsScene();
            var controller = player.GetComponent<CharacterController>();
            var spawn = player.transform.position;
            bool free = ReviewPlayerGrounding.TryResolve(physics, spawn, controller.height, controller.radius,
                controller.slopeLimit, out var grounded, out var hit);
            if (!free || Mathf.Abs(hit.point.y) > .3f) throw new InvalidOperationException("El marcador PlayerSpawn debe tener piso de planta baja y espacio libre para el jugador.");
            // La misma regla de Play ignora las capas 29–31 y valida el cuerpo completo dentro del recibidor.
            player.transform.position = grounded;
            // Cada local debe quedar donde dice el plano: confirma ejes, escala y giro del kit en Unity.
            foreach (var (data, instance) in world.Places)
            {
                // Solo el modelo del edificio (primer hijo): guardias, cajero y compradores no cuentan. Si el modelo trae
                // patio propio (escondite), se mide la casa, marcada como «Edificio».
                var model = instance.transform.GetChild(0);
                var building = model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == "Edificio") ?? model;
                var renderers = building.GetComponentsInChildren<Renderer>(true);
                var bounds = renderers[0].bounds; foreach (var r in renderers) bounds.Encapsulate(r.bounds);
                if (Vector2.Distance(new Vector2(bounds.center.x, bounds.center.z), new Vector2(data.x, data.y)) > 1.5f)
                    throw new InvalidOperationException($"{data.place.name} quedó fuera de su lugar en el plano.");
            }
            return JsonUtility.ToJson(new Evidence { objects = world.Placed, groundSectors = world.Ground.Count, places = world.Places.Count, spawnGroundHeight = hit.point.y, spawnPosition = grounded, spawnFree = free, play_tested = false }, true);
        }
    }
}
