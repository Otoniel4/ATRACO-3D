using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Una forma de cerrar la mano para sujetar algo (cilindro, caja, pinza, plano, asa). Los ángulos salen de Blender
    // (Art/BlenderScripts/build_hand_poses.py), ajustados sobre la mano del elenco contra un objeto de prueba. Cada
    // vector trae la flexión en grados de las tres articulaciones del dedo, de la base a la punta. Una pose nueva es
    // un asset nuevo: el código que cierra los dedos no cambia.
    [CreateAssetMenu(menuName = "Alarma/Ciudad/Pose de mano")]
    public sealed class HandPose : ScriptableObject
    {
        public const int Fingers = 5, Joints = 3;
        public string Id;
        public Vector3 Thumb, Index, Middle, Ring, Pinky;
        private float[] angles;

        // Los quince ángulos en el orden pulgar, índice, medio, anular y meñique (el que usa CommerceFingerPose).
        public float[] Angles => angles ??= new[]
        {
            Thumb.x, Thumb.y, Thumb.z, Index.x, Index.y, Index.z, Middle.x, Middle.y, Middle.z,
            Ring.x, Ring.y, Ring.z, Pinky.x, Pinky.y, Pinky.z,
        };

        private void OnValidate() => angles = null;
    }
}
