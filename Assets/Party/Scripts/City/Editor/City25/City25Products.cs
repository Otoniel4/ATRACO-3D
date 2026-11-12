using System;
using System.IO;
using System.Linq;
using Alarma.AI.CityLife;
using Alarma.AI.CityLife.Editor;
using UnityEditor;
using UnityEngine;

namespace Alarma.City.Editor
{
    // Importación repetible: conserva GUID y asigna materiales URP a los modelos aprobados.
    internal static class City25Products
    {
        private const string Root = "Assets/Party/Art/Props/ShopObjects";
        [Serializable] private sealed class Catalog { public Entry[] items; public Finish[] materials; }
        [Serializable] private sealed class Entry
        {
            public string id, shop;
            public Vector3 support, right, left, fingers, normal, leftFingers, leftNormal;
            public float curl;
            public bool twoHands;
        }
        [Serializable] private sealed class Finish { public string name; public Color color; public float metallic, roughness; }
        // Poses de dedos hechas en Blender (build_hand_poses.py) y qué pose usa cada objeto.
        private const string HandPoses = "Assets/Party/Art/Characters/Animations/hand_poses.json";
        [Serializable] private sealed class HandCatalog { public Grip[] poses; public GripUse[] objects; }
        [Serializable] private sealed class Grip { public string id; public float[] thumb, index, middle, ring, pinky; }
        [Serializable] private sealed class GripUse { public string id, pose; }

        public static ShopProductDefinition[] Load(string business)
        {
            var source = AssetDatabase.LoadAssetAtPath<TextAsset>(Root + "/catalog.json");
            if (source == null) throw new InvalidOperationException("Falta el catálogo aprobado de objetos R44.");
            var catalog = JsonUtility.FromJson<Catalog>(source.text);
            EnsureFolder(Root + "/Materials"); EnsureFolder(Root + "/Definitions");
            foreach (var finish in catalog.materials)
            {
                string path = Root + "/Materials/" + finish.name + ".mat";
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material == null)
                {
                    material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                    AssetDatabase.CreateAsset(material, path);
                }
                material.SetColor("_BaseColor", finish.color);
                material.SetFloat("_Metallic", finish.metallic);
                material.SetFloat("_Smoothness", 1f - finish.roughness);
                EditorUtility.SetDirty(material);
            }
            var hands = LoadHandPoses();
            return catalog.items.Where(e => e.shop == business).Select(e => Prepare(e, catalog, hands)).ToArray();
        }

        // Un asset por pose (ShopObjects/HandPoses) y, por objeto, la pose que le toca. Sin el archivo, los objetos
        // quedan con el cierre parejo de siempre.
        private static System.Collections.Generic.Dictionary<string, HandPose> LoadHandPoses()
        {
            var uses = new System.Collections.Generic.Dictionary<string, HandPose>();
            var source = AssetDatabase.LoadAssetAtPath<TextAsset>(HandPoses);
            if (source == null) { Debug.LogWarning("Falta " + HandPoses + ": las manos usan el cierre parejo."); return uses; }
            var data = JsonUtility.FromJson<HandCatalog>(source.text);
            EnsureFolder(Root + "/HandPoses");
            var poses = new System.Collections.Generic.Dictionary<string, HandPose>();
            foreach (var grip in data.poses)
            {
                string path = Root + "/HandPoses/" + grip.id + ".asset";
                var pose = AssetDatabase.LoadAssetAtPath<HandPose>(path);
                if (pose == null) { pose = ScriptableObject.CreateInstance<HandPose>(); AssetDatabase.CreateAsset(pose, path); }
                pose.Id = grip.id;
                pose.Thumb = Angles(grip.thumb); pose.Index = Angles(grip.index); pose.Middle = Angles(grip.middle);
                pose.Ring = Angles(grip.ring); pose.Pinky = Angles(grip.pinky);
                EditorUtility.SetDirty(pose);
                poses[grip.id] = pose;
            }
            foreach (var use in data.objects)
                if (poses.TryGetValue(use.pose, out var pose)) uses[use.id] = pose;
            return uses;
        }

        private static Vector3 Angles(float[] joints)
        {
            if (joints == null || joints.Length != HandPose.Joints) throw new InvalidOperationException("Cada dedo de una pose de mano lleva " + HandPose.Joints + " ángulos.");
            return new Vector3(joints[0], joints[1], joints[2]);
        }

