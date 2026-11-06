using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Alarma.Player.Items
{
    // Efectos visuales de las armas y herramientas, creados por código con colores planos: fogonazo, trazador, impacto,
    // humo, destello, pulso EMP y chispas de termita. Cada uno se borra solo.
    public static class ItemEffects
    {
        private static readonly Dictionary<Color, Material> Solid = new Dictionary<Color, Material>();
        private static Material particles;

        public static void MuzzleFlash(Vector3 position, Vector3 forward, Color color)
        {
            var flash = Shape(PrimitiveType.Sphere, "Fogonazo", position + forward * .03f, Vector3.one * .07f, color);
            var light = flash.AddComponent<Light>();
            light.type = LightType.Point; light.range = 4f; light.intensity = 4f; light.color = color;
            flash.AddComponent<TimedEffect>().Play(.06f, 1f, .2f);
        }

        public static void Tracer(Vector3 from, Vector3 to, Color color, float width = .012f, float seconds = .06f)
        {
            var go = new GameObject("Trazador");
            var line = go.AddComponent<LineRenderer>();
            line.positionCount = 2; line.SetPosition(0, from); line.SetPosition(1, to);
            line.startWidth = width; line.endWidth = width * .5f;
            line.sharedMaterial = Material(color); line.shadowCastingMode = ShadowCastingMode.Off;
            go.AddComponent<TimedEffect>().Play(seconds, 1f, 1f);
        }

        // Marca del disparo pegada a la superficie que recibió el tiro (si es una puerta o un auto, se mueve con ella)
        // y una nube de polvo. Sobre personas no queda marca: solo el polvo, que se desvanece enseguida.
        public static void Impact(Vector3 point, Vector3 normal, Transform surface, bool mark)
        {
            if (mark)
            {
                var hole = Shape(PrimitiveType.Cylinder, "Impacto", point + normal * .004f, new Vector3(.035f, .002f, .035f), new Color(.08f, .08f, .09f));
                hole.transform.up = normal;
                if (surface != null) hole.transform.SetParent(surface, true);
                hole.AddComponent<TimedEffect>().Play(8f, 1f, 1f);
            }
            var puff = Shape(PrimitiveType.Sphere, "Polvo", point + normal * .05f, Vector3.one * .06f, new Color(.72f, .7f, .66f));
            puff.AddComponent<TimedEffect>().Play(.25f, 1f, 2.6f);
        }

        public static void Smoke(Vector3 position, float seconds)
        {
            var system = Particles("Humo", position, seconds + 6f, new Color(.75f, .76f, .78f, .75f));
            var main = system.main;
            main.startLifetime = 6f; main.startSpeed = .45f; main.startSize = new ParticleSystem.MinMaxCurve(1.6f, 2.8f); main.duration = seconds;
            var emission = system.emission; emission.rateOverTime = 22f;
            var shape = system.shape; shape.shapeType = ParticleSystemShapeType.Sphere; shape.radius = .6f;
            var size = system.sizeOverLifetime; size.enabled = true; size.size = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0, .6f, 1, 1.6f));
            system.Play();
        }

        public static void Flash(Vector3 position)
        {
            var ball = Shape(PrimitiveType.Sphere, "Destello", position, Vector3.one * .4f, Color.white);
            var light = ball.AddComponent<Light>();
            light.type = LightType.Point; light.range = 14f; light.intensity = 30f;
            ball.AddComponent<TimedEffect>().Play(.3f, 1f, 6f);
        }

        public static void EmpPulse(Vector3 position)
        {
            var ring = Shape(PrimitiveType.Sphere, "Pulso EMP", position, new Vector3(.3f, .05f, .3f), new Color(.3f, .75f, 1f));
            var light = ring.AddComponent<Light>();
            light.type = LightType.Point; light.range = 10f; light.intensity = 8f; light.color = new Color(.3f, .75f, 1f);
            ring.AddComponent<TimedEffect>().Play(.55f, 1f, 30f);
        }

        public static void Burn(Vector3 position, float seconds)
        {
            var system = Particles("Termita", position, seconds + 1f, new Color(1f, .6f, .15f, 1f));
            var main = system.main;
            main.startLifetime = .45f; main.startSpeed = new ParticleSystem.MinMaxCurve(1.5f, 3.5f); main.startSize = .05f; main.gravityModifier = 1f; main.duration = seconds;
            var emission = system.emission; emission.rateOverTime = 70f;
            var shape = system.shape; shape.shapeType = ParticleSystemShapeType.Cone; shape.angle = 35f; shape.radius = .05f;
            system.transform.rotation = Quaternion.LookRotation(Vector3.up);
            var light = system.gameObject.AddComponent<Light>();
            light.type = LightType.Point; light.range = 5f; light.intensity = 5f; light.color = new Color(1f, .55f, .2f);
            system.gameObject.AddComponent<FlickerLight>();
            system.Play();
        }

        private static GameObject Shape(PrimitiveType type, string name, Vector3 position, Vector3 scale, Color color)
        {
            var go = GameObject.CreatePrimitive(type);
            UnityEngine.Object.Destroy(go.GetComponent<Collider>());
            go.name = name;
            go.transform.SetPositionAndRotation(position, Quaternion.identity);
            go.transform.localScale = scale;
            var renderer = go.GetComponent<Renderer>();
            renderer.sharedMaterial = Material(color);
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            return go;
        }

        private static ParticleSystem Particles(string name, Vector3 position, float lifetime, Color color)
        {
            var go = new GameObject(name);
            go.transform.position = position;
            var system = go.AddComponent<ParticleSystem>();
            system.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            var main = system.main; main.startColor = color; main.loop = false; main.playOnAwake = false;
            var renderer = go.GetComponent<ParticleSystemRenderer>();
            renderer.sharedMaterial = ParticleMaterial();
            go.AddComponent<TimedEffect>().Play(lifetime, 1f, 1f);
            return system;
        }

        // Color plano sin luz: brilla igual de día y de noche.
        private static Material Material(Color color)
        {
            if (Solid.TryGetValue(color, out var material) && material != null) return material;
            material = new Material(Shader.Find("Universal Render Pipeline/Unlit") ?? throw new InvalidOperationException("Falta el shader URP/Unlit."));
            material.SetColor("_BaseColor", color);
            return Solid[color] = material;
        }

        // Partículas transparentes de URP (humo y chispas).
        private static Material ParticleMaterial()
        {
            if (particles != null) return particles;
            particles = new Material(Shader.Find("Universal Render Pipeline/Particles/Unlit") ?? throw new InvalidOperationException("Falta el shader URP/Particles/Unlit."));
            particles.SetFloat("_Surface", 1f);
            particles.SetOverrideTag("RenderType", "Transparent");
            particles.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
            particles.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
            particles.SetInt("_ZWrite", 0);
            particles.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            particles.renderQueue = (int)RenderQueue.Transparent;
            return particles;
        }
    }

    // Vida corta de un efecto: cambia de tamaño, apaga su luz y se borra.
    public sealed class TimedEffect : MonoBehaviour
    {
        private float life, age, from, to;
        private Vector3 baseScale;
        private Light lamp;
        private float lampIntensity;

        public void Play(float seconds, float startScale, float endScale)
        {
            life = Mathf.Max(.01f, seconds); from = startScale; to = endScale;
            baseScale = transform.localScale;
            lamp = GetComponent<Light>();
            if (lamp != null) lampIntensity = lamp.intensity;
        }

        private void Update()
        {
            age += Time.deltaTime;
            float t = Mathf.Clamp01(age / life);
            if (!Mathf.Approximately(from, to)) transform.localScale = baseScale * Mathf.Lerp(from, to, t);
            if (lamp != null) lamp.intensity = lampIntensity * (1f - t);
            if (age >= life) Destroy(gameObject);
        }
    }

    // Llama que titila (termita encendida).
    public sealed class FlickerLight : MonoBehaviour
    {
        private Light lamp;
        private float baseIntensity;
        private void Start() { lamp = GetComponent<Light>(); baseIntensity = lamp != null ? lamp.intensity : 0f; }
        private void Update() { if (lamp != null) lamp.intensity = baseIntensity * (.7f + Mathf.PerlinNoise(Time.time * 12f, 0f) * .6f); }
    }

    // Carga con mecha (granada lanzada, termita colocada): espera y luego obra su efecto una sola vez.
    public sealed class FusedCharge : MonoBehaviour
    {
        private float fuse;
        private Action<Vector3> explode;
        private Renderer blink;

        public void Arm(float seconds, Action<Vector3> effect, Renderer led = null) { fuse = seconds; explode = effect; blink = led; }

        private void Update()
        {
            fuse -= Time.deltaTime;
            if (blink != null) blink.enabled = Mathf.Repeat(Time.time * (fuse < 1f ? 8f : 2f), 1f) > .5f;
            if (fuse > 0f || explode == null) return;
            var effect = explode;
            explode = null;
            effect(transform.position);
        }
    }
}
