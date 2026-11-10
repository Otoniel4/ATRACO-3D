using System.Collections.Generic;
using NUnit.Framework;
using Alarma.AI.CityLife;

namespace Alarma.Tests.CityLife
{
    // Rendimiento sin cambiar decisiones: quienes planifican con la misma clave comparten rutas y consultas de paso.
    // Antes cada cliente repetía todas las consultas físicas del local y los pasos de la multitud daban tirones.
    public sealed class PedestrianTrafficSharedPlanTests
    {
        private const int Side = 6;

        private sealed class Grid : ITrafficMap
        {
            public int Count => Side * Side;
            public int[] Neighbours(int cell)
            {
                int x = cell % Side, z = cell / Side;
                var list = new List<int>();
                if (x > 0) list.Add(cell - 1);
                if (x < Side - 1) list.Add(cell + 1);
                if (z > 0) list.Add(cell - Side);
                if (z < Side - 1) list.Add(cell + Side);
                return list.ToArray();
            }
            public CityPoint Position(int cell) => new CityPoint(cell % Side, 0f, cell / Side);
        }

        private static int Cell(int x, int z) => z * Side + x;

        // Un muro en la columna 3, con hueco solo en la fila 5: el paso depende únicamente de las dos celdas.
        private static bool Wall(int from, int to)
            => !((from % Side == 3 || to % Side == 3) && from / Side != 5 && to / Side != 5);

        private static PedestrianTraffic Crowd()
        {
            var traffic = new PedestrianTraffic(new Grid());
            int[] starts = { Cell(0, 0), Cell(1, 0), Cell(0, 2), Cell(1, 3), Cell(2, 1), Cell(0, 4) };
            for (int i = 0; i < starts.Length; i++)
            {
                Assert.That(traffic.TryAdd(i + 1, starts[i]), Is.True);
                Assert.That(traffic.SetGoal(i + 1, Cell(5, 0)), Is.True);
            }
            return traffic;
        }

        [Test]
        public void CompartirLaClaveNoCambiaNingunPaso()
        {
            var alone = Crowd();
            var shared = Crowd();
            for (int step = 0; step < 12; step++)
            {
                var expected = alone.StepAvoidingOthers((from, to, mine) => Wall(from, to));
                var actual = shared.StepAvoidingOthers((from, to, mine) => Wall(from, to), cell => -1);
                Assert.That(actual, Is.EquivalentTo(expected), $"Paso {step}");
            }
        }

        [Test]
        public void CompartirLaClaveConsultaMuchoMenos()
        {
            int alone = 0, shared = 0;
            Crowd().StepAvoidingOthers((from, to, mine) => { alone++; return Wall(from, to); });
            Crowd().StepAvoidingOthers((from, to, mine) => { shared++; return Wall(from, to); }, cell => -1);
            // Seis clientes con el mismo destino: una sola búsqueda en vez de seis.
            Assert.That(shared * 3, Is.LessThan(alone), $"Consultas compartidas {shared}, por cliente {alone}");
        }

        [Test]
        public void QuienEmpujaConservaSuClavePropia()
        {
            int pusher = Cell(2, 2);
            var traffic = new PedestrianTraffic(new Grid());
            traffic.TryAdd(1, pusher);
            traffic.SetGoal(1, Cell(2, 5));
            // Su cuerpo adelantado tapa (2,2)→(2,3) a todos menos a él; los demás planifican con la clave común -1.
            var steps = traffic.StepAvoidingOthers((from, to, mine) => !(from == pusher && to == Cell(2, 3) && mine != pusher),
                cell => cell == pusher ? cell : -1);
            Assert.That(steps[1], Is.EqualTo(Cell(2, 3)), "Rodeó en vez de ir derecho");
        }
    }
}
