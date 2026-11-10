using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;
using Alarma.Player.Items;

namespace Alarma.Police
{
    // Pistola del agente: aparece en la mano al apuntar, mira siempre al punto apuntado y dispara un rayo con
    // dispersión que daña a lo que implemente IDamageable. Usa los mismos efectos y el mismo canal de ruido que las
    // armas del jugador. No decide cuándo disparar: eso es del estado del agente.
    public sealed class PoliceSidearm : MonoBehaviour
    {
        private static readonly Color Flash = new Color(1f, .82f, .4f), Trail = new Color(1f, .9f, .6f);
        [SerializeField, Tooltip("Pistola en la mano (hija del agarre de la mano derecha).")] private Transform holder;
        [SerializeField] private Transform muzzle;
        [SerializeField] private NoiseChannel noise;
        [SerializeField] private PoliceSettings settings;
        [SerializeField, Tooltip("Lo que reciben las balas: todo menos otros NPC (29) y la interfaz (31).")]
        private LayerMask hitMask = ~((1 << 29) | (1 << 31));
        private Vector3 aimPoint;
        private bool drawn;

        public void Configure(Transform pistol, Transform muzzlePoint, NoiseChannel channel, PoliceSettings policeSettings)
        {
            holder = pistol; muzzle = muzzlePoint; noise = channel; settings = policeSettings;
        }

        public void Draw() { drawn = true; if (holder != null) holder.gameObject.SetActive(true); }
        public void Holster() { drawn = false; if (holder != null) holder.gameObject.SetActive(false); }
        public void AimAt(Vector3 point) => aimPoint = point;

        // Después del Animator: el cañón queda hacia el punto apuntado aunque la mano no esté perfecta.
        private void LateUpdate()
        {
            if (!drawn || holder == null) return;
            Vector3 direction = aimPoint - holder.position;
            if (direction.sqrMagnitude > .01f) holder.rotation = Quaternion.LookRotation(direction);
        }

        public void Fire(GameObject shooter)
        {
            if (muzzle == null) return;
            Vector3 from = muzzle.position;
            Vector3 straight = (aimPoint - from).normalized;
            Vector3 direction = Quaternion.AngleAxis(Random.Range(0f, 360f), straight)
                                * Quaternion.AngleAxis(Random.Range(0f, settings.Spread), Vector3.Cross(straight, Vector3.up).normalized) * straight;
            float range = settings.ShootRange * 2f;
            bool hit = Physics.Raycast(from, direction, out var impact, range, hitMask, QueryTriggerInteraction.Ignore);
            ItemEffects.MuzzleFlash(from, direction, Flash);
            ItemEffects.Tracer(from, hit ? impact.point : from + direction * range, Trail);
            if (hit)
            {
                var target = impact.collider.GetComponentInParent<IDamageable>();
                target?.TakeDamage(settings.Damage, shooter);
                ItemEffects.Impact(impact.point, impact.normal, impact.collider.transform, target == null);
            }
            if (noise != null) noise.Raise(from, settings.GunshotRadius, NoiseKind.Gunshot, shooter);
        }
    }
}
