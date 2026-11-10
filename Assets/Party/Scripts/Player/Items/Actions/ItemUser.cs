using System;
using UnityEngine;
using Alarma.Core.Contracts;

namespace Alarma.Player.Items
{
    // Usa el objeto que se tiene en la mano: clic derecho apunta las armas (y apuntarle a alguien lo intimida, GDD 8.1),
    // clic izquierdo dispara o usa la herramienta. Reproduce la acción del objeto (ItemAction) cuadro a cuadro: su
    // animación se suma a la pose de HeldItemView y su efecto ocurre en el momento indicado. Corre antes que HeldItemView.
    [DefaultExecutionOrder(80)]
    public sealed class ItemUser : MonoBehaviour, IArmed
    {
        private const float AimSpeed = 7f;
        [SerializeField] private PlayerInventory owner;
        [SerializeField] private HeldItemView view;
        [SerializeField, Tooltip("Componente que implementa IItemControls.")] private MonoBehaviour controlsSource;
        [SerializeField, Tooltip("Cámara: de ahí sale la mira.")] private Transform aimSource;
        [SerializeField, Tooltip("Capas que reciben disparos y herramientas: todo menos el jugador (30) y la interfaz (31). Los NPC (29) sí.")]
        private LayerMask hitMask = ~((1 << 30) | (1 << 31));
        private IItemControls controls;
        private ItemActionContext context;
        private GameObject contextModel;
        private ItemAction running;
        private float time, aim;
        private bool triggered;
        private IIntimidatable intimidated;

        public float AimWeight => aim;
        // Acción en curso (null al terminar): la escucha el componente que mueve el Animator (ItemActionAnimator).
        public event Action<ItemAction> ActionChanged;
        // Mientras dura una acción de cuerpo completo (palanca, ganzúa, termita…) el jugador no camina.
        public bool HoldsStill => running != null && running.FullBody;
        // El objetivo pidió dónde pararse antes de usarlo (bridas): lo atiende quien mueve al jugador.
        public event Action<Pose> PlacementRequested;
        public bool HoldingFirearm => view != null && view.Ready && view.HeldItem.Action != null && view.HeldItem.Action.CanAim;
        // Arma a la vista: los civiles rendidos esperan más para escapar mientras siga en la mano.
        public bool WeaponDrawn => HoldingFirearm;
        public event Action<string> Feedback;

        public void Configure(PlayerInventory playerInventory, HeldItemView heldView, IItemControls input, Transform camera)
        {
            owner = playerInventory; view = heldView; controlsSource = input as MonoBehaviour; aimSource = camera;
        }

        private void Start()
        {
            controls = controlsSource as IItemControls;
            if (owner == null || view == null || controls == null)
            {
                Debug.LogWarning("El uso de objetos no tiene inventario, mano o controles: usa Alarma > Crear y probar juego.", this);
                enabled = false;
            }
        }

        private void OnDisable() { Stop(); SetIntimidated(null); }

        private void Update()
        {
            var item = view.HeldItem;
            var action = item != null ? item.Action : null;
            bool ready = view.Ready && action != null;
            if (view.HeldModel != contextModel) { Stop(); contextModel = view.HeldModel; context = contextModel != null ? NewContext(item) : null; }
            if (!ready && running != null) Stop();

            bool aiming = ready && action.CanAim && controls.AimHeld;
            aim = Mathf.MoveTowards(aim, aiming ? 1f : 0f, Time.deltaTime * AimSpeed);
            view.SetAim(aim, AimPitch());
            SetIntimidated(aiming ? Aimed() : null);

            if (running == null && ready && (controls.UsePressed || (controls.UseHeld && action.RepeatWhileHeld)))
            {
                context.Aim = AimRay();
                if (action.CanBegin(context)) Begin(action);
            }
            if (running == null) { view.SetAction(ActionPose.None); return; }

            time += Time.deltaTime / running.Duration;
            context.Aim = AimRay();
            context.Aiming = aim;
            context.Forward = view.ItemForward;
            running.Animate(context, Mathf.Clamp01(time));
            if (!triggered && time >= running.TriggerAt) { triggered = true; running.Trigger(context); }
            view.SetAction(running.Evaluate(Mathf.Clamp01(time)));
            if (time < 1f) return;
            bool again = running.RepeatWhileHeld && controls.UseHeld && ready;
            var finished = running;
            Stop();
            if (again) Begin(finished);
        }

        private void Begin(ItemAction action) { running = action; time = 0f; triggered = false; ActionChanged?.Invoke(action); }

        private void Stop()
        {
            if (running != null && context != null) running.Release(context);
            bool wasRunning = running != null;
            running = null;
            view.HideModel(false);
            if (wasRunning) ActionChanged?.Invoke(null);
        }

        private ItemActionContext NewContext(ItemDefinition item) => new ItemActionContext
        {
            User = gameObject, Item = item, Model = contextModel.transform, HitMask = hitMask,
            Consume = () => owner.Inventory.ConsumeActive(),
            Feedback = message => { if (!string.IsNullOrEmpty(message)) Feedback?.Invoke(message); },
            HideModel = view.HideModel,
            PlaceUser = pose => PlacementRequested?.Invoke(pose),
        };

        private Ray AimRay()
        {
            if (aimSource != null) return new Ray(aimSource.position, aimSource.forward);
            return new Ray(transform.position + Vector3.up * 1.5f, transform.forward);
        }

        private float AimPitch()
        {
            if (aimSource == null) return 0f;
            float pitch = aimSource.eulerAngles.x;
            return pitch > 180f ? pitch - 360f : pitch;
        }

        private IIntimidatable Aimed()
        {
            return Physics.Raycast(AimRay(), out var hit, 25f, ~0, QueryTriggerInteraction.Ignore) && hit.collider.transform.root != transform.root
                ? hit.collider.GetComponentInParent<IIntimidatable>() : null;
        }

        // Apuntarle a alguien empieza la intimidación; dejar de apuntarle la termina (GDD 8.1, Task 13).
        private void SetIntimidated(IIntimidatable target)
        {
            if (ReferenceEquals(target, intimidated)) return;
            intimidated?.EndIntimidation(gameObject);
            intimidated = target;
            intimidated?.BeginIntimidation(gameObject);
        }
    }
}
