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
            animator.SetBool(Browse,false);animator.SetBool(Carry,false);
        }
        public void Refresh(PedestrianRoutine routine, float speed, bool showBag = true)
        {
            if (bag != null) bag.SetActive(routine.HoldingBag && showBag);
            if (animator == null) return;
            animator.SetFloat(Speed,speed>.08f?1.6f:0);animator.speed=speed>.08f && !routine.Interaction?speed/1.6f:1;animator.SetFloat(Rate,speed);
            // Los clips de zancada (Browse, Pay) no se usan mientras el alcance mueve el cuerpo: al tomar el producto y en
            // todo el mostrador la persona queda parada (Idle) y PedestrianReach inclina el tronco y lleva la mano. Sumar
            // las dos cosas dejaba las piernas abiertas dentro del mueble y el torso doblado dos veces.
            animator.SetBool(Browse, routine.State == PedestrianState.Browsing && speed < .1f);
            // Con la bolsa colgando usa el estado de llevar; con un producto en la mano camina con el clip normal y la mano
            // la sostiene el alcance (el clip viejo de llevar daba zancadas de un metro).
            animator.SetBool(Carry, routine.Carrying && routine.HoldingBag && showBag);
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
