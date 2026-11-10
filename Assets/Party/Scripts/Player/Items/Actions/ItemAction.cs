using System;
using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.Core.Events;

namespace Alarma.Player.Items
{
    // Movimiento del objeto durante su uso, sumado a la pose de sostener (x derecha, y arriba, z adelante; grados).
    // Lean: inclinación del torso (x adelante, y giro a la derecha, z de costado, en grados).
    // LeftHand: 0–1, cuánto va la mano izquierda al segundo agarre (Grip_L) de un objeto que se lleva con una mano.
    // BodyFromClip: el cuerpo lo mueve un clip del Animator (capa Acciones); Lean solo sirve para ubicar las manos.
    public struct ActionPose
    {
        public Vector3 Offset, Euler, Lean;
        public float LeftHand;
        public bool BodyFromClip;
        public static readonly ActionPose None = default;
    }

    // Curvas de la animación de uso en el tiempo normalizado 0–1. Se editan en el Inspector.
    [Serializable]
    public sealed class MotionCurves
    {
        public AnimationCurve side = AnimationCurve.Constant(0, 1, 0), up = AnimationCurve.Constant(0, 1, 0), forward = AnimationCurve.Constant(0, 1, 0);
        public AnimationCurve pitch = AnimationCurve.Constant(0, 1, 0), yaw = AnimationCurve.Constant(0, 1, 0), roll = AnimationCurve.Constant(0, 1, 0);
        public AnimationCurve leanForward = AnimationCurve.Constant(0, 1, 0), leanTwist = AnimationCurve.Constant(0, 1, 0), leanSide = AnimationCurve.Constant(0, 1, 0);
        public AnimationCurve leftHand = AnimationCurve.Constant(0, 1, 0);

        public ActionPose Evaluate(float t) => new ActionPose
        {
            Offset = new Vector3(side.Evaluate(t), up.Evaluate(t), forward.Evaluate(t)),
            Euler = new Vector3(pitch.Evaluate(t), yaw.Evaluate(t), roll.Evaluate(t)),
            Lean = new Vector3(leanForward.Evaluate(t), leanTwist.Evaluate(t), leanSide.Evaluate(t)),
            LeftHand = Mathf.Clamp01(leftHand.Evaluate(t)),
        };
    }

    // Lo que necesita una acción para obrar: quién la usa, el modelo en la mano, hacia dónde apunta y cómo avisar.
    public sealed class ItemActionContext
    {
        public GameObject User;
        public ItemDefinition Item;
        public Transform Model;
        public Ray Aim;
        public Vector3 Forward;        // hacia dónde apunta el objeto en la mano (cañón, broca)
        public float Aiming;           // 0 a la cadera, 1 apuntando con clic derecho
        public LayerMask HitMask;
        public Func<bool> Consume;     // gasta una unidad del objeto en la mano
        public Action<string> Feedback;
        public Action<bool> HideModel; // la granada sale de la mano al lanzarla
        public Action<Pose> PlaceUser; // el objetivo pide dónde pararse (bridas: detrás de la persona)

        public Transform Part(string name)
        {
            foreach (var t in Model.GetComponentsInChildren<Transform>(true))
                if (Named(t, name)) return t;
            return null;
        }

        // Todas las piezas con ese nombre (Code, Code.001… de la tablet).
        public Renderer[] Renderers(string name)
        {
            var found = new System.Collections.Generic.List<Renderer>();
            foreach (var r in Model.GetComponentsInChildren<Renderer>(true))
                if (Named(r.transform, name)) found.Add(r);
            return found.ToArray();
        }

        private static bool Named(Transform t, string name) => t.name == name || t.name.StartsWith(name + ".", StringComparison.Ordinal);

        // Posición de reposo de una pieza móvil (corredera de la escopeta, broca), para moverla y devolverla.
        private readonly System.Collections.Generic.Dictionary<Transform, (Vector3 position, Quaternion rotation)> rest =
            new System.Collections.Generic.Dictionary<Transform, (Vector3, Quaternion)>();
        public (Vector3 position, Quaternion rotation) Rest(Transform part)
        {
            if (!rest.TryGetValue(part, out var pose)) rest[part] = pose = (part.localPosition, part.localRotation);
            return pose;
        }

        public Vector3 MuzzleOr(Vector3 fallback) { var muzzle = Part("MuzzlePoint"); return muzzle != null ? muzzle.position : fallback; }

        // Primer objetivo que acepta este objeto a lo largo de la mira, dentro de «range» metros del jugador.
        public IItemTarget FindTarget(float range, out RaycastHit hit)
        {
            hit = default;
            var hits = Physics.RaycastAll(Aim, range + 6f, HitMask, QueryTriggerInteraction.Collide);
            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            foreach (var candidate in hits)
            {
                if (Vector3.Distance(candidate.point, User.transform.position) > range + .6f) break;
                var target = candidate.collider.GetComponentInParent<IItemTarget>();
                if (target != null && target.Accepts(Item.Id)) { hit = candidate; return target; }
            }
            return null;
        }
    }

