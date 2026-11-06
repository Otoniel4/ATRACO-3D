using UnityEngine;

namespace Alarma.Player.Items
{
    // Sostiene el objeto elegido de la barra rápida: lo ubica frente al pecho según su forma de sostener (HoldPoseLibrary)
    // y lleva las manos a sus puntos de agarre con IK (Grip_R siempre; Grip_L si se toma con dos manos).
    // Se balancea al caminar, baja el arma al correr y, al cambiar de objeto, lo saca desde la cadera.
    // Corre después del Animator y antes del gesto de empujar puertas (orden 100), que puede tomar la mano derecha un momento.
    [DefaultExecutionOrder(90)]
    public sealed class HeldItemView : MonoBehaviour
    {
        private const float EquipSeconds = .28f, WalkSpeed = 1.3f, RunSpeed = 3f, StepRate = 2.1f;
        private static readonly Vector3 Holster = new Vector3(.22f, -.55f, .04f); // al costado de la cadera
        [SerializeField] private PlayerInventory owner;
        [SerializeField, Tooltip("Componente que implementa ICharacterRig.")] private MonoBehaviour rigSource;
        [SerializeField] private HoldPoseLibrary poses;
        private ICharacterRig rig;
        private Inventory inventory;
        private GameObject held;
        private Transform gripRight, gripLeft;
        private ItemDefinition shown;
        private ItemDefinition requested;
        private HandGripPose rightHand, leftHand;
        private Transform boundPalm;
        private Quaternion modelBasis;
        private float equip, run, speed, phase;
        private Vector3 lastPosition;
        private float aimWeight, aimPitch;
        private ActionPose action;
        private bool modelHidden;
        private Quaternion spinePose;
        private Transform posedSpine;

        // Lo que se tiene en la mano, para quien lo usa (ItemUser).
        public GameObject HeldModel => held;
        public ItemDefinition HeldItem => held != null ? shown : null;
        public bool Ready => held != null && shown != null && requested == shown && equip >= 1f && rig != null && !rig.HandsBusy;
        public Vector3 ItemForward { get; private set; } = Vector3.forward;

        // Apuntar (0–1) eleva el arma a la altura de los ojos e inclina según la cámara (grados, positivo = abajo).
        public void SetAim(float weight, float pitch) { aimWeight = Mathf.Clamp01(weight); aimPitch = Mathf.Clamp(pitch, -60f, 60f); }
        // Movimiento de la acción en curso (retroceso, palanca, lanzamiento), sumado a la pose.
        public void SetAction(ActionPose pose) => action = pose;
        public void HideModel(bool hidden) => modelHidden = hidden;

        public void Configure(PlayerInventory playerInventory, ICharacterRig character, HoldPoseLibrary holdPoses)
        {
            owner = playerInventory; rigSource = character as MonoBehaviour; poses = holdPoses;
        }

        // En Start: el inventario ya se creó en Awake y el cuerpo del personaje ya existe.
        private void Start()
        {
            rig = rigSource as ICharacterRig;
            if (owner == null || rig == null || poses == null)
            {
                Debug.LogWarning("El objeto en la mano no tiene inventario, cuerpo o poses: la escena es de una versión anterior. Usa Alarma > Crear y probar juego.", this);
                enabled = false;
                return;
            }
            inventory = owner.Inventory;
            inventory.Changed += Refresh;
            inventory.SelectionChanged += OnSelected;
            rig.RigChanged += BindHands;
            BindHands();
            lastPosition = transform.position;
            Refresh();
        }

        private void OnDestroy()
        {
            rightHand?.Dispose(); leftHand?.Dispose();
            if (rig != null) rig.RigChanged -= BindHands;
            if (inventory == null) return;
            inventory.Changed -= Refresh;
            inventory.SelectionChanged -= OnSelected;
        }

        private void OnSelected(int _) => Refresh();

        private void Refresh()
        {
            requested = inventory.ActiveStack.Item; // guardado = manos libres
        }

