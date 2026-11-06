using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Player.Items
{
    public enum BlastKind { Smoke, Flash, Emp }

    // Granadas: se lanzan hacia la mira, rebotan y a los segundos sueltan humo, un destello aturdidor o un pulso EMP.
    // Avisan a los IItemTarget cercanos (cámaras que se apagan, guardias aturdidos) y se gasta una del montón.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Acción: lanzar", fileName = "Action_Throw")]
    public sealed class ThrowAction : ItemAction
    {
        [SerializeField] private BlastKind blast;
        [SerializeField, Min(1)] private float speed = 13f;
        [SerializeField, Min(0)] private float fuse = 1.6f;
        [SerializeField, Min(.5f)] private float radius = 6f;
        [SerializeField, Min(1), Tooltip("Cuánto dura el humo, en segundos.")] private float smokeSeconds = 10f;

        public void Configure(BlastKind kind, float throwSpeed, float seconds, float area) { blast = kind; speed = throwSpeed; fuse = seconds; radius = area; }

        public override void Trigger(ItemActionContext context)
        {
            if (!context.Consume()) return;
            context.HideModel?.Invoke(true);
            var grenade = Instantiate(context.Item.HandModel, context.Model.position, context.Model.rotation);
            grenade.name = context.Item.DisplayName + " lanzada";
            var body = grenade.AddComponent<Rigidbody>();
            body.mass = .4f; body.interpolation = RigidbodyInterpolation.Interpolate; body.collisionDetectionMode = CollisionDetectionMode.Continuous;
            var collider = grenade.AddComponent<SphereCollider>();
            collider.radius = .05f;
            var userCollider = context.User.GetComponent<Collider>();
            if (userCollider != null) Physics.IgnoreCollision(collider, userCollider);
            body.linearVelocity = context.Aim.direction * speed + Vector3.up * 2.5f;
            body.angularVelocity = Random.insideUnitSphere * 8f;
            string itemId = context.Item.Id;
            var user = context.User;
            grenade.AddComponent<FusedCharge>().Arm(fuse, position =>
            {
                if (blast == BlastKind.Smoke) ItemEffects.Smoke(position, smokeSeconds);
                else if (blast == BlastKind.Flash) ItemEffects.Flash(position);
                else ItemEffects.EmpPulse(position);
                foreach (var near in Physics.OverlapSphere(position, radius, ~0, QueryTriggerInteraction.Collide))
                {
                    var target = near.GetComponentInParent<IItemTarget>();
                    if (target != null && target.Accepts(itemId)) target.UseItem(itemId, user);
                }
                Destroy(grenade);
            });
            context.Feedback?.Invoke(context.Item.DisplayName + " lanzada");
        }
    }
}
