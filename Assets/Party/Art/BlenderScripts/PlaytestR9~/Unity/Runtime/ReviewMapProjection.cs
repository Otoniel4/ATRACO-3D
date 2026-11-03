using UnityEngine;
namespace Alarma.City.Playtest
{
    public static class ReviewMapProjection
    {
        public static Vector2 Normalized(Vector3 position)=>new Vector2(Mathf.Clamp01((position.x+1500)/3000),Mathf.Clamp01((1500-position.z)/3000));
    }
}
