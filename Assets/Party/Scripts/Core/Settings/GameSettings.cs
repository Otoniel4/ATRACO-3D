using System;
using UnityEngine;

namespace Alarma.Core.Settings
{
    // Opciones del jugador guardadas en este equipo (PlayerPrefs). Los valores iniciales se ajustan en el asset.
    [CreateAssetMenu(menuName = "Alarma/Ajustes del juego", fileName = "GameSettings")]
    public sealed class GameSettings : ScriptableObject
    {
        public const float MinSensitivity = .2f, MaxSensitivity = 3f;
        private const string Prefix = "Alarma.Ajustes.";

        [SerializeField, Range(0f, 1f)] private float defaultVolume = .8f;
        [SerializeField, Range(MinSensitivity, MaxSensitivity)] private float defaultSensitivity = 1f;

        private bool loaded;

        public event Action Changed;
        public float Volume { get; private set; }
        public float MouseSensitivity { get; private set; }
        public bool Fullscreen { get; private set; }
        public int Quality { get; private set; }

        // El asset sobrevive entre sesiones de Play en el editor: se vuelve a leer al empezar cada una.
        private void OnEnable() => loaded = false;

        public void EnsureLoaded()
        {
            if (loaded) return;
            Volume = PlayerPrefs.GetFloat(Prefix + "Volumen", defaultVolume);
            MouseSensitivity = Mathf.Clamp(PlayerPrefs.GetFloat(Prefix + "Sensibilidad", defaultSensitivity), MinSensitivity, MaxSensitivity);
            Fullscreen = PlayerPrefs.GetInt(Prefix + "PantallaCompleta", Screen.fullScreen ? 1 : 0) == 1;
            Quality = Mathf.Clamp(PlayerPrefs.GetInt(Prefix + "Calidad", QualitySettings.GetQualityLevel()), 0, QualitySettings.names.Length - 1);
            loaded = true;
            Changed?.Invoke();
        }

        public void SetVolume(float value) { Volume = Mathf.Clamp01(value); Save(); }
        public void SetMouseSensitivity(float value) { MouseSensitivity = Mathf.Clamp(value, MinSensitivity, MaxSensitivity); Save(); }
        public void SetFullscreen(bool value) { Fullscreen = value; Save(); }
        public void SetQuality(int value) { Quality = (int)Mathf.Repeat(value, QualitySettings.names.Length); Save(); }

        private void Save()
        {
            PlayerPrefs.SetFloat(Prefix + "Volumen", Volume);
            PlayerPrefs.SetFloat(Prefix + "Sensibilidad", MouseSensitivity);
            PlayerPrefs.SetInt(Prefix + "PantallaCompleta", Fullscreen ? 1 : 0);
            PlayerPrefs.SetInt(Prefix + "Calidad", Quality);
            PlayerPrefs.Save();
            Changed?.Invoke();
        }
    }
}
