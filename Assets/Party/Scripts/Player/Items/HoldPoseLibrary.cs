using System;
using UnityEngine;

namespace Alarma.Player.Items
{
    // Dónde va el objeto según su forma de sostener, respecto del pecho del personaje (x derecha, y arriba, z adelante):
    // una pose al caminar y otra al correr (arma baja y pegada al cuerpo). Se ajusta en el Inspector sin tocar código.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Poses para sostener", fileName = "HoldPoses")]
    public sealed class HoldPoseLibrary : ScriptableObject
    {
        [Serializable]
        public struct Pose
        {
            public HoldStyle style;
            [Tooltip("Posición de la mano derecha (punto Grip_R del objeto) respecto del pecho.")] public Vector3 offset;
            [Tooltip("Giro del objeto respecto del personaje, en grados.")] public Vector3 euler;
            public Vector3 runOffset;
            public Vector3 runEuler;
            [Tooltip("Cuánto se balancea al caminar, en metros.")] public float sway;
            [Tooltip("Hacia dónde apuntan los dedos de cada mano, en ejes del objeto: rodean la empuñadura.")] public Vector3 rightFingers;
            public Vector3 leftFingers;
            [Tooltip("Pose apuntando con clic derecho (solo armas), sin inclinar: la cámara la inclina.")] public Vector3 aimOffset;
            public Vector3 aimEuler;
        }

        // Valores medidos con el brazo del elenco (unos 48 cm del hombro a la palma); revisión en Blender: preview_hold_poses.py.
        [SerializeField] private Pose[] poses =
        {
            // Pistola en guardia baja con las dos manos; al correr, apuntando al suelo junto al pecho.
            new Pose { style = HoldStyle.Pistol, offset = new Vector3(.05f, -.2f, .34f), euler = new Vector3(14, 0, 0), runOffset = new Vector3(.12f, -.24f, .24f), runEuler = new Vector3(55, 8, 0), sway = .012f, aimOffset = new Vector3(.06f, .06f, .42f), aimEuler = Vector3.zero,
                       rightFingers = new Vector3(-1, 0, .35f), leftFingers = new Vector3(1, -.2f, .3f) },
            // Escopeta y rifle en guardia baja, algo girados a la izquierda con el guardamanos al centro; al correr, cruzados sobre el pecho.
            new Pose { style = HoldStyle.Long, offset = new Vector3(.12f, -.12f, .14f), euler = new Vector3(8, -25, 0), runOffset = new Vector3(.08f, -.08f, .14f), runEuler = new Vector3(20, -55, 15), sway = .016f, aimOffset = new Vector3(.11f, .03f, .09f), aimEuler = new Vector3(0, -8, 0),
                       rightFingers = new Vector3(-1, 0, .35f), leftFingers = new Vector3(.9f, .4f, .2f) },
            // Herramienta larga en una mano (palanca, cortavidrios, gancho, granadas): baja y hacia adelante.
            new Pose { style = HoldStyle.OneHandUpright, offset = new Vector3(.2f, -.36f, .16f), euler = new Vector3(100, 0, 0), runOffset = new Vector3(.2f, -.34f, .1f), runEuler = new Vector3(120, 0, 0), sway = .02f,
                       rightFingers = new Vector3(-1, 0, .3f), leftFingers = new Vector3(1, 0, .3f) },
            // Herramienta chica que apunta adelante (ganzúa, bridas).
            new Pose { style = HoldStyle.OneHandPointing, offset = new Vector3(.2f, -.36f, .2f), euler = new Vector3(25, 0, 0), runOffset = new Vector3(.2f, -.34f, .12f), runEuler = new Vector3(40, 0, 0), sway = .02f,
                       rightFingers = new Vector3(-1, 0, .3f), leftFingers = new Vector3(1, 0, .3f) },
            // Tablet con las dos manos, la pantalla mirando a la cara.
            new Pose { style = HoldStyle.TwoHandTablet, offset = new Vector3(.12f, -.18f, .3f), euler = new Vector3(-55, 0, 0), runOffset = new Vector3(.12f, -.24f, .22f), runEuler = new Vector3(-20, 0, 0), sway = .01f,
                       rightFingers = new Vector3(-1, -.3f, 0), leftFingers = new Vector3(1, -.3f, 0) },
            // Carga de termita parada, sostenida con las dos manos frente al cuerpo.
            new Pose { style = HoldStyle.TwoHandCanister, offset = new Vector3(.05f, -.24f, .28f), euler = new Vector3(0, 0, 0), runOffset = new Vector3(.05f, -.26f, .22f), runEuler = new Vector3(10, 0, 0), sway = .014f,
                       rightFingers = new Vector3(-.3f, 0, 1), leftFingers = new Vector3(.3f, 0, 1) },
        };

        // Para assets creados antes de que existiera la pose de apuntar: copia solo esa pose desde los valores por defecto.
        public bool CompleteAimFrom(HoldPoseLibrary defaults)
        {
            bool changed = false;
            for (int i = 0; i < poses.Length; i++)
            {
                if (poses[i].aimOffset != Vector3.zero) continue;
                var fallback = defaults.Find(poses[i].style);
                if (fallback.style != poses[i].style || fallback.aimOffset == Vector3.zero) continue;
                poses[i].aimOffset = fallback.aimOffset; poses[i].aimEuler = fallback.aimEuler;
                changed = true;
            }
            return changed;
        }

        public Pose Find(HoldStyle style)
        {
            foreach (var pose in poses)
                if (pose.style == style) return pose;
            return poses[0];
        }
    }
}
