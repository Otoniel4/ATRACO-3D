using UnityEngine;

namespace Alarma.Vehicles
{
    // Luces traseras que se intensifican al frenar e intermitentes que parpadean del lado al que dobla el auto.
    // Solo toca materiales cuando algo cambia.
    public sealed class CarLights : MonoBehaviour
    {
        private static readonly int Emission = Shader.PropertyToID("_EmissionColor");
        private const float BlinkRate = 1.6f;

        [SerializeField] private MonoBehaviour stateSource; // implementa IVehicleState
        [SerializeField] private Renderer[] tail, left, right;
        [SerializeField] private Color tailColor = new Color(.91f, .2f, .17f), amber = new Color(1f, .64f, .12f);
        [SerializeField, Min(0f)] private float tailIdle = 1.2f, tailBrake = 4f, indicatorOn = 3f;
        private IVehicleState state;
        private MaterialPropertyBlock block;
        private bool started, braking, blink;
        private int signal;

        public void Configure(MonoBehaviour source, Renderer[] tailLights, Renderer[] leftIndicators, Renderer[] rightIndicators)
        {
            stateSource = source; tail = tailLights; left = leftIndicators; right = rightIndicators;
        }

        private void Awake()
        {
            state = stateSource as IVehicleState;
            block = new MaterialPropertyBlock();
        }

        private void Update()
        {
            bool nowBraking = state != null && state.Braking;
            int nowSignal = state != null ? state.TurnSignal : 0;
            bool nowBlink = nowSignal != 0 && Mathf.Repeat(Time.time * BlinkRate, 1f) < .5f;
            if (!started || nowBraking != braking) Glow(tail, tailColor * (nowBraking ? tailBrake : tailIdle));
            if (!started || nowSignal != signal || nowBlink != blink)
            {
                Glow(left, amber * (nowBlink && nowSignal < 0 ? indicatorOn : 0f));
                Glow(right, amber * (nowBlink && nowSignal > 0 ? indicatorOn : 0f));
            }
            started = true; braking = nowBraking; signal = nowSignal; blink = nowBlink;
        }

        private void Glow(Renderer[] renderers, Color color)
        {
            block.SetColor(Emission, color);
            foreach (var r in renderers) r.SetPropertyBlock(block);
        }
    }
}
