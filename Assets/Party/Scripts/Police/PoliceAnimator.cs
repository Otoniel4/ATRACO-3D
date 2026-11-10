using UnityEngine;

namespace Alarma.Police
{
    // Posturas del agente; cada una es un estado del Animator con el mismo nombre (PoliceAssets).
    public enum PolicePose { Quieto = 0, Caminar = 1, Correr = 2, Apuntar = 3, Esposar = 4, LevantarseEspalda = 5, LevantarseBoca = 6 }

    // Único componente que cambia el Animator del agente: pide la postura con el parámetro «Policia». Así
    // NetworkAnimator podrá sincronizarla cuando llegue la red.
    public sealed class PoliceAnimator : MonoBehaviour
    {
        public const string Parameter = "Policia";
        private static readonly int ParameterId = Animator.StringToHash(Parameter);
        [SerializeField] private Animator animator;

        public void Configure(Animator body) => animator = body;

        public void Show(PolicePose pose)
        {
            if (animator != null && animator.isActiveAndEnabled) animator.SetInteger(ParameterId, (int)pose);
        }

        // Al volver de la caída: el Animator se reactiva directo en la postura, sin transición (la mezcla la hace NpcRagdoll).
        public void Resume(PolicePose pose)
        {
            if (animator == null) return;
            animator.enabled = true;
            animator.SetInteger(ParameterId, (int)pose);
            animator.Play(pose.ToString(), 0, 0f);
        }
    }
}
