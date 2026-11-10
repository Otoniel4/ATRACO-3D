using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;

namespace Alarma.AI.Reactions
{
    // En cada civil de la población (peatones, clientes y personal): oye los disparos y nota cuando le apuntan, le
    // disparan o le dan con el táser. Al primer motivo lo reemplaza en el mismo lugar, con la misma pose, por su doble
    // de reacción (NpcReactions) y le pasa el motivo. La población sigue con su lógica sin cambios: el civil original
    // queda oculto hasta que ella lo recicle, y el doble no desaparece a mitad de la reacción.
    public sealed class NpcReactionTrigger : MonoBehaviour, IIntimidatable, IDamageable, IItemTarget
    {
        [SerializeField] private NpcReactions doublePrefab;
        [SerializeField] private NoiseChannel noise;
        [SerializeField, Tooltip("Cuerpo animado del civil (de ahí se copia la pose).")] private Transform visual;
        private NpcReactions spawned;

        public void Configure(NpcReactions reactionDouble, NoiseChannel channel, Transform body)
        {
            doublePrefab = reactionDouble; noise = channel; visual = body;
        }

        private void OnEnable() { spawned = null; if (noise != null) noise.Raised += OnNoise; }
        private void OnDisable() { if (noise != null) noise.Raised -= OnNoise; }

        private void OnNoise(NoiseEvent sound)
        {
            float radius = NoiseReach.RadiusAt(sound, transform.position); // con una pared en medio llega menos o nada
            if ((sound.Position - transform.position).sqrMagnitude <= radius * radius) Swap()?.Hear(sound);
        }

        public void BeginIntimidation(GameObject instigator) => Swap()?.BeginIntimidation(instigator);
        // Quien apuntaba sigue teniendo a este civil como objetivo aunque ya lo reemplazó su doble: se lo avisa al doble.
        public void EndIntimidation(GameObject instigator) { if (spawned != null) spawned.EndIntimidation(instigator); }
        public void TakeDamage(float amount, GameObject instigator) => Swap()?.TakeDamage(amount, instigator);
        public bool Accepts(string itemId) => itemId == "taser";
        public string UseItem(string itemId, GameObject user) { var reaction = Swap(); return reaction != null ? reaction.UseItem(itemId, user) : ""; }

        private NpcReactions Swap()
        {
            if (doublePrefab == null || !isActiveAndEnabled) return null;
            var reaction = Instantiate(doublePrefab, transform.position, transform.rotation);
            reaction.name = doublePrefab.name + " (reacción)";
            if (visual != null) reaction.CopyPose(visual);
            gameObject.SetActive(false);
            spawned = reaction;
            return reaction;
        }
    }
}
