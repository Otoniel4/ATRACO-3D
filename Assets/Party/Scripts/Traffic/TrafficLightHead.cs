using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Traffic
{
    // Las tres luces de un semáforo; solo cambia materiales cuando cambia el color.
    public sealed class TrafficLightHead : MonoBehaviour
    {
        [SerializeField] private int signal = -1, axis;
        [SerializeField] private Renderer red, yellow, green;
        [SerializeField] private Material off, redOn, yellowOn, greenOn;
        private bool shown;
        private SignalLight current;

        public int Signal => signal;
        public int Axis => axis;

        public void ConfigureLamps(Renderer redLamp, Renderer yellowLamp, Renderer greenLamp, Material dark, Material redLit, Material yellowLit, Material greenLit)
        {
            red = redLamp; yellow = yellowLamp; green = greenLamp; off = dark; redOn = redLit; yellowOn = yellowLit; greenOn = greenLit;
        }

        public void Assign(int signalIndex, int axisIndex) { signal = signalIndex; axis = axisIndex; }

        public void Show(SignalLight light)
        {
            if (shown && current == light) return;
            shown = true; current = light;
            red.sharedMaterial = light == SignalLight.Red ? redOn : off;
            yellow.sharedMaterial = light == SignalLight.Yellow ? yellowOn : off;
            green.sharedMaterial = light == SignalLight.Green ? greenOn : off;
        }
    }
}
