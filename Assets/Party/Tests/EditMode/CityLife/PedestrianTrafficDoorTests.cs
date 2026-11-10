using System.Collections.Generic;
using NUnit.Framework;
using Alarma.AI.CityLife;

namespace Alarma.Tests.CityLife
{
    // Quien empuja una puerta queda adelantado fuera del centro de su celda. Ese cuerpo tapa el paso a los demás, pero
    // al abrirse la puerta no debe taparle a él su propio camino recto (antes rodeaba y volvía a empujar).
    public sealed class PedestrianTrafficDoorTests
    {
        // Grilla de 3 columnas × 4 filas; la puerta está entre las filas 1 y 2 de la columna del medio.
        private sealed class Grid : ITrafficMap
        {
            public int Count => 12;
            public int[] Neighbours(int cell)
            {
                int x = cell % 3, z = cell / 3;
                var list = new List<int>();
                if (x > 0) list.Add(cell - 1);
                if (x < 2) list.Add(cell + 1);
                if (z > 0) list.Add(cell - 3);
                if (z < 3) list.Add(cell + 3);
                return list.ToArray();
            }
            public CityPoint Position(int cell) => new CityPoint(cell % 3, 0f, cell / 3);
        }

        private static int Cell(int x, int z) => z * 3 + x;

        // El cuerpo adelantado de quien está en «pusher» tapa el paso por la puerta (1,1)→(1,2) a todos menos a él.
        private static System.Func<int, int, int, bool> DoorBody(int pusher)
            => (from, to, mine) => !(from == Cell(1, 1) && to == Cell(1, 2) && mine != pusher);

        [Test]
        public void QuienEmpujaVaDerechoPorLaPuertaAbierta()
        {
            var traffic = new PedestrianTraffic(new Grid());
            Assert.That(traffic.TryAdd(1, Cell(1, 0)), Is.True);
            Assert.That(traffic.SetGoal(1, Cell(1, 3)), Is.True);
            var steps = traffic.StepAvoidingOthers(DoorBody(Cell(1, 0)));
            Assert.That(steps[1], Is.EqualTo(Cell(1, 1)), "Rodeó en vez de ir derecho hacia la puerta");
        }

        [Test]
        public void LosDemasNoPasanPorEncimaDeQuienEmpuja()
        {
            var traffic = new PedestrianTraffic(new Grid());
            traffic.TryAdd(2, Cell(1, 1));
            traffic.SetGoal(2, Cell(1, 3));
            // El cuerpo adelantado es de otro (celda 0,0): para este cliente el paso por la puerta sigue tapado.
            var steps = traffic.StepAvoidingOthers(DoorBody(Cell(0, 0)));
            Assert.That(steps[2], Is.Not.EqualTo(Cell(1, 2)));
        }

        [Test]
        public void LaFirmaAnteriorSigueFuncionando()
        {
            var traffic = new PedestrianTraffic(new Grid());
            traffic.TryAdd(3, Cell(0, 0));
            traffic.SetGoal(3, Cell(0, 3));
            var steps = traffic.Step((from, to) => true);
            Assert.That(steps[3], Is.EqualTo(Cell(0, 1)));
        }
    }
}