        private static ShopProductDefinition Prepare(Entry entry, Catalog catalog, System.Collections.Generic.Dictionary<string, HandPose> hands)
        {
            string modelPath = Root + "/" + entry.id + ".fbx";
            var importer = AssetImporter.GetAtPath(modelPath) as ModelImporter;
            if (importer == null) throw new InvalidOperationException("Falta el modelo " + modelPath);
            // Blender exporta estos FBX en centímetros con el objeto a escala 100: sin la escala del archivo, una botella
            // de 25 cm mide 25 m en Unity.
            bool changed = importer.importAnimation || importer.addCollider || !importer.useFileScale || !Mathf.Approximately(importer.globalScale, 1f);
            importer.importAnimation = false; importer.addCollider = false; importer.useFileScale = true; importer.globalScale = 1f;
            var mappings = importer.GetExternalObjectMap();
            foreach (var finish in catalog.materials)
            {
                var key = new AssetImporter.SourceAssetIdentifier(typeof(Material), finish.name);
                var material = AssetDatabase.LoadAssetAtPath<Material>(Root + "/Materials/" + finish.name + ".mat");
                if (!mappings.TryGetValue(key, out var previous) || previous != material)
                { importer.AddRemap(key, material); changed = true; }
            }
            if (changed) importer.SaveAndReimport();
            string path = Root + "/Definitions/" + entry.id + ".asset";
            var definition = AssetDatabase.LoadAssetAtPath<ShopProductDefinition>(path);
            if (definition == null)
            {
                definition = ScriptableObject.CreateInstance<ShopProductDefinition>();
                AssetDatabase.CreateAsset(definition, path);
            }
            definition.Id = entry.id; definition.Business = entry.shop;
            definition.Model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            definition.Support = entry.support; definition.RightGrip = entry.right; definition.LeftGrip = entry.left;
            definition.Fingers = entry.fingers; definition.PalmNormal = entry.normal;
            definition.LeftFingers = entry.leftFingers; definition.LeftNormal = entry.leftNormal;
            definition.FingerCurl = entry.curl; definition.TwoHands = entry.twoHands;
            definition.Hand = hands.TryGetValue(entry.id, out var hand) ? hand : null;
            CalibrateImportedAnchors(definition);
            EditorUtility.SetDirty(definition);
            return definition;
        }

        // Lee el FBX ya importado: no supone que Blender y Unity conservan el signo del eje lateral.
        private static void CalibrateImportedAnchors(ShopProductDefinition definition)
        {
            var root = definition.Model.transform;
            var anchors = root.GetComponentsInChildren<Transform>(true);
            Vector3 Read(string name)
            {
                var matches = anchors.Where(t => BlenderAssetNames.Matches(t.name, name)).ToArray();
                if (matches.Length != 1) throw new InvalidOperationException(definition.Id + ": se esperaba un marcador " + name +
                    ", encontrados " + matches.Length + ". Nombres: " + string.Join(", ", anchors.Select(t => t.name)));
                var anchor = matches[0];
                return root.localRotation * Vector3.Scale(root.InverseTransformPoint(anchor.position), root.lossyScale);
            }
            definition.Support = Read("Support");
            definition.RightGrip = Read("Grip_R");
            definition.LeftGrip = Read("Grip_L");
            float side = Mathf.Sign(definition.RightGrip.x - definition.LeftGrip.x);
            definition.PalmNormal = new Vector3(definition.PalmNormal.x * side, definition.PalmNormal.y, definition.PalmNormal.z);
            definition.LeftNormal = new Vector3(definition.LeftNormal.x * side, definition.LeftNormal.y, definition.LeftNormal.z);
            if (definition.Id == "Vaso") definition.RightGrip = new Vector3(.033f * side, .07f, definition.Support.z);
            if (definition.Business == "joyeria") definition.RightGrip = definition.Support - Vector3.up * .004f;
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent); AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        public static void BankDisplay(Transform parent, ShopProductDefinition[] products, Vector3 center)
        {
            foreach (var definition in products.Where(p => p.Id != "Sobre"))
            {
                var item = UnityEngine.Object.Instantiate(definition.Model, parent);
                item.name = "Objeto_" + definition.Id;
                item.transform.localPosition = center + new Vector3(definition.Id == "Lingote" ? -.55f : .55f, 0f, -.30f) - definition.Support;
                item.AddComponent<ShopProductInstance>().Definition = definition;
            }
        }
    }
}
