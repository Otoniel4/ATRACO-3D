using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;

namespace Alarma.Player.Items
{
    // Disparo de pistola, escopeta, rifle o táser: rayo desde la mira con dispersión (menor al apuntar), fogonazo,
    // trazador e impacto. Daña lo que implementa IDamageable; el táser no daña: aturde a un IItemTarget con su dardo.
    // La escopeta mueve su corredera después de cada tiro.
    [CreateAssetMenu(menuName = "Alarma/Inventario/Acción: disparar", fileName = "Action_Firearm")]
    public sealed class FirearmAction : ItemAction
    {
        [SerializeField, Min(0)] private float damage = 25f;
        [SerializeField, Min(1)] private float range = 60f;
        [SerializeField, Min(1)] private int pellets = 1;
        [SerializeField, Tooltip("Dispersión en grados al disparar sin apuntar.")] private float hipSpread = 4f;
        [SerializeField, Tooltip("Dispersión en grados apuntando con clic derecho.")] private float aimSpread = .6f;
        [SerializeField] private Color flash = new Color(1f, .82f, .4f), tracer = new Color(1f, .9f, .6f);
        [SerializeField, Tooltip("Táser: dardo con cable que aturde en vez de dañar.")] private bool stun;
        [SerializeField, Tooltip("Pieza que va y vuelve después del tiro (Pump de la escopeta).")] private string pumpPart = "";
        [SerializeField] private float pumpTravel = .07f;

        public override bool CanAim => true;

        public void Configure(float hit, float reach, int shots, float hip, float aimed, bool stuns, string pump, Color light, Color trail)
        {
            damage = hit; range = reach; pellets = Mathf.Max(1, shots); hipSpread = hip; aimSpread = aimed; stun = stuns; pumpPart = pump; flash = light; tracer = trail;
        }

        public override void Trigger(ItemActionContext context)
        {
            Vector3 muzzle = context.MuzzleOr(context.Model.position);
            ItemEffects.MuzzleFlash(muzzle, context.Forward, flash);
            float spread = Mathf.Lerp(hipSpread, aimSpread, context.Aiming);
            for (int i = 0; i < pellets; i++)
            {
                Vector3 direction = Quaternion.AngleAxis(Random.Range(0f, 360f), context.Aim.direction)
                                    * Quaternion.AngleAxis(Random.Range(0f, spread), Vector3.Cross(context.Aim.direction, Vector3.up).normalized)
                                    * context.Aim.direction;
                // Primero desde la cámara (adonde mira la mira) y luego desde el cañón, por si algo se interpone.
                Vector3 point = Physics.Raycast(context.Aim.origin, direction, out var aimHit, range, context.HitMask, QueryTriggerInteraction.Ignore)
                    ? aimHit.point : context.Aim.origin + direction * range;
                Vector3 toPoint = point - muzzle;
                bool hitSomething = Physics.Raycast(muzzle, toPoint.normalized, out var hit, toPoint.magnitude + .05f, context.HitMask, QueryTriggerInteraction.Ignore);
                Vector3 end = hitSomething ? hit.point : point;
                ItemEffects.Tracer(muzzle, end, stun ? new Color(.35f, .7f, 1f) : tracer, stun ? .004f : .012f, stun ? .35f : .06f);
                if (!hitSomething) continue;
                if (stun)
                {
                    var target = hit.collider.GetComponentInParent<IItemTarget>();
                    context.Feedback?.Invoke(target != null && target.Accepts(context.Item.Id) ? target.UseItem(context.Item.Id, context.User) : "El dardo no alcanzó a nadie");
                }
                else
                {
                    hit.collider.GetComponentInParent<IDamageable>()?.TakeDamage(damage / pellets, context.User);
                    // Las personas (tienen Animator) no guardan agujeros: al moverse quedarían flotando en el aire.
                    bool person = hit.collider.GetComponentInParent<Animator>() != null || hit.collider.GetComponentInChildren<Animator>() != null
                                  || hit.collider.GetComponentInParent<IDamageable>() != null;
                    ItemEffects.Impact(hit.point, hit.normal, hit.collider.transform, !person);
                }
            }
            // El ruido va después de los impactos: quien lo oye puede cambiar de cuerpo (doble de reacción) y la bala ya llegó.
            MakeNoise(muzzle, NoiseKind.Gunshot, context.User);
        }

        // Corredera de la escopeta: atrás y adelante en la segunda mitad de la animación.
        public override void Animate(ItemActionContext context, float t)
        {
            base.Animate(context, t);
            if (string.IsNullOrEmpty(pumpPart)) return;
            var part = context.Part(pumpPart);
            if (part == null) return;
            var rest = context.Rest(part);
            float k = t < .35f || t > .85f ? 0f : Mathf.Sin((t - .35f) / .5f * Mathf.PI);
            part.localPosition = rest.position + part.parent.InverseTransformDirection(-context.Forward) * (pumpTravel * k);
        }

        public override void Release(ItemActionContext context)
        {
            base.Release(context);
            var part = string.IsNullOrEmpty(pumpPart) ? null : context.Part(pumpPart);
            if (part != null) part.localPosition = context.Rest(part).position;
        }
    }
}
