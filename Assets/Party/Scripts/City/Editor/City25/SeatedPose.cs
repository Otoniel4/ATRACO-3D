using System;
using System.Linq;
using UnityEngine;

namespace Alarma.City.Editor
{
    // Sienta a un personaje del elenco orientando sus huesos por dirección (misma regla que la revisión en Blender:
    // build_vehicles.py). Espacio del personaje en Unity: derecha +X, arriba +Y, frente +Z; los valores son del lado izquierdo.
    internal static class SeatedPose
    {
        private static readonly Vector3 Abdomen = new Vector3(0f, 1f, -.3f), UpperLeg = new Vector3(-.06f, .15f, 1f), LowerLeg = new Vector3(0f, -1f, .25f);
        private static readonly Vector3 DriveUpperArm = new Vector3(.15f, -.45f, .8f), DriveLowerArm = new Vector3(.35f, .2f, .9f);
        private static readonly Vector3 RideUpperArm = new Vector3(.1f, -1f, .35f), RideLowerArm = new Vector3(.1f, -.15f, 1f);

        // character debe mirar hacia el frente del auto; seat es el vacío Seat_* del modelo del auto.
        public static void Apply(Transform character, Transform car, Transform seat, bool driving)
        {
            var bones = character.GetComponentsInChildren<Transform>(true);
            Transform Bone(string name) => bones.FirstOrDefault(t => t.name == name) ?? throw new InvalidOperationException($"{character.name}: falta el hueso {name}.");
            Aim(character, Bone("Abdomen"), Bone("Torso").position, Abdomen);
            foreach (var (side, mirror) in new[] { ("L", 1f), ("R", -1f) })
            {
                Vector3 Side(Vector3 v) => new Vector3(v.x * mirror, v.y, v.z);
                Transform upper = Bone("UpperLeg." + side), lower = Bone("LowerLeg." + side), foot = Bone("Foot." + side);
                // El pie cuelga de Root, no de la pierna: se guarda dónde está respecto de la pantorrilla y se lo lleva con ella.
                Vector3 ankle = lower.InverseTransformPoint(foot.position);
                Aim(character, upper, lower.position, Side(UpperLeg));
                Aim(character, lower, lower.TransformPoint(ankle), LowerLeg);
                foot.position = lower.TransformPoint(ankle);
                Transform arm = Bone("UpperArm." + side), forearm = Bone("LowerArm." + side);
                Aim(character, arm, forearm.position, Side(driving ? DriveUpperArm : RideUpperArm));
                Aim(character, forearm, Bone("Wrist." + side).position, Side(driving ? DriveLowerArm : RideLowerArm));
            }
            // La cadera queda sobre el cojín, un poco hacia atrás: la cabeza cabe bajo el techo.
            Vector3 hips = Bone("Hips").position;
            character.position += seat.position + car.up * .04f - car.forward * .08f - hips;
        }

        private static void Aim(Transform character, Transform bone, Vector3 point, Vector3 desiredLocal)
        {
            Vector3 desired = character.rotation * desiredLocal;
            bone.rotation = Quaternion.FromToRotation(point - bone.position, desired) * bone.rotation;
        }
    }
}
