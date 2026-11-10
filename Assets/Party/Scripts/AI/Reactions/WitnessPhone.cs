using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Lo que se ve de un testigo que graba y llama: el celular en la mano y, sobre su cabeza, la barra de la llamada que
    // se va llenando (siempre de cara a la cámara). El celular tiene dos agarres, como en una persona: para grabar va de
    // pie entre los dedos y el pulgar; para hablar, a lo largo de la palma. Al cambiar se acomoda de uno a otro en un
    // cuarto de segundo. Lo arma el editor (NpcReactionAssets); NpcReactions solo le dice cuánto va la llamada, si ya
    // está hablando, o que lo esconda.
    public sealed class WitnessPhone : MonoBehaviour
    {
        private const float RegripSeconds = .25f; // igual que REGRIP en build_npc_reaction_clips.py
        [SerializeField] private GameObject phone;
        [SerializeField] private Transform bar, fill;
        [SerializeField, Tooltip("Ancho de la barra llena, en metros.")] private float width = .5f;
        [SerializeField, Tooltip("Dónde va el celular respecto de la muñeca al grabar y al hablar.")] private Pose filmGrip, callGrip;
        private bool calling;
        private float grip; // 0 = agarre de grabar, 1 = agarre de hablar

        public void Configure(GameObject phoneModel, Transform barRoot, Transform barFill, float barWidth, Pose film, Pose call)
        {
            phone = phoneModel; bar = barRoot; fill = barFill; width = barWidth; filmGrip = film; callGrip = call;
        }

        public void Show(float progress, bool onCall)
        {
            float filled = width * Mathf.Clamp01(progress);
            calling = onCall;
            if (!phone.activeSelf) { grip = onCall ? 1f : 0f; Hold(); } // recién lo saca: ya en su agarre
            phone.SetActive(true);
            bar.gameObject.SetActive(true);
            fill.localScale = new Vector3(filled, fill.localScale.y, 1f);
            fill.localPosition = new Vector3((filled - width) * .5f, 0f, -.002f); // crece desde la izquierda, delante del fondo
        }

        public void Hide()
        {
            phone.SetActive(false);
            bar.gameObject.SetActive(false);
        }

        private void LateUpdate()
        {
            if (!phone.activeSelf) return;
            float target = calling ? 1f : 0f;
            if (!Mathf.Approximately(grip, target))
            {
                grip = Mathf.MoveTowards(grip, target, Time.deltaTime / RegripSeconds);
                Hold();
            }
            var view = Camera.main;
            if (view != null) bar.rotation = view.transform.rotation;
        }

        private void Hold()
        {
            float t = Mathf.SmoothStep(0f, 1f, grip);
            phone.transform.localPosition = Vector3.Lerp(filmGrip.position, callGrip.position, t);
            phone.transform.localRotation = Quaternion.Slerp(filmGrip.rotation, callGrip.rotation, t);
        }
    }
}
