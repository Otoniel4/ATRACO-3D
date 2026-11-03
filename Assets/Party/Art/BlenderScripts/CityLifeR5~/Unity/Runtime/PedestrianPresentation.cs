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
        public void Refresh(PedestrianRoutine routine, float speed)
        {
            if (bag != null) bag.SetActive(routine.Carrying);
            if (animator == null) return;
            animator.SetFloat(Speed, speed); animator.SetFloat(Rate, Mathf.Clamp(speed, .2f, 1.6f));
            animator.SetBool(Browse, routine.State == PedestrianState.Browsing && speed < .1f);
            animator.SetBool(Pay, routine.State == PedestrianState.Paying);
            animator.SetBool(Carry, routine.Carrying);
        }
        public void ResetView() { if (bag != null) bag.SetActive(false); if (animator != null && animator.gameObject.activeInHierarchy) { animator.Rebind(); animator.Update(0); } }
    }
}
