using UnityEngine;

namespace Alarma.AI.CityLife
{
    public sealed class PedestrianPresentation : MonoBehaviour
    {
        [SerializeField] private Animator animator;
        [SerializeField] private GameObject bag;
        private static readonly int Speed = Animator.StringToHash("Speed");
        private static readonly int Rate = Animator.StringToHash("WalkRate");
        private static readonly int Browse = Animator.StringToHash("Browse");
        private static readonly int Pay = Animator.StringToHash("Pay");
        private static readonly int Carry = Animator.StringToHash("Carry");
        public void Configure(Animator target, GameObject shoppingBag) { animator = target; bag = shoppingBag; if (animator != null) animator.applyRootMotion = false; }
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
            animator.SetBool(Pay, routine.Interaction && routine.State!=PedestrianState.PickingUp);
            animator.SetBool(Carry, routine.Carrying);
        }
        public void ResetView() { if (bag != null) bag.SetActive(false); if (animator != null && animator.gameObject.activeInHierarchy) { animator.speed=1;animator.Rebind(); animator.Update(0); } }
    }
}
