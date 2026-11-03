using UnityEngine;
using UnityEngine.InputSystem;

namespace Alarma.AI.CityLife
{
    public sealed class CityLifePreviewCamera : MonoBehaviour
    {
        [SerializeField] private float movementSpeed = 8f;
        private void Update()
        {
            Keyboard keyboard = Keyboard.current; Mouse mouse = Mouse.current;
            if (keyboard == null || mouse == null) return;
            Vector3 axis = new Vector3((keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0),
                (keyboard.eKey.isPressed ? 1 : 0) - (keyboard.qKey.isPressed ? 1 : 0),
                (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0));
            float speed = movementSpeed * (keyboard.leftShiftKey.isPressed ? 3f : 1f);
            transform.position += transform.TransformDirection(Vector3.ClampMagnitude(axis, 1f)) * (speed * Time.unscaledDeltaTime);
            if (!mouse.rightButton.isPressed) return;
            Vector2 delta = mouse.delta.ReadValue() * .10f;
            Vector3 angles = transform.eulerAngles; angles.x -= delta.y; angles.y += delta.x; angles.z = 0;
            transform.rotation = Quaternion.Euler(angles);
        }
    }
}
