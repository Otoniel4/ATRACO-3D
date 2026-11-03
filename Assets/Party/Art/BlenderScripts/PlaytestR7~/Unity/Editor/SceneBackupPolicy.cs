namespace Alarma.City.Playtest.Editor
{
    public enum SceneBackupMode { None, AssignSavedPath, PreserveOriginalPath }
    public static class SceneBackupPolicy
    {
        public static SceneBackupMode Choose(bool hasPath,bool dirty)
        {
            // Una escena sin ruta bloquea NewScene(Additive), incluso después de elegir «Don't Save».
            if(!hasPath)return SceneBackupMode.AssignSavedPath;
            return dirty?SceneBackupMode.PreserveOriginalPath:SceneBackupMode.None;
        }
    }
}
