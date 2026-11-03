using System;
using UnityEngine;
namespace Alarma.City.Playtest
{
    public enum ReviewCategory { Character,Vehicle,Equipment,Prop }
    [Serializable] public sealed class ReviewModel
    {
        public string Id,Label;
        public ReviewCategory Category;
        public GameObject Prefab;
    }
    [CreateAssetMenu(menuName="Alarma datos/Catálogo de revisión")]
    public sealed class ReviewCatalog:ScriptableObject
    {
        public ReviewModel[] Models=Array.Empty<ReviewModel>();
    }
}
