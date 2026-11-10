using UnityEngine;

namespace Alarma.AI.Security
{
    // Posturas del guardia; cada una es un estado del Animator con el mismo nombre (GuardAssets).
    public enum GuardPose { Quieto = 0, Caminar = 1, Correr = 2, Golpear = 3, LevantarseEspalda = 4, LevantarseBoca = 5 }

    // Lo que se ve del guardia: su postura (único lugar que cambia el Animator, con el parámetro «Guardia», para que
    // NetworkAnimator pueda sincronizarlo) y la porra en la mano, que se levanta y baja con el golpe.
    public sealed class GuardBody : MonoBehaviour
    {
        public const string Parameter = "Guardia";
        private const float Carried = 25f, Raised = -55f, Lowered = 85f; // inclinación de la porra hacia adelante, en grados
        private static readonly int ParameterId = Animator.StringToHash(Parameter);
        [SerializeField] private Animator animator;
        [SerializeField, Tooltip("Porra en la mano (hija del agarre de la mano derecha), apagada en el puesto.")] private Transform baton;
        private float tilt = Carried;

        public void Configure(Animator body, Transform batonInHand) { animator = body; baton = batonInHand; }

        public void Show(GuardPose pose)
        {
            if (animator != null && animator.isActiveAndEnabled) animator.SetInteger(ParameterId, (int)pose);
        }

        // Al volver de la caída: el Animator se reactiva directo en la postura, sin transición (la mezcla la hace NpcRagdoll).
        public void Resume(GuardPose pose)
        {
            if (animator == null) return;
            animator.enabled = true;
            animator.SetInteger(ParameterId, (int)pose);
            animator.Play(pose.ToString(), 0, 0f);
        }

        public void DrawBaton(bool drawn) { if (baton != null) baton.gameObject.SetActive(drawn); tilt = Carried; }

        // Avance del golpe de 0 a 1: la porra sube atrás hasta «hitAt» y de ahí baja de golpe.
        public void Swing(float t, float hitAt)
            => tilt = t < hitAt ? Mathf.Lerp(Carried, Raised, t / Mathf.Max(.01f, hitAt)) : Mathf.Lerp(Raised, Lowered, Mathf.Clamp01((t - hitAt) / .15f));

        public void RestBaton() => tilt = Carried;

        // Después del Animator: la porra sigue a la mano y se inclina según el golpe, respecto del frente del guardia.
        private void LateUpdate()
        {
            if (baton != null && baton.gameObject.activeSelf) baton.rotation = transform.rotation * Quaternion.Euler(tilt, 0f, 0f);
        }
    }
}