        private void ReplaceItem()
        {
            var item = requested;
            if (held != null) Destroy(held);
            held = null; gripRight = gripLeft = null; shown = item; equip = 0f;
            if (item == null || item.HandModel == null) return;
            held = Instantiate(item.HandModel, transform);
            // El FBX trae su conversión Blender→Unity en la raíz (−90° X). No sustituirla por la pose.
            modelBasis = held.transform.localRotation;
            held.name = "En la mano: " + item.DisplayName;
            gripRight = Point(held, "Grip_R");
            gripLeft = Point(held, "Grip_L");
            SetLayer(held.transform, gameObject.layer);
        }

        private void BindHands()
        {
            rightHand?.Dispose(); leftHand?.Dispose();
            boundPalm = rig.RightPalm;
            rightHand = boundPalm != null ? new HandGripPose(boundPalm, true) : null;
            leftHand = rig.LeftPalm != null ? new HandGripPose(rig.LeftPalm, false) : null;
            equip = 0f;
        }

        private void Update() => RestoreHands();
        private void RestoreHands()
        {
            rightHand?.Restore(); leftHand?.Restore();
            if (posedSpine != null) { posedSpine.localRotation = spinePose; posedSpine = null; }
        }
        private void OnDisable() { RestoreHands(); if (held != null) held.SetActive(false); }

