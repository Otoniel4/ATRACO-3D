using System.Collections.Generic;
using UnityEngine;

namespace Alarma.Core.Sets
{
    // Conjunto en tiempo de ejecución (patrón Runtime Set con ScriptableObject): quienes pueden ser buscados por la
    // policía se anotan al aparecer y se borran al desaparecer. La policía lo recorre sin conocer al jugador ni usar
    // búsquedas en la escena; con red, cada jugador conectado se anota igual.
    [CreateAssetMenu(menuName = "Alarma/Conjuntos/Sospechosos", fileName = "Sospechosos")]
    public sealed class SuspectSet : ScriptableObject
    {
        private readonly List<GameObject> items = new List<GameObject>();

        public IReadOnlyList<GameObject> Items => items;

        public void Add(GameObject suspect)
        {
            items.RemoveAll(item => item == null); // restos de una partida anterior en el editor
            if (suspect != null && !items.Contains(suspect)) items.Add(suspect);
        }

        public void Remove(GameObject suspect) => items.Remove(suspect);
    }
}
