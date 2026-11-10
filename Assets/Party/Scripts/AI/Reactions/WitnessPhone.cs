using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Lo que se ve de un testigo que graba y llama: el celular en la mano y, sobre su cabeza, la barra de la llamada que
    // se va llenando (siempre de cara a la cámara). Lo arma el editor (NpcReactionAssets); NpcReactions solo le dice
    // cuánto va la llamada o que lo esconda.
    public sealed class WitnessPhone : MonoBehaviour
    {
        [SerializeField] private GameObject phone;
        [SerializeField] private Transform bar, fill;
        [SerializeField, Tooltip("Ancho de la barra llena, en metros.")] private float width = .5f;

        public void Configure(GameObject phoneModel, Transform barRoot, Transform barFill, float barWidth)
        {
            phone = phoneModel; bar = barRoot; fill = barFill; width = barWidth;
        }

        public void Show(float progress)
        {
            float filled = width * Mathf.Clamp01(progress);
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
            if (!bar.gameObject.activeSelf) return;
            var view = Camera.main;
            if (view != null) bar.rotation = view.transform.rotation;
        }
    }
}
