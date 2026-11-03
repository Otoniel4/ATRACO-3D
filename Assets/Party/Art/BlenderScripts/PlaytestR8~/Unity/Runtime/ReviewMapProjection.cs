using UnityEngine;
namespace Alarma.City.Playtest
{
    public static class ReviewMapProjection
    {
        public static Vector2 Normalized(Vector3 position)=>new Vector2(Mathf.Clamp01((position.x+2000)/4000),Mathf.Clamp01((2000-position.z)/4000));
    }
}
