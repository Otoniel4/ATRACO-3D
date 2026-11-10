using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Una trayectoria por persona: dos clientes que toman productos nunca comparten el objetivo de la mano.
    public sealed class CommerceHandMotion
    {
        private Transform anchor;
        private Vector3 velocity;
        private bool tracking;
        private PedestrianReach owner;

        public void Follow(PedestrianReach hand, Vector3? point, float speed, float smoothing, bool fromAbove = false)
        {
            if (hand == null || !point.HasValue) { Release(); return; }
            if (owner != hand) { Release(); owner = hand; }
            if (anchor == null)
            {
                anchor = new GameObject("Trayectoria_Compra").transform;
                anchor.SetParent(hand.transform, false);
            }
            if (!tracking) { anchor.position = hand.PalmPosition; velocity = Vector3.zero; }
            anchor.position = Vector3.SmoothDamp(anchor.position, point.Value, ref velocity,
                Mathf.Max(.04f, smoothing), Mathf.Max(.2f, speed), Time.deltaTime);
            hand.ReachObject(anchor, fromAbove);
            tracking = true;
        }

        public void Release()
        {
            if (owner != null && anchor != null) owner.Release(anchor);
            velocity = Vector3.zero;
            tracking = false;
        }
    }
}
