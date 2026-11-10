using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Player.Items
{
    // Herramienta de mano (palanca, ganzúa, taladro, cortavidrios, tablet, bridas, gancho): hace su animación y, al llegar
    // el momento del efecto, la usa sobre el IItemTarget que se mira (cerradura, caja, vitrina, cámara, empleado...).
    // Si no hay nada que la acepte, solo avisa. Las bridas se gastan solo cuando amarran a alguien y, como su animación
    // es un amarre con otra persona, ni siquiera empiezan si no hay a quién amarrar (requireTarget).
    [CreateAssetMenu(menuName = "Alarma/Inventario/Acción: herramienta", fileName = "Action_Tool")]
    public sealed class ToolAction : ItemAction
    {
        [SerializeField, Min(.5f), Tooltip("Hasta dónde llega, en metros.")] private float range = 1.8f;
        [SerializeField, Tooltip("Se gasta una unidad cuando el objetivo la acepta (bridas).")] private bool consumeOnUse;
        [SerializeField, Tooltip("Dibuja una cuerda hasta donde se enganchó (gancho).")] private bool rope;
        [SerializeField] private string nothingMessage = "Aquí no hay nada para usarla";
        [SerializeField, Tooltip("Solo empieza si hay un objetivo que la acepte al frente (la animación no tiene sentido en el aire).")] private bool requireTarget;

        public void Configure(float reach, bool consume, bool drawRope, string emptyMessage, bool needsTarget = false)
        {
            range = reach; consumeOnUse = consume; rope = drawRope; nothingMessage = emptyMessage; requireTarget = needsTarget;
        }

        public override bool CanBegin(ItemActionContext context)
        {
            var target = context.FindTarget(range, out _);
            if (target == null && requireTarget) { context.Feedback?.Invoke(nothingMessage); return false; }
            // El objetivo puede pedir dónde pararse (bridas: detrás de la persona) y prepararse para recibirla.
            if (target is IUseAnchor anchor && anchor.PrepareUse(context.Item.Id, context.User, out var standAt)) context.PlaceUser?.Invoke(standAt);
            return true;
        }

        public override void Trigger(ItemActionContext context)
        {
            if (rope && Physics.Raycast(context.Aim, out var anchor, range, context.HitMask, QueryTriggerInteraction.Ignore))
                ItemEffects.Tracer(context.Model.position, anchor.point, new Color(.69f, .54f, .35f), .015f, 1.4f);
            var target = context.FindTarget(range, out _);
            if (target == null) { context.Feedback?.Invoke(nothingMessage); return; }
            if (consumeOnUse && !context.Consume()) return;
            context.Feedback?.Invoke(target.UseItem(context.Item.Id, context.User));
        }
    }
}
