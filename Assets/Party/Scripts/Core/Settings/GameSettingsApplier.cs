using UnityEngine;

namespace Alarma.Core.Settings
{
    // Aplica al motor los ajustes que no pertenecen a un sistema concreto: volumen general, pantalla completa y calidad.
    public sealed class GameSettingsApplier : MonoBehaviour
    {
        [SerializeField] private GameSettings settings;
        private int appliedQuality = -1;

        public void Configure(GameSettings gameSettings) => settings = gameSettings;

        private void OnEnable()
        {
            if (settings == null) return;
            settings.Changed += Apply;
            settings.EnsureLoaded();
            Apply();
        }

        private void OnDisable()
        {
            if (settings != null) settings.Changed -= Apply;
        }

        private void Apply()
        {
            AudioListener.volume = settings.Volume;
            if (Screen.fullScreen != settings.Fullscreen) Screen.fullScreen = settings.Fullscreen;
            // Cambiar la calidad recompila recursos: solo cuando de verdad cambia.
            if (appliedQuality != settings.Quality) { QualitySettings.SetQualityLevel(settings.Quality, true); appliedQuality = settings.Quality; }
        }
    }
}