        private void LateUpdate()
        {
            float dt = Time.deltaTime;
            if (dt <= 0f) return;
            Vector3 moved = transform.position - lastPosition;
            moved.y = 0f;
            lastPosition = transform.position;
            speed = Mathf.Lerp(speed, moved.magnitude / dt, 1f - Mathf.Exp(-10f * dt));
            if (rig == null || rig.Chest == null || rig.RightPalm == null) return;
            if (boundPalm != rig.RightPalm) BindHands();
            bool stow = rig.HandsBusy || requested != shown;
            equip = Mathf.MoveTowards(equip, stow ? 0f : 1f, dt / EquipSeconds);
            if (equip <= 0f && requested != shown) ReplaceItem();
            if (held == null) return;
            held.SetActive((!rig.HandsBusy || equip > 0f) && !modelHidden);
            if (!held.activeSelf) return;
            run = Mathf.MoveTowards(run, speed > RunSpeed ? 1f : 0f, dt * 4f);
            phase += speed * dt * StepRate;
            var pose = poses.Find(shown.HoldStyle);
            float drawn = Mathf.SmoothStep(0f, 1f, equip), walking = Mathf.Clamp01(speed / WalkSpeed);
            // Balanceo de los pasos: un poco de lado y arriba-abajo, más fuerte al correr.
            Vector3 sway = new Vector3(Mathf.Sin(phase) * .6f, -Mathf.Abs(Mathf.Cos(phase)), 0f) * pose.sway * walking * (1f + run) * (1f - .7f * aimWeight);
            Vector3 offset = Vector3.Lerp(pose.offset, pose.runOffset, run) + shown.HoldOffset + sway;
            Quaternion turn = Quaternion.Slerp(Quaternion.Euler(pose.euler), Quaternion.Euler(pose.runEuler), run) * Quaternion.Euler(shown.HoldEuler);
            // Apuntando: el arma sube a la línea de los ojos y gira con la inclinación de la cámara, alrededor del pecho.
            Quaternion tilt = Quaternion.Euler(aimPitch * aimWeight, 0f, 0f);
            offset = Vector3.Lerp(offset, Quaternion.Euler(aimPitch, 0f, 0f) * pose.aimOffset + shown.HoldOffset, aimWeight);
            turn = Quaternion.Slerp(turn, Quaternion.Euler(aimPitch, 0f, 0f) * Quaternion.Euler(pose.aimEuler) * Quaternion.Euler(shown.HoldEuler), aimWeight);
            // La acción en curso se suma: desplazamiento en ejes del cuerpo (inclinado si se apunta) y giro en ejes del objeto.
            offset += tilt * action.Offset;
            turn *= Quaternion.Euler(action.Euler);
            Quaternion body = Quaternion.Euler(0f, transform.eulerAngles.y, 0f);
            // Torso: lo inclina la acción (palanca, lanzamiento, colocar la termita) y, al apuntar, sigue a la cámara.
            Vector3 aimLean = new Vector3(aimPitch * .35f * aimWeight, 0f, 0f) * drawn;
            Vector3 lean = action.Lean * drawn + aimLean;
            // Con clip, el Animator ya inclinó el torso, agachó el cuerpo y movió la cabeza: aquí solo se suma la mira.
            Vector3 spineLean = action.BodyFromClip ? aimLean : lean;
            if (rig.Spine != null && spineLean.sqrMagnitude > .0001f)
            {
                spinePose = rig.Spine.localRotation; posedSpine = rig.Spine;
                rig.Spine.rotation = Quaternion.AngleAxis(spineLean.y, Vector3.up) * Quaternion.AngleAxis(spineLean.x, body * Vector3.right)
                                     * Quaternion.AngleAxis(-spineLean.z, body * Vector3.forward) * rig.Spine.rotation;
            }
            // Las manos acompañan el giro del torso y la mitad de su inclinación.
            body = Quaternion.AngleAxis(lean.y, Vector3.up) * body;
            Quaternion frame = body * Quaternion.Euler(lean.x * .5f, 0f, 0f);
            Vector3 target = rig.Chest.position + frame * Vector3.Lerp(Holster, offset, drawn);

            bool firearmPose = shown.HoldStyle == HoldStyle.Pistol || shown.HoldStyle == HoldStyle.Long;
            Vector3 fingersR = firearmPose ? Vector3.forward : pose.rightFingers.normalized;
            Vector3 fingersL = firearmPose ? Vector3.forward : pose.leftFingers.normalized;
            Vector3 normalR = GripNormal(fingersR, -Vector3.right), normalL = GripNormal(fingersL, Vector3.right);
            var item = held.transform;
            Quaternion orientation = body * Quaternion.Slerp(Quaternion.Euler(80f, 0f, 0f), turn, drawn);
            ItemForward = orientation * Vector3.forward;
            item.rotation = orientation * modelBasis;
            item.position += target - GripRight(item);
            Vector3 right = body * Vector3.right;
            rightHand.Capture(rig.RightUpperArm, rig.RightLowerArm);
            TwoBoneIk.SolveHand(rig.RightUpperArm, rig.RightLowerArm, rightHand.Palm, target,
                rightHand.WristRotation(orientation, fingersR, normalR), right * .45f + Vector3.down, drawn);
            rightHand.Curl(drawn, firearmPose);
            // El objeto sigue a la palma real: si el brazo no llega al punto, no queda flotando.
            item.rotation = rightHand.ItemRotation(fingersR, normalR) * modelBasis;
            item.position += rightHand.Palm.position - GripRight(item);
            // Mano izquierda: siempre en los objetos de dos manos; en los de una mano, solo cuando la acción la pide.
            float leftWeight = Mathf.Max(TwoHanded(shown.HoldStyle) ? 1f : 0f, action.LeftHand) * drawn;
            if (gripLeft != null && leftHand != null && leftWeight > .01f)
            {
                leftHand.Capture(rig.LeftUpperArm, rig.LeftLowerArm);
                TwoBoneIk.SolveHand(rig.LeftUpperArm, rig.LeftLowerArm, leftHand.Palm, gripLeft.position,
                    leftHand.WristRotation(item.rotation * Quaternion.Inverse(modelBasis), fingersL, normalL),
                    -right * .45f + Vector3.down, leftWeight);
                leftHand.Curl(leftWeight, false);
            }
        }

        private Vector3 GripRight(Transform item) => gripRight != null ? gripRight.position : item.position;

        private static bool TwoHanded(HoldStyle style)
            => style == HoldStyle.Pistol || style == HoldStyle.Long || style == HoldStyle.TwoHandTablet || style == HoldStyle.TwoHandCanister;

        private static Vector3 GripNormal(Vector3 fingers, Vector3 inward)
        {
            return Vector3.ProjectOnPlane(Mathf.Abs(Vector3.Dot(fingers, inward)) > .95f ? Vector3.down : inward, fingers).normalized;
        }

        private static Transform Point(GameObject model, string name)
        {
            foreach (var t in model.GetComponentsInChildren<Transform>(true))
                if (t.name == name || t.name.StartsWith(name + ".", System.StringComparison.Ordinal)) return t;
            return null;
        }

        private static void SetLayer(Transform item, int layer)
        {
            item.gameObject.layer = layer;
            foreach (Transform child in item) SetLayer(child, layer);
        }
    }
}
