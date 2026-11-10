using System.Linq;
using NUnit.Framework;
using Alarma.AI.CityLife;

namespace Alarma.Tests.CityLife
{
    // Varias cajas: cada cliente va a la que tiene menos gente y todas atienden a la vez.
    public sealed class CheckoutLanesTests
    {
        // Llega al instante a donde lo mandan: la prueba mide decisiones, no recorridos.
        private sealed class InstantMotor : IPedestrianMotor
        {
            public bool MoveTo(CityPoint destination) => true;
            public bool HasArrived => true;
            public void Stop() { }
        }

        private static CityPoint P(float x, float z) => new CityPoint(x, 0f, z);

        private static PedestrianPlan Plan(int lanes) => new PedestrianPlan
        {
            Walk = new[] { P(0, 10) }, Entry = new[] { P(0, 8) }, Exit = new[] { P(0, 9) },
            BrowseStations = Enumerable.Range(0, 6).Select(i => P(i, 0)).ToArray(),
            Queues = Enumerable.Range(0, lanes).Select(l => new[] { P(l * 2, 5), P(l * 2, 4), P(l * 2, 3) }).ToArray(),
            Looks = new int[0], Buys = true, VisitsShop = true, OneVisit = true, WalletCents = 100000,
        };

        private static void Run(PedestrianRoutine routine, PedestrianState until, float seconds = 60f)
        {
            for (float t = 0f; t < seconds && routine.State < until; t += .1f) routine.Tick(.1f);
        }

        [Test]
        public void EligeLaCajaConMenosGente()
        {
            var lanes = new CheckoutLanes(3, 3);
            Assert.That(lanes.Choose(), Is.EqualTo(0));
            lanes[0].TryJoin(1);
            Assert.That(lanes.Choose(), Is.EqualTo(1));
            lanes[1].TryJoin(2);
            lanes[2].TryJoin(3);
            lanes[0].TryJoin(4);
            Assert.That(lanes.Choose(), Is.EqualTo(1), "Empate entre la 2 y la 3: va a la primera");
        }

        [Test]
        public void ConTodasLasFilasLlenasNoHayCaja()
        {
            var lanes = new CheckoutLanes(2, 1);
            lanes[0].TryJoin(1); lanes[1].TryJoin(2);
            Assert.That(lanes.Choose(), Is.EqualTo(-1));
        }

        [Test]
        public void CadaCajaAtiendeAlPrimeroDeSuFila()
        {
            var lanes = new CheckoutLanes(2, 3);
            lanes[0].TryJoin(1); lanes[0].TryJoin(2); lanes[1].TryJoin(3);
            Assert.That(lanes.IsFront(1), Is.True);
            Assert.That(lanes.IsFront(2), Is.False);
            Assert.That(lanes.IsFront(3), Is.True, "El primero de la segunda caja también es atendido");
            lanes.Release(1);
            Assert.That(lanes.IsFront(2), Is.True);
        }

        [Test]
        public void TresClientesUsanLasTresCajasYPaganALaVez()
        {
            var lanes = new CheckoutLanes(3, 3);
            var service = new ShopService("super", lanes, 6, 50, 100);
            var routines = Enumerable.Range(1, 3).Select(id => new PedestrianRoutine(id, new InstantMotor(), lanes, Plan(3), service)).ToArray();
            foreach (var routine in routines) routine.Start();
            foreach (var routine in routines) Run(routine, PedestrianState.Queueing);
            Assert.That(routines.Select(r => r.Lane), Is.EquivalentTo(new[] { 0, 1, 2 }), "No se repartieron entre las cajas");
            foreach (var routine in routines) Run(routine, PedestrianState.ReceivingReceipt);
            Assert.That(routines.All(r => r.State >= PedestrianState.ReceivingReceipt), Is.True, "Alguna caja no cobró");
            Assert.That(service.PurchaseCount, Is.EqualTo(3));
        }

        [Test]
        public void ConUnaCajaFuncionaComoAntes()
        {
            var lanes = new CheckoutLanes(1, 3);
            var service = new ShopService("mini", lanes, 6, 50, 100);
            var first = new PedestrianRoutine(1, new InstantMotor(), lanes, Plan(1), service);
            var second = new PedestrianRoutine(2, new InstantMotor(), lanes, Plan(1), service);
            first.Start(); second.Start();
            Run(first, PedestrianState.Queueing); Run(second, PedestrianState.Queueing);
            Assert.That(first.Lane, Is.EqualTo(0));
            Assert.That(second.Lane, Is.EqualTo(0));
            Assert.That(lanes.IsFront(1) != lanes.IsFront(2), Is.True, "Solo uno a la vez en la única caja");
        }
    }
}
