using UnityEngine;

namespace Alarma.AI.Security
{
    // Guardia de puerta: no se mueve de su puesto, pero mira despacio a un lado y al otro, cada uno a su ritmo.
    public sealed class SentryLook : MonoBehaviour
    {
        [SerializeField, Range(0f, 90f)] private float sweep = 35f;
        [SerializeField, Min(1f)] private float period = 9f;
        private Quaternion rest;
        private float phase;

        private void Awake()
        {
            rest = transform.rotation;
            phase = Random.value * period;
        }

        private void Update()
        {
            float t = (Time.time + phase) / period * Mathf.PI * 2f;
            transform.rotation = rest * Quaternion.Euler(0f, Mathf.Sin(t) * sweep, 0f);
        }
    }
}
