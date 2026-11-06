using UnityEngine;
using UnityEngine.UI;
using Alarma.Player.Items;
using Alarma.UI.Map;

namespace Alarma.UI.Hud
{
    // Mira en el centro de la pantalla: aparece solo mientras se apunta un arma con clic derecho.
    public sealed class CrosshairView : MonoBehaviour
    {
        [SerializeField] private ItemUser user;
        private RectTransform[] arms;
        private Image dot;
        private GameObject root;

        public void Configure(ItemUser itemUser) => user = itemUser;

        private void Start()
        {
            if (user == null) { enabled = false; return; }
            var canvas = MapUi.Canvas("Mira", transform, 36);
            root = canvas.gameObject;
            dot = MapUi.Panel("Punto", canvas.transform, Color.white);
            dot.rectTransform.anchorMin = dot.rectTransform.anchorMax = new Vector2(.5f, .5f);
            dot.rectTransform.sizeDelta = new Vector2(5, 5);
            arms = new RectTransform[4];
            for (int i = 0; i < 4; i++)
            {
                var arm = MapUi.Panel("Brazo", canvas.transform, Color.white).rectTransform;
                arm.anchorMin = arm.anchorMax = new Vector2(.5f, .5f);
                arm.sizeDelta = i < 2 ? new Vector2(3, 14) : new Vector2(14, 3);
                arm.gameObject.AddComponent<Shadow>().effectColor = new Color(0, 0, 0, .6f);
                arms[i] = arm;
            }
        }

        private void Update()
        {
            if (root == null) return;
            // Solo mientras se apunta con clic derecho: aparece y se cierra al subir el arma.
            float aim = user.HoldingFirearm ? user.AimWeight : 0f;
            dot.color = new Color(1, 1, 1, .9f * aim);
            float gap = Mathf.Lerp(20f, 9f, aim);
            Vector2[] places = { new Vector2(0, gap), new Vector2(0, -gap), new Vector2(gap, 0), new Vector2(-gap, 0) };
            for (int i = 0; i < 4; i++)
            {
                arms[i].anchoredPosition = places[i];
                arms[i].GetComponent<Image>().color = new Color(1, 1, 1, .95f * aim);
            }
        }
    }
}
