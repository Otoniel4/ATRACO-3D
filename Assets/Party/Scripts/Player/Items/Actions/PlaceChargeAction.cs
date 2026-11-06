using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Player.Items
{
    // Termita: se apoya en la puerta o el suelo que se mira (hasta 2 m), su luz parpadea durante la mecha y luego arde.
    // Si quedó pegada a un IItemTarget (la bóveda del banco), le avisa al encenderse. Se gasta al colocarla.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Acción: colocar carga", fileName = "Action_PlaceCharge")]
    public sealed class PlaceChargeAction : ItemAction
    {
        [SerializeField, Min(.5f)] private float reach = 2f;
        [SerializeField, Min(0)] private float fuse = 3f;
        [SerializeField, Min(1)] private float burnSeconds = 6f;

        public void Configure(float distance, float seconds, float burn) { reach = distance; fuse = seconds; burnSeconds = burn; }

        public override void Trigger(ItemActionContext context)
        {
            Vector3 point, normal;
            Collider surface = null;
            var origin = context.User.transform.position + Vector3.up * 1.2f;
            if (Physics.Raycast(context.Aim, out var aimed, 30f, context.HitMask, QueryTriggerInteraction.Ignore) && Vector3.Distance(aimed.point, origin) <= reach)
            { point = aimed.point; normal = aimed.normal; surface = aimed.collider; }
            else if (Physics.Raycast(origin + context.User.transform.forward * .6f, Vector3.down, out var ground, 3f, context.HitMask, QueryTriggerInteraction.Ignore))
            { point = ground.point; normal = ground.normal; }
            else { context.Feedback?.Invoke("No hay dónde apoyar la termita"); return; }
            if (!context.Consume()) return;
            var charge = Instantiate(context.Item.HandModel, point + normal * .1f, Quaternion.FromToRotation(Vector3.up, normal));
            charge.name = "Termita colocada";
            Renderer led = null;
            foreach (var r in charge.GetComponentsInChildren<Renderer>())
                if (r.name.StartsWith("TimerLed")) led = r;
            var target = surface != null ? surface.GetComponentInParent<IItemTarget>() : null;
            string itemId = context.Item.Id;
            var user = context.User;
            charge.AddComponent<FusedCharge>().Arm(fuse, position =>
            {
                ItemEffects.Burn(position + normal * .12f, burnSeconds);
                if (target != null && target.Accepts(itemId)) target.UseItem(itemId, user);
                charge.AddComponent<TimedEffect>().Play(burnSeconds, 1f, .6f);
            }, led);
            context.Feedback?.Invoke(target != null && target.Accepts(itemId) ? "Termita colocada: ¡aléjate!" : "Termita colocada");
        }
    }
}
