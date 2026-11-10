using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Posturas del doble de reacción; cada una es un estado del Animator con el mismo nombre (NpcReactionAssets).
    public enum ReactionPose { Quieto = 0, Correr = 1, Caminar = 2, Suplicar = 3, Rendido = 4, Amarrado = 5, LevantarseEspalda = 6, LevantarseBoca = 7, Grabar = 8 }

    // Único componente que cambia el Animator del doble: pide la postura con el parámetro «Reaccion». Así NetworkAnimator
    // podrá sincronizarla cuando llegue la red.
    public sealed class NpcReactionAnimator : MonoBehaviour
    {
        public const string Parameter = "Reaccion";
        private static readonly int ParameterId = Animator.StringToHash(Parameter);
        [SerializeField] private Animator animator;

        public Animator Body => animator;

        public void Configure(Animator body) => animator = body;

        public void Show(ReactionPose pose)
        {
            if (animator != null && animator.isActiveAndEnabled) animator.SetInteger(ParameterId, (int)pose);
        }

        // Al volver de la caída: el Animator se reactiva directo en la postura, sin transición (la mezcla la hace NpcRagdoll).
        public void Resume(ReactionPose pose)
        {
            if (animator == null) return;
            animator.enabled = true;
            animator.SetInteger(ParameterId, (int)pose);
            animator.Play(pose.ToString(), 0, 0f);
        }
    }
}
