using UnityEngine;

namespace Alarma.AI.Reactions
{
    // Medidor de valentía de un civil (0 = aterrado, 1 = valiente): los disparos y que le apunten lo bajan; se recupera
    // de a poco cuando la amenaza se aleja. Decide si se agacha pidiendo piedad o si huye.
    public sealed class NpcBravery
    {
        private readonly float cowerBelow;

        public float Value { get; private set; }
        public bool Cowers => Value < cowerBelow;

        public NpcBravery(float start, float cowerThreshold) { Value = Mathf.Clamp01(start); cowerBelow = cowerThreshold; }

        public void Frighten(float amount) => Value = Mathf.Clamp01(Value - Mathf.Max(0f, amount));
        public void Recover(float amount) => Value = Mathf.Clamp01(Value + Mathf.Max(0f, amount));

        // Miedo de un ruido: completo a quemarropa y nada en el borde de su alcance.
        public static float FearAt(float distance, float radius, float fear) => radius <= 0f ? 0f : fear * Mathf.Clamp01(1f - distance / radius);
    }
}
