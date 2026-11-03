using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    [Serializable] public sealed class TrafficCell {public Vector3 Position;public int[] Links=Array.Empty<int>();}
    [CreateAssetMenu(menuName="Alarma/Ciudad/Grafo peatonal")]
    public sealed class TrafficGraph : ScriptableObject,ITrafficMap
    {
        public TrafficCell[] Cells=Array.Empty<TrafficCell>();
        public int Count=>Cells.Length;
        public int[] Neighbours(int cell)=>Cells[cell].Links;
        public CityPoint Position(int cell){Vector3 p=Cells[cell].Position;return new CityPoint(p.x,p.y,p.z);}
        public int Nearest(Vector3 point,float maximumDistance=1f)
        {
            float best=maximumDistance*maximumDistance;int index=-1;
            for(int i=0;i<Cells.Length;i++){float d=(Cells[i].Position-point).sqrMagnitude;if(d<best){best=d;index=i;}}
            return index;
        }
    }
}
