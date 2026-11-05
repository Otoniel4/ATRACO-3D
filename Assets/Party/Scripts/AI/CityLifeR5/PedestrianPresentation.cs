using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class PedestrianPresentation : MonoBehaviour
    {
        [SerializeField] private Animator animator;
        [SerializeField] private GameObject bag;
        // Giro de la bolsa respecto del cuerpo en la pose de reposo, cuando cuelga bien de la mano.
        [SerializeField] private Quaternion bagRest = Quaternion.identity;
        private static readonly int Speed = Animator.StringToHash("Speed");
        private static readonly int Rate = Animator.StringToHash("WalkRate");
        private static readonly int Browse = Animator.StringToHash("Browse");
        private static readonly int Pay = Animator.StringToHash("Pay");
        private static readonly int Carry = Animator.StringToHash("Carry");
        public void Configure(Animator target, GameObject shoppingBag)
        {
            animator = target; bag = shoppingBag;
            if (animator != null) animator.applyRootMotion = false;
            if (bag != null) bagRest = Quaternion.Inverse(transform.rotation) * bag.transform.rotation;
        }
        public void WalkOnly(float speed)
        {
            if(bag!=null)bag.SetActive(false);if(animator==null)return;
            animator.SetFloat(Speed,speed>.08f?1.6f:0);animator.speed=speed>.08f?speed/1.6f:1;animator.SetFloat(Rate,speed);
            animator.SetBool(Browse,false);animator.SetBool(Pay,false);animator.SetBool(Carry,false);
        }
        public void Refresh(PedestrianRoutine routine, float speed)
        {
            if (bag != null) bag.SetActive(routine.HoldingBag);
            if (animator == null) return;
            animator.SetFloat(Speed,speed>.08f?1.6f:0);animator.speed=speed>.08f && !routine.Interaction?speed/1.6f:1;animator.SetFloat(Rate,speed);
            animator.SetBool(Browse, (routine.State == PedestrianState.Browsing || routine.State==PedestrianState.PickingUp) && speed < .1f);
            // Gesto de pagar solo al entregar el dinero y recibir el vuelto; el resto del mostrador lo hacen las manos.
            animator.SetBool(Pay, routine.State==PedestrianState.Paying || routine.State==PedestrianState.ReceivingReceipt);
            animator.SetBool(Carry, routine.Carrying);
        }
        // La bolsa cuelga del agarre de la mano. Algunos clips (como Idle) la animan hacia la espalda, así que después
        // del Animator se vuelve a colocar en la palma con el giro que tenía colgando en reposo.
        private void LateUpdate()
        {
            if (bag == null || !bag.activeSelf || bag.transform.parent == null) return;
            bag.transform.SetPositionAndRotation(bag.transform.parent.position, transform.rotation * bagRest);
        }
        public void ResetView() { if (bag != null) bag.SetActive(false); if (animator != null && animator.gameObject.activeInHierarchy) { animator.speed=1;animator.Rebind(); animator.Update(0); } }
    }
}
