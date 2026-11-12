using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Datos del objeto en metros y ejes Unity; no dependen de la orientación de quien lo sostiene.
    [CreateAssetMenu(menuName = "Alarma/Ciudad/Objeto de negocio")]
    public sealed class ShopProductDefinition : ScriptableObject
    {
        public string Id, Business;
        public GameObject Model;
        public Vector3 Support, RightGrip, LeftGrip;
        public Vector3 Fingers = Vector3.up, PalmNormal = Vector3.left;
        public Vector3 LeftFingers = Vector3.forward, LeftNormal = Vector3.up;
        [Range(0f, 2.5f)] public float FingerCurl = 1f;
        public bool TwoHands;
        // Cómo cierra los dedos la mano que lo sujeta. Vacío: cierre parejo según FingerCurl.
        public HandPose Hand;
    }
}
