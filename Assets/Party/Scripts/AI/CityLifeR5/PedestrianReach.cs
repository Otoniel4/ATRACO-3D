using System;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    // Resuelve el alcance sin estirar los huesos; las puertas usan una palma anatómica independiente del agarre de compras.
    // En el mostrador el cuerpo se inclina como una persona: bisagra de cadera repartida entre cadera, abdomen y torso
    // (ningún hueso hace todo el giro), el cuello levanta la mirada y el brazo libre acompaña sin meterse en el mueble.
    [DefaultExecutionOrder(100)]
    public sealed class PedestrianReach : MonoBehaviour
    {
        [SerializeField] private Transform upper, lower, grip, spine;
        private Transform target;
        private float until, weight;
        private bool surface;
        private bool holding;
        // Cuánto queda el hombro derecho hacia el costado del cuerpo en reposo, en metros.
        private float shoulderSide;
        // Altura y adelanto del hombro sobre los pies, y largo del brazo del hombro a la muñeca.
        private float shoulderHeight, shoulderAhead, armLength;

        // Punto junto a la cadera derecha (el bolsillo) al que la palma llega con el brazo casi estirado y el cuerpo
        // derecho. Sale del largo real del brazo: un punto fijo a 95 cm del piso quedaba 10 cm más lejos de lo que el
        // brazo alcanza y la persona se doblaba hasta el tope para sacar o guardar el dinero.
        public Vector3 PocketPoint
        {
            get
            {
                Vector3 ahead = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
                Vector3 wrist = transform.position + Vector3.Cross(Vector3.up, ahead) * (shoulderSide + .03f)
                    + Vector3.up * (shoulderHeight - armLength * .88f) + ahead * (shoulderAhead + armLength * .3f);
                return surfaceHand != null ? surfaceHand.PalmAt(wrist, surfaceHand.HoldingRotation(ahead)) : wrist;
            }
        }
        private float commerceLean;
        // Tope de la inclinación total (los mostradores piden hasta 46° con la persona en su puesto; más que eso ya no
        // es una postura humana), cuánto la compensa el cuello y cuánto la acompaña el brazo libre. Medidos con
        // Art/BlenderScripts/CounterPosture46~/preview.py. MaxSide y MinAhead limitan el desvío lateral a unos 40°.
        private const float MaxLean = 48f, MaxSide = .64f, MinAhead = .77f, NeckShare = .45f, FreeArmFollow = .7f;
        // Rapidez con que la mano gira hacia el agarre pedido (por segundo; 12 ≈ llega en un cuarto de segundo).
        private const float HandTurnRate = 12f;
        // Adelanto mínimo del punto respecto del hombro, en metros, para que el cuerpo se incline hacia él.
        private const float LeanFrom = .2f;
        // Huesos que reparten la inclinación, de abajo hacia arriba, con la parte que gira cada uno (suman 1).
        private Transform[] leanChain = Array.Empty<Transform>();
        private float[] leanShare = Array.Empty<float>();
        private Transform neck;
        // Todo hueso del tronco que se toca en un cuadro, con su pose original para devolverla.
        private Transform[] bent = Array.Empty<Transform>();
        private Quaternion[] bentPose = Array.Empty<Quaternion>();
        private bool graspFromAbove;
        private Vector3 objectFingers, objectNormal;
        private float objectPoseUntil, objectCurl = 1f;
        private float[] objectFingerAngles;
        // Giro de la mano que se aplica: sigue al pedido de a poco, nunca de golpe.
        private Quaternion handRotation = Quaternion.identity;
        private bool handTracking;
        public void SetObjectPose(Vector3 fingers, Vector3 normal, float curl, float[] fingerAngles = null)
        {
            objectFingerAngles = fingerAngles;
            // Quien entrega elige el sentido de los dedos según hacia dónde mira el cuerpo. Con el objeto casi de costado
            // ese sentido cambiaba de un cuadro al siguiente y la muñeca daba media vuelta ida y vuelta (el brazo se
            // doblaba y parpadeaba). Mientras se sigue sujetando, se conserva el sentido ya elegido.
            bool sameGrip = Time.time < objectPoseUntil + .25f;
            if (sameGrip && Vector3.Dot(fingers, objectFingers) < 0f
                && Mathf.Abs(Vector3.Dot(fingers.normalized, transform.forward)) < .5f) fingers = -fingers;
            objectFingers = fingers; objectNormal = normal; objectCurl = curl;
            objectPoseUntil = Time.time + .08f;
        }
        private Transform freeArm;
        private Quaternion freeArmPose;
        [SerializeField] private Transform purchaseGrip;
        private CommerceFingerPose purchaseFingers;
        public Transform PurchaseGrip => purchaseGrip != null ? purchaseGrip : grip;
        // Llevar relajado: mientras camina con algo en la mano y no hay nada que alcanzar, el brazo lo mueve el clip
        // (balanceo natural) y acá solo se cierran los dedos sobre el objeto. Antes la mano iba fija a un punto frente
        // al pecho y el brazo quedaba duro durante todo el camino.
        private float relaxedUntil;
        public void CarryRelaxed() => relaxedUntil = Time.time + .15f;
        public bool RelaxedCarry => Time.time <= relaxedUntil && !(target != null && Time.time <= until) && weight <= 0f;
        // Giro de la mano tal como la deja la animación (para que el objeto viaje con ella).
        public Quaternion HandFrame => surfaceHand != null ? surfaceHand.Frame : transform.rotation;
        private SurfaceHandPose surfaceHand;
        private Quaternion wristPose;
        private float palmError = float.PositiveInfinity;
        // Abdomen y brazos recuperan la pose original antes de que el Animator escriba el fotograma siguiente.
        private Quaternion upperPose, lowerPose;
        private bool adjusted;
        public bool HasContact => weight > .85f && palmError <= (surface ? .008f : .035f);
        public Vector3 PalmPosition => (surface || holding) && surfaceHand != null ? surfaceHand.Position
            : grip != null ? grip.position : transform.position;

        // La distancia lateral sale del rig real, no de un hombro supuesto a 22 cm del centro. Se usa la del cuerpo en
        // reposo: con la del cuadro actual (ya inclinado y con el brazo movido) el puesto cambiaba al acercarse y la
        // persona nunca terminaba de llegar; seguía dando pasos contra el mueble.
        public Vector3 AlignSurfaceStand(Vector3 contact, Vector3 stand, Vector3 forward)
        {
            if (upper == null) return stand;
            Vector3 side = Vector3.Cross(Vector3.up, forward).normalized;
            float correction = Vector3.Dot(contact - stand, side) - shoulderSide;
            return stand + side * correction;
        }

        public void Configure(Transform hand)
        {
            // Si se vuelve a configurar con el cuerpo ya inclinado, primero se devuelve la pose: las medidas son del cuerpo derecho.
            RestorePose();
            grip = hand;
            upper = Bone(HumanBodyBones.RightUpperArm);
            lower = Bone(HumanBodyBones.RightLowerArm);
            spine = Bone(HumanBodyBones.Spine);
            shoulderSide = Vector3.Dot(upper.position - transform.position, transform.right);
            shoulderHeight = upper.position.y - transform.position.y;
            shoulderAhead = Vector3.Dot(upper.position - transform.position, transform.forward);
            BuildLeanChain();
            foreach (var bone in transform.GetComponentsInChildren<Transform>(true))
                if (bone.name == "UpperArm.L" || bone.name == "LeftUpperArm") { freeArm = bone; break; }
            var wrist = RigBones.Find(transform, HumanBodyBones.RightHand);
            surfaceHand = wrist != null ? new SurfaceHandPose(wrist, grip) : null;
            armLength = Vector3.Distance(upper.position, lower.position) + Vector3.Distance(lower.position, (wrist != null ? wrist : grip).position);
            if (surfaceHand != null)
            {
                if (purchaseGrip == null) purchaseGrip = new GameObject("Palma_Compra").transform;
                purchaseGrip.SetParent(wrist, false);
                purchaseGrip.position = surfaceHand.Position;
                purchaseFingers = new CommerceFingerPose(wrist);
            }
        }

        // Busca por nombre en los dos esqueletos del elenco (el propio de Blender y los modulares). La cadera entra solo
        // si las piernas no cuelgan de ella: si no, se inclinarían con el tronco.
        private void BuildLeanChain()
        {
            var bones = transform.GetComponentsInChildren<Transform>(true);
            Transform hips = Named(bones, "Hips"), leg = Named(bones, "UpperLeg.L", "LeftUpperLeg");
            Transform middle = Named(bones, "Torso", "Chest");
            bool hinge = hips != null && Under(spine, hips) && !(leg != null && Under(leg, hips));
            bool curve = middle != null && Under(middle, spine) && Under(upper, middle);
            if (hinge && curve) { leanChain = new[] { hips, spine, middle }; leanShare = new[] { .45f, .30f, .25f }; }
            else if (hinge) { leanChain = new[] { hips, spine }; leanShare = new[] { .6f, .4f }; }
            else if (curve) { leanChain = new[] { spine, middle }; leanShare = new[] { .55f, .45f }; }
            else { leanChain = new[] { spine }; leanShare = new[] { 1f }; }
            neck = Named(bones, "Neck");
            if (neck != null && !Under(neck, leanChain[leanChain.Length - 1])) neck = null;
            bent = new Transform[leanChain.Length + (neck != null ? 1 : 0)];
            leanChain.CopyTo(bent, 0);
            if (neck != null) bent[bent.Length - 1] = neck;
            bentPose = new Quaternion[bent.Length];
        }

        private static Transform Named(Transform[] bones, params string[] names)
        {
            foreach (string wanted in names)
                foreach (var bone in bones)
                    if (bone.name == wanted) return bone;
            return null;
        }

        // Verdadero si el hueso cuelga del otro (sin contar al propio).
        private static bool Under(Transform bone, Transform ancestor)
        {
            for (var parent = bone.parent; parent != null; parent = parent.parent)
                if (parent == ancestor) return true;
            return false;
        }

        private Transform Bone(HumanBodyBones bone) => RigBones.Find(transform, bone)
            ?? throw new InvalidOperationException("Falta el hueso " + bone + " en " + name);

        private void Awake() { if (grip != null) Configure(grip); }

        public void Reach(Transform point, float seconds = .1f) => SetTarget(point, seconds, false);
        public void ReachSurface(Transform point) => SetTarget(point, .18f, true);
        public void ReachObject(Transform point, bool fromAbove = false)
        {
            SetTarget(point, .15f, false);
            holding = true;
            graspFromAbove = fromAbove;
        }
        public void Release(Transform point)
        {
            if (target == point) until = 0;
        }

        public bool CanReach(Vector3 point, float tolerance = .04f)
        {
            if (upper == null || lower == null || grip == null) return false;
            float length = Vector3.Distance(upper.position, lower.position) + Vector3.Distance(lower.position, grip.position);
            return Vector3.Distance(upper.position, point) <= length + tolerance;
        }

        // Una palma vertical requiere otra posición de muñeca que el marcador de llevar objetos.
        public bool CanReachSurface(Transform point, float tolerance = .005f)
        {
            if (point == null || upper == null || lower == null) return false;
            if (surfaceHand == null) return CanReach(point.position, tolerance);
            Quaternion rotation = surfaceHand.Rotation(point.forward);
            Vector3 wristTarget = surfaceHand.WristTarget(point.position, rotation);
            float length = Vector3.Distance(upper.position, lower.position)
                + Vector3.Distance(lower.position, surfaceHand.Wrist.position) - .001f;
            return Vector3.Distance(upper.position, wristTarget) <= length + tolerance;
        }

        private void SetTarget(Transform point, float seconds, bool doorSurface)
        {
            if (target != point) palmError = float.PositiveInfinity;
            target = point;
            surface = doorSurface;
            holding = false;
            until = Time.time + seconds;
        }

        private void Update() => RestorePose();

        private void OnDisable()
        {
            RestorePose();
            target = null;
            weight = 0;
            palmError = float.PositiveInfinity;
        }

        private void RestorePose()
        {
            purchaseFingers?.Restore();
            if (!adjusted) return;
            for (int i = 0; i < bent.Length; i++) bent[i].localRotation = bentPose[i];
            upper.localRotation = upperPose;
            lower.localRotation = lowerPose;
            if (freeArm != null) freeArm.localRotation = freeArmPose;
            if (surfaceHand != null) surfaceHand.Wrist.localRotation = wristPose;
            adjusted = false;
        }

        private void LateUpdate()
        {
            if (grip == null || upper == null || lower == null || spine == null || Time.deltaTime <= 0) return;
            bool active = target != null && Time.time <= until;
            weight = Mathf.MoveTowards(weight, active ? 1f : 0f, Time.deltaTime / (active ? .14f : .18f));
            if (target == null || weight <= 0)
            {
                palmError = float.PositiveInfinity;
                handTracking = false;
                if (RelaxedCarry && purchaseFingers != null)
                {
                    bool posed = Time.time < objectPoseUntil;
                    purchaseFingers.Apply(1f, posed ? objectCurl : 1f, posed ? objectFingerAngles : null);
                }
                return;
            }
            if (holding && surfaceHand != null)
            {
                // El agarre pedido cambia de golpe al pasar de un objeto a otro o al soltarlo; la mano gira hacia él
                // en unas décimas de segundo. La palma sigue en su punto porque muñeca y giro se calculan juntos.
                Quaternion wanted = WantedObjectRotation();
                handRotation = handTracking ? Quaternion.Slerp(handRotation, wanted, Mathf.Clamp(Time.deltaTime * HandTurnRate, 0f, 1f)) : wanted;
                handTracking = true;
            }
            else handTracking = false;
            for (int i = 0; i < bent.Length; i++) bentPose[i] = bent[i].localRotation;
            upperPose = upper.localRotation;
            lowerPose = lower.localRotation;
            if (freeArm != null) freeArmPose = freeArm.localRotation;
            Quaternion freeWorld = freeArm != null ? freeArm.rotation : Quaternion.identity;
            if (surfaceHand != null) wristPose = surfaceHand.Wrist.localRotation;
            adjusted = true;

            Vector3 direction = target.position - upper.position;
            direction.y = 0;
            if (direction.sqrMagnitude > .001f)
            {
                if (holding && surfaceHand != null) LeanToReach(direction.normalized, freeWorld);
                // Puertas y gestos cortos: una inclinación leve del abdomen, como antes.
                else spine.rotation = Quaternion.AngleAxis((surface ? 10f : 12f) * weight, Vector3.Cross(Vector3.up, direction.normalized)) * spine.rotation;
            }
            if ((surface || holding) && surfaceHand != null)
            {
                Quaternion before = surfaceHand.Wrist.rotation;
                Quaternion rotation = surface ? surfaceHand.Rotation(target.forward) : ObjectRotation();
                SolveArm(surfaceHand.WristTarget(target.position, rotation), surfaceHand.Wrist);
                surfaceHand.Wrist.rotation = Quaternion.Slerp(before, rotation, weight);
                if (holding)
                {
                    bool posed = Time.time < objectPoseUntil;
                    purchaseFingers?.Apply(weight, posed ? objectCurl : 1f, posed ? objectFingerAngles : null);
                }
            }
            else SolveArm(target.position, grip);
            palmError = Vector3.Distance(PalmPosition, target.position);
        }

        // Inclina solo lo necesario para que el brazo llegue; nunca alarga los huesos ni mueve los pies a través del mueble.
        private void LeanToReach(Vector3 direction, Quaternion freeWorld)
        {
            // Se inclina hacia adelante; hacia un costado solo un poco, para no doblarse de lado.
            Vector3 ahead = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, ahead);
            Vector3 toward = (ahead * Mathf.Max(Vector3.Dot(direction, ahead), MinAhead)
                + right * Mathf.Clamp(Vector3.Dot(direction, right), -MaxSide, MaxSide)).normalized;
            Vector3 axis = Vector3.Cross(Vector3.up, toward).normalized;
            Vector3 wrist = surfaceHand.WristTarget(target.position, ObjectRotation());
            float length = Vector3.Distance(upper.position, lower.position)
                + Vector3.Distance(lower.position, surfaceHand.Wrist.position) - .006f;
            float desired = MaxLean, nearest = float.PositiveInfinity;
            // Inclinarse solo sirve para llegar a algo que está adelante. Un punto junto al cuerpo (el bolsillo, el
            // objeto que ya lleva) se alcanza con el brazo; buscarlo con el tronco lo doblaba hasta el tope.
            float limit = Vector3.Dot(wrist - upper.position, ahead) < LeanFrom ? 0f : MaxLean;
            for (float candidate = 0f; candidate <= limit; candidate += 2f)
            {
                float distance = Vector3.Distance(ShoulderAt(candidate, axis), wrist);
                if (distance < nearest) { nearest = distance; desired = candidate; }
                if (distance <= length) break;
            }
            commerceLean = Mathf.MoveTowards(commerceLean, desired, Time.deltaTime * 75f);
            float lean = commerceLean * weight;
            // De la cadera hacia arriba: cada giro arrastra a los huesos que siguen.
            for (int i = 0; i < leanChain.Length; i++)
                leanChain[i].rotation = Quaternion.AngleAxis(lean * leanShare[i], axis) * leanChain[i].rotation;
            if (neck != null) neck.rotation = Quaternion.AngleAxis(-lean * NeckShare, axis) * neck.rotation;
            if (freeArm != null) freeArm.rotation = Quaternion.Slerp(freeWorld, freeArm.rotation, FreeArmFollow);
        }

        // Dónde queda el hombro si la cadena reparte ese ángulo alrededor del eje.
        private Vector3 ShoulderAt(float angle, Vector3 axis)
        {
            int last = leanChain.Length - 1;
            Vector3 offset = upper.position - leanChain[last].position;
            for (int i = last; i >= 0; i--)
            {
                offset = Quaternion.AngleAxis(angle * leanShare[i], axis) * offset;
                if (i > 0) offset += leanChain[i].position - leanChain[i - 1].position;
            }
            return leanChain[0].position + offset;
        }

        private Quaternion ObjectRotation() => handRotation;

        private Quaternion WantedObjectRotation() => Time.time < objectPoseUntil
            ? surfaceHand.ObjectRotation(objectFingers, objectNormal)
            : graspFromAbove ? surfaceHand.GraspRotation(transform.forward) : surfaceHand.HoldingRotation(transform.forward);

        private void SolveArm(Vector3 point, Transform endpoint)
        {
            Vector3 shoulder = upper.position;
            Vector3 upperBone = lower.position - shoulder;
            float a = upperBone.magnitude;
            float b = Vector3.Distance(lower.position, endpoint.position);
            Vector3 reach = point - shoulder;
            if (a < .001f || b < .001f || reach.sqrMagnitude < .000001f) return;
            Vector3 direction = reach.normalized;
            float distance = Mathf.Clamp(reach.magnitude, Mathf.Abs(a - b) + .001f, a + b - .001f);
            float along = (a * a - b * b + distance * distance) / (2f * distance);
            // Al sostener un objeto el codo apunta abajo, algo afuera y atrás, como en una persona. Seguir la pose del
            // clip lo dejaba a veces levantado o hacia adentro (brazo quebrado). Las puertas conservan su pose.
            Vector3 natural = Vector3.down + transform.right * .45f - transform.forward * .25f;
            Vector3 bend = Vector3.ProjectOnPlane(holding ? natural : upperBone, direction);
            if (bend.sqrMagnitude < .0001f) bend = Vector3.ProjectOnPlane(Vector3.down + transform.right * .45f, direction);
            Vector3 elbow = shoulder + direction * along + bend.normalized * Mathf.Sqrt(Mathf.Max(0, a * a - along * along));

            Quaternion upperGoal = Quaternion.FromToRotation(upperBone, elbow - shoulder) * upper.rotation;
            upper.rotation = Quaternion.Slerp(upper.rotation, upperGoal, weight);
            Vector3 toPalm = endpoint.position - lower.position;
            Vector3 toPoint = point - lower.position;
            if (toPalm.sqrMagnitude < .000001f || toPoint.sqrMagnitude < .000001f) return;
            Quaternion lowerGoal = Quaternion.FromToRotation(toPalm, toPoint) * lower.rotation;
            lower.rotation = Quaternion.Slerp(lower.rotation, lowerGoal, weight);
        }
    }
}