    // Uso de un objeto con clic izquierdo (patrón Strategy): cada tipo de arma o herramienta es una subclase con su efecto,
    // y cada objeto es un asset con su animación, duración y datos. Agregar un objeto nuevo no cambia ItemUser.
    public abstract class ItemAction : ScriptableObject
    {
        [SerializeField, Min(.05f), Tooltip("Duración de una animación de uso, en segundos.")] private float duration = .6f;
        [SerializeField, Range(0, 1), Tooltip("Momento de la animación en que ocurre el efecto (0 = al empezar).")] private float triggerAt;
        [SerializeField, Tooltip("Si se mantiene el clic, se repite (rifle automático, taladro).")] private bool repeatWhileHeld;
        [SerializeField] private MotionCurves motion = new MotionCurves();
        [SerializeField, Tooltip("Vibración durante el uso, en metros (taladro).")] private float shake;
        [SerializeField] private float shakeRate = 28f;
        [SerializeField, Tooltip("Pieza del modelo que gira durante el uso (por ejemplo, Bit del taladro).")] private string spinPart = "";
        [SerializeField] private float spinDegreesPerSecond;
        [SerializeField, Tooltip("Piezas que parpadean durante el uso (por ejemplo, Code de la tablet).")] private string blinkPart = "";
        [SerializeField, Tooltip("Número del clip de cuerpo en el parámetro «Accion» del Animator (0 = sin clip).")] private int animationId;
        [SerializeField, Tooltip("El clip usa todo el cuerpo (rodillas y cadera): el jugador se queda quieto mientras dura.")] private bool fullBody;
        [SerializeField, Tooltip("Canal donde avisa su ruido (disparos, estallidos): lo oyen los civiles.")] private NoiseChannel noise;
        [SerializeField, Min(0), Tooltip("Hasta dónde se oye, en metros (0 = silencioso).")] private float noiseRadius;
        [SerializeField, HideInInspector] private int dataVersion;

        public float Duration => duration;
        public float TriggerAt => triggerAt;
        public bool RepeatWhileHeld => repeatWhileHeld;
        public string SpinPart => spinPart;
        public float SpinSpeed => spinDegreesPerSecond;
        // Versión de Data/Items/item_actions.json con que se escribió el asset.
        public int DataVersion => dataVersion;
        public int AnimationId => animationId;
        public bool FullBody => fullBody;
        // Solo las armas se apuntan con clic derecho.
        public virtual bool CanAim => false;

        public ActionPose Evaluate(float t)
        {
            var pose = motion.Evaluate(t);
            pose.BodyFromClip = animationId > 0;
            if (shake > 0f)
            {
                float s = Time.time * shakeRate;
                pose.Offset += new Vector3(Mathf.PerlinNoise(s, 0f) - .5f, Mathf.PerlinNoise(0f, s) - .5f, 0f) * (shake * 2f);
            }
            return pose;
        }

        // Antes de empezar: false cancela el uso (por ejemplo, bridas sin nadie a quien amarrar). Por defecto siempre se puede.
        public virtual bool CanBegin(ItemActionContext context) => true;

        public abstract void Trigger(ItemActionContext context);

        // Movimiento de piezas del modelo cuadro a cuadro (t de 0 a 1): gira la pieza SpinPart y hace parpadear BlinkPart.
        public virtual void Animate(ItemActionContext context, float t)
        {
            if (!string.IsNullOrEmpty(blinkPart))
            {
                // Cada línea se enciende y apaga con su propio ritmo, como texto que corre en la pantalla.
                var lines = context.Renderers(blinkPart);
                for (int i = 0; i < lines.Length; i++) lines[i].enabled = Mathf.Repeat(Time.time * 5f + i * .37f, 1f) > .3f;
            }
            if (string.IsNullOrEmpty(spinPart) || spinDegreesPerSecond == 0f) return;
            var part = context.Part(spinPart);
            if (part == null) return;
            var rest = context.Rest(part);
            // Gira alrededor del eje del objeto (la broca sobre sí misma), sin depender de los ejes del FBX.
            var parent = part.parent;
            Quaternion restWorld = parent.rotation * rest.rotation;
            part.localRotation = Quaternion.Inverse(parent.rotation) * (Quaternion.AngleAxis(Time.time * spinDegreesPerSecond, context.Forward) * restWorld);
        }

        // Al terminar o interrumpirse el uso, las piezas móviles vuelven a su lugar y las que parpadean quedan encendidas.
        public virtual void Release(ItemActionContext context)
        {
            if (!string.IsNullOrEmpty(blinkPart))
                foreach (var line in context.Renderers(blinkPart)) line.enabled = true;
            if (string.IsNullOrEmpty(spinPart)) return;
            var part = context.Part(spinPart);
            if (part != null) { var rest = context.Rest(part); part.localPosition = rest.position; part.localRotation = rest.rotation; }
        }

        // Lo usa el preparador del editor al crear o actualizar el asset desde item_actions.json.
        public void ConfigureMotion(float seconds, float trigger, bool repeat, MotionCurves curves, float vibration = 0f, string spin = "", float spinSpeed = 0f,
                                    string blink = "", int version = 0)
        {
            duration = seconds; triggerAt = trigger; repeatWhileHeld = repeat; motion = curves; shake = vibration; spinPart = spin; spinDegreesPerSecond = spinSpeed;
            blinkPart = blink ?? ""; dataVersion = version;
        }

        public void ConfigureBody(int clip, bool wholeBody) { animationId = Mathf.Max(0, clip); fullBody = wholeBody && clip > 0; }

        public void ConfigureNoise(NoiseChannel channel, float radius) { noise = channel; noiseRadius = Mathf.Max(0f, radius); }

        // Avisa el ruido de la acción (si tiene) a quien escuche el canal.
        protected void MakeNoise(Vector3 position, NoiseKind kind, GameObject source)
        {
            if (noise != null) noise.Raise(position, noiseRadius, kind, source);
        }
    }
}
