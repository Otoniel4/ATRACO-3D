using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife;
using Alarma.AI.Security;
using Alarma.Core.Editor;

namespace Alarma.City.Editor
{
    // Cámaras de seguridad en cada local con interior (Task 15): una sobre la puerta mirando hacia adentro (caja y
    // pasillos) y otra al fondo mirando hacia la puerta (la entrada). Van colgadas del techo que encuentran arriba.
    internal static class City25Cameras
    {
        private const string Model = "Assets/Party/Art/Props/Prop_SecurityCamera.fbx";
        private const string SettingsPath = "Assets/Party/Data/NPC/Camaras.asset";
        private const float FromWall = 1.2f, BelowCeiling = .32f, Tilt = 28f;
        private const int Structure = ~((1 << 28) | (1 << 29) | (1 << 30) | (1 << 31));

        public static int Place(City25World.Result world)
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Model);
            if (model == null) { Debug.LogWarning("Falta " + Model + ": los locales no tendrán cámaras."); return 0; }
            var settings = LoadOrCreateSettings();
            int placed = 0;
            Physics.SyncTransforms();
            foreach (var (data, instance) in world.Places)
            {
                if (data.size.Length < 2 || instance.GetComponentInChildren<ShopActivity>(true) == null) continue;
                float front = data.size[1] / 2f; // la fachada mira a +Z
                if (Mount(instance.transform, new Vector3(0f, 0f, front - FromWall), Vector3.back, model, settings)) placed++;
                if (Mount(instance.transform, new Vector3(0f, 0f, -front + FromWall), Vector3.forward, model, settings)) placed++;
            }
            return placed;
        }

        private static bool Mount(Transform shop, Vector3 local, Vector3 localLook, GameObject model, SecurityCameraSettings settings)
        {
            Vector3 below = shop.TransformPoint(local) + Vector3.up * 1.5f;
            if (!Physics.Raycast(below, Vector3.up, out var ceiling, 8f, Structure, QueryTriggerInteraction.Ignore)) return false;
            var root = new GameObject("Cámara de seguridad");
            root.transform.SetParent(shop, false);
            root.transform.SetPositionAndRotation(ceiling.point - Vector3.up * BelowCeiling, Quaternion.LookRotation(shop.TransformDirection(localLook), Vector3.up));
            // Cabeza que gira: el lente del modelo mira a +Z; va inclinada hacia el piso.
            var head = new GameObject("Cabeza").transform;
            head.SetParent(root.transform, false);
            head.localRotation = Quaternion.Euler(Tilt, 0f, 0f);
            var body = (GameObject)PrefabUtility.InstantiatePrefab(model);
            body.transform.SetParent(head, false);
            foreach (var collider in body.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(collider);
            var cone = new GameObject("Cono de visión").AddComponent<Light>();
            cone.transform.SetParent(head, false);
            cone.transform.localPosition = new Vector3(0f, .17f, .34f); // delante del lente
            cone.type = LightType.Spot; cone.shadows = LightShadows.None; cone.intensity = 6f;
            cone.range = settings.Range; cone.spotAngle = settings.HalfAngle * 2f; cone.color = new Color(.3f, 1f, .45f);
            root.AddComponent<SecurityCamera>().Configure(settings, head, cone, EventAssets.Suspects(), EventAssets.CrimeReports());
            return true;
        }

        private static SecurityCameraSettings LoadOrCreateSettings()
        {
            var settings = AssetDatabase.LoadAssetAtPath<SecurityCameraSettings>(SettingsPath);
            if (settings != null) return settings;
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsPath));
            settings = ScriptableObject.CreateInstance<SecurityCameraSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }
    }
}
