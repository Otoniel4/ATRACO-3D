using System;
using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Traffic
{
    // Reloj de todos los semáforos: cada cruce reparte el verde entre sus ejes por turnos.
    // El estado sale del tiempo y no se guarda por cruce: en red bastará con que todos usen el reloj del host.
    public sealed class TrafficSignalNetwork : MonoBehaviour, ITrafficSignals
    {
        [SerializeField] private TrafficSignalTiming timing;
        [SerializeField] private int[] axisCount = Array.Empty<int>();
        [SerializeField] private float[] offsets = Array.Empty<float>();
        [SerializeField] private TrafficLightHead[] heads = Array.Empty<TrafficLightHead>();

        public int Count => axisCount.Length;

        public void Configure(TrafficSignalTiming signalTiming, int[] axes, float[] startOffsets, TrafficLightHead[] lights)
        {
            timing = signalTiming; axisCount = axes; offsets = startOffsets; heads = lights;
        }

        public SignalLight Light(int signal, int axis)
        {
            float slot = timing.Slot;
            float t = Mathf.Repeat(Time.time + offsets[signal], slot * axisCount[signal]);
            int phase = (int)(t / slot);
            if (phase != axis) return SignalLight.Red;
            float inSlot = t - phase * slot;
            return inSlot < timing.Green ? SignalLight.Green : inSlot < timing.Green + timing.Yellow ? SignalLight.Yellow : SignalLight.Red;
        }

        public float SecondsUntilGreen(int signal, int axis)
        {
            if (Light(signal, axis) != SignalLight.Red) return 0f;
            float slot = timing.Slot, cycle = slot * axisCount[signal];
            float t = Mathf.Repeat(Time.time + offsets[signal], cycle);
            return Mathf.Repeat(axis * slot - t, cycle);
        }

        private void Update()
        {
            foreach (var head in heads)
                if (head != null && head.isActiveAndEnabled) head.Show(Light(head.Signal, head.Axis));
        }
    }
}
