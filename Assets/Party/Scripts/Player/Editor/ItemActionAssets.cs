using System;
using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.Player.Items;

namespace Alarma.Player.Editor
{
    // Crea o pone al día la acción de cada objeto (Party/Data/Items/Actions) con los datos de Data/Items/item_actions.json,
    // que genera Art/BlenderScripts/make_item_actions.py y que también usa Blender para revisar las animaciones cuadro a cuadro.
    // Un asset se vuelve a escribir solo si su versión es menor que la del archivo; así lo ajustado en el Inspector se conserva
    // hasta que se publiquen datos nuevos.
    public static class ItemActionAssets
    {
        private const string Folder = "Assets/Party/Data/Items/Actions";
        private const string DataFile = "Assets/Party/Data/Items/item_actions.json";
        public static ItemAction For(string itemId)
        {
            var data = Load();
            var entry = Array.Find(data.actions, a => a.id == itemId);
            if (entry == null) return null;
            Directory.CreateDirectory(Folder);
            string path = Folder + "/Action_" + itemId + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<ItemAction>(path);
            if (existing != null && existing.DataVersion >= data.version) return existing;
            var action = existing != null && existing.GetType() == TypeOf(entry) ? existing : (ItemAction)ScriptableObject.CreateInstance(TypeOf(entry));
            Apply(action, entry, data.version);
            if (action == existing) EditorUtility.SetDirty(action);
            else if (existing == null) AssetDatabase.CreateAsset(action, path);
            else
            {
                // Cambió el tipo de acción: el asset anterior no puede convertirse; se reemplaza en el mismo lugar.
                Debug.LogWarning("La acción de " + itemId + " cambió de tipo; se vuelve a crear " + path + ".");
                AssetDatabase.CreateAsset(action, path);
            }
            return action;
        }

        // Se lee cada vez: el archivo es pequeño y así se toman los datos recién generados.
        private static ActionFile Load()
        {
            if (!File.Exists(DataFile)) throw new FileNotFoundException("Faltan los datos de las acciones (make_item_actions.py)", DataFile);
            return JsonUtility.FromJson<ActionFile>(File.ReadAllText(DataFile));
        }

        private static Type TypeOf(ActionEntry entry)
        {
            switch (entry.type)
            {
                case "firearm": return typeof(FirearmAction);
                case "tool": return typeof(ToolAction);
                case "throw": return typeof(ThrowAction);
                case "charge": return typeof(PlaceChargeAction);
                default: throw new InvalidDataException("Tipo de acción desconocido en item_actions.json: " + entry.type);
            }
        }

        private static void Apply(ItemAction action, ActionEntry entry, int version)
        {
            action.ConfigureMotion(entry.duration, entry.trigger, entry.repeat, entry.curves.ToMotion(), entry.shake, entry.spin, entry.spinSpeed, entry.blink, version);
            // Clip de cuerpo (build_action_clips.py → capa Acciones del Animator, ItemActionAnimatorAssets).
            action.ConfigureBody(entry.clip ? entry.animationId : 0, entry.fullBody);
            switch (action)
            {
                case FirearmAction gun:
                    var f = entry.firearm;
                    gun.Configure(f.damage, f.range, f.pellets, f.hipSpread, f.aimSpread, f.stun, f.pump, ToColor(f.flash), ToColor(f.tracer));
                    break;
                case ToolAction tool:
                    tool.Configure(entry.tool.range, entry.tool.consume, entry.tool.rope, entry.tool.nothing, entry.tool.requireTarget);
                    break;
                case ThrowAction thrown:
                    thrown.Configure((BlastKind)Enum.Parse(typeof(BlastKind), entry.thrown.kind), entry.thrown.speed, entry.thrown.fuse, entry.thrown.radius);
                    break;
                case PlaceChargeAction charge:
                    charge.Configure(entry.charge.reach, entry.charge.fuse, entry.charge.burn);
                    break;
            }
        }

        private static Color ToColor(float[] rgb) => rgb != null && rgb.Length >= 3 ? new Color(rgb[0], rgb[1], rgb[2]) : Color.white;

        // Forma del archivo JSON (los nombres de los campos son las claves del archivo).
        [Serializable] private sealed class ActionFile { public int version; public ActionEntry[] actions = Array.Empty<ActionEntry>(); }

        [Serializable]
        private sealed class ActionEntry
        {
            public string id, type, spin, blink;
            public float duration, trigger, shake, spinSpeed;
            public bool repeat, clip, fullBody;
            public int animationId;
            public CurveData curves = new CurveData();
            public FirearmData firearm = new FirearmData();
            public ToolData tool = new ToolData();
            public ThrowData thrown = new ThrowData();
            public ChargeData charge = new ChargeData();
        }

        [Serializable]
        private sealed class CurveData
        {
            public float[] side, up, forward, pitch, yaw, roll, leanForward, leanTwist, leanSide, leftHand;

            public MotionCurves ToMotion()
            {
                var motion = new MotionCurves();
                motion.side = Curve(side); motion.up = Curve(up); motion.forward = Curve(forward);
                motion.pitch = Curve(pitch); motion.yaw = Curve(yaw); motion.roll = Curve(roll);
                motion.leanForward = Curve(leanForward); motion.leanTwist = Curve(leanTwist); motion.leanSide = Curve(leanSide);
                motion.leftHand = Curve(leftHand);
                return motion;
            }

            // Curva suave por pares (tiempo, valor); sin datos, queda en cero. Pasa por cada punto sin pasarse de largo:
            // tangente plana en los extremos, los picos y los tramos quietos, y acotada en las subidas (la misma cuenta que
            // preview_item_actions.py). SmoothTangents se pasaba: un tramo quieto de 40 cm llegaba a bajar 62.
            private static AnimationCurve Curve(float[] pairs)
            {
                if (pairs == null || pairs.Length < 2) return AnimationCurve.Constant(0, 1, 0);
                int count = pairs.Length / 2;
                var keys = new Keyframe[count];
                for (int i = 0; i < count; i++)
                {
                    float slope = 0f;
                    if (i > 0 && i < count - 1)
                    {
                        float a = (pairs[2 * i + 1] - pairs[2 * i - 1]) / (pairs[2 * i] - pairs[2 * i - 2]);
                        float b = (pairs[2 * i + 3] - pairs[2 * i + 1]) / (pairs[2 * i + 2] - pairs[2 * i]);
                        if (a * b > 0f) slope = Mathf.Sign(a) * Mathf.Min(Mathf.Abs(a + b) / 2f, 3f * Mathf.Min(Mathf.Abs(a), Mathf.Abs(b)));
                    }
                    keys[i] = new Keyframe(pairs[2 * i], pairs[2 * i + 1], slope, slope);
                }
                return new AnimationCurve(keys);
            }
        }

        [Serializable] private sealed class FirearmData { public float damage, range, hipSpread, aimSpread; public int pellets = 1; public bool stun; public string pump = ""; public float[] flash, tracer; }
        [Serializable] private sealed class ToolData { public float range = 1.5f; public bool consume, rope, requireTarget; public string nothing = ""; }
        [Serializable] private sealed class ThrowData { public string kind = "Smoke"; public float speed = 13f, fuse = 1.5f, radius = 6f; }
        [Serializable] private sealed class ChargeData { public float reach = 2f, fuse = 3f, burn = 6f; }
    }
}
