using UnityEngine;
using Alarma.Player.Items;

namespace Alarma.Animation
{
    // Único componente que cambia el Animator para usar objetos. Cuando ItemUser empieza una acción con clip de cuerpo,
    // pide su estado con los parámetros «Usando» y «Accion» y sube el peso de su capa: «Acciones torso» (se puede
    // caminar) o «Acciones cuerpo» (rodillas y cadera); al terminar, lo baja. Como son parámetros del Animator,
    // NetworkAnimator podrá mostrarlos a los demás jugadores cuando llegue la red (Task 02).
    [DefaultExecutionOrder(81)] // justo después de ItemUser (80), en el mismo cuadro
    public sealed class ItemActionAnimator : MonoBehaviour
    {
        public const string UsingParameter = "Usando", ActionParameter = "Accion", TorsoLayer = "Acciones torso", BodyLayer = "Acciones cuerpo";
        private const float BlendSeconds = .15f;
        private static readonly int UsingId = Animator.StringToHash(UsingParameter), ActionId = Animator.StringToHash(ActionParameter);
        [SerializeField] private ItemUser user;
        [SerializeField, Tooltip("Componente que implementa ICharacterAnimator.")] private MonoBehaviour bodySource;
        private ICharacterAnimator body;
        private Animator animator;
        private int torsoLayer = -1, bodyLayer = -1;
        private float torsoWeight, bodyWeight;
        private ItemAction current;

        public void Configure(ItemUser itemUser, ICharacterAnimator character) { user = itemUser; bodySource = character as MonoBehaviour; }

        private void Start()
        {
            body = bodySource as ICharacterAnimator;
            if (user == null || body == null)
            {
                Debug.LogWarning("Los clips de uso de objetos no tienen ItemUser o cuerpo: usa Alarma > Crear y probar juego.", this);
                enabled = false;
                return;
            }
            user.ActionChanged += OnActionChanged;
            body.RigChanged += Bind;
            Bind();
        }

        private void OnDestroy()
        {
            if (user != null) user.ActionChanged -= OnActionChanged;
            if (body != null) body.RigChanged -= Bind;
        }

        private void OnActionChanged(ItemAction action) => current = action;

        // El cuerpo cambió (otro rol): se buscan sus capas de acciones.
        private void Bind()
        {
            animator = body.Animator;
            torsoWeight = bodyWeight = 0f;
            torsoLayer = animator != null ? animator.GetLayerIndex(TorsoLayer) : -1;
            bodyLayer = animator != null ? animator.GetLayerIndex(BodyLayer) : -1;
            if (animator != null && (torsoLayer < 0 || bodyLayer < 0))
                Debug.LogWarning("El Animator del personaje no tiene las capas de acciones: usa Alarma > Crear y probar juego.", this);
        }

        private void Update()
        {
            if (animator == null || torsoLayer < 0 || bodyLayer < 0) return;
            bool playing = current != null && current.AnimationId > 0;
            animator.SetBool(UsingId, playing);
            if (playing) animator.SetInteger(ActionId, current.AnimationId);
            // El peso sube y baja al mismo ritmo que la transición del estado: entra y sale suave.
            float step = Time.deltaTime / BlendSeconds;
            torsoWeight = Mathf.MoveTowards(torsoWeight, playing && !current.FullBody ? 1f : 0f, step);
            bodyWeight = Mathf.MoveTowards(bodyWeight, playing && current.FullBody ? 1f : 0f, step);
            animator.SetLayerWeight(torsoLayer, torsoWeight);
            animator.SetLayerWeight(bodyLayer, bodyWeight);
        }
    }
}
