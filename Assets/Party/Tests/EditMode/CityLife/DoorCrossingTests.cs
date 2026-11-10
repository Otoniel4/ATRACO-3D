using NUnit.Framework;
using Alarma.AI.CityLife;

namespace Alarma.Tests.CityLife
{
    // El cruce de puertas nunca deja a un cliente esperando para siempre, aunque el giro, el paso o la mano fallen.
    public sealed class DoorCrossingTests
    {
        private const float Frame = 1f / 60f;

        // Simula «seconds» segundos con las condiciones dadas y devuelve cuándo empujó por primera vez (o -1).
        private static float FirstPush(DoorCrossing door, float seconds, float facing, bool atStand, bool touching, bool doorOpen = false)
        {
            for (float t = 0f; t < seconds; t += Frame)
                if (door.Tick(Frame, true, doorOpen, facing, atStand, touching).Push) return t;
            return -1f;
        }

        [Test]
        public void EmpujaAunqueNoGireNiLlegueNiToque()
        {
            var door = new DoorCrossing();
            float pushed = FirstPush(door, 5f, facing: 0f, atStand: false, touching: false);
            Assert.That(pushed, Is.GreaterThanOrEqualTo(0f), "Nunca empujó");
            Assert.That(pushed, Is.LessThanOrEqualTo(DoorCrossing.TurnLimit + DoorCrossing.StepLimit + DoorCrossing.ReachLimit + .1f));
        }

        [Test]
        public void ConTodoBienEmpujaEnseguida()
        {
            var door = new DoorCrossing();
            float pushed = FirstPush(door, 2f, facing: 1f, atStand: true, touching: true);
            Assert.That(pushed, Is.InRange(0f, .1f));
        }

        [Test]
        public void SiLaPuertaNoAbreVuelveAEmpujar()
        {
            var door = new DoorCrossing();
            int pushes = 0;
            for (float t = 0f; t < 10f; t += Frame)
                if (door.Tick(Frame, true, false, 0f, false, false).Push) pushes++;
            Assert.That(pushes, Is.GreaterThanOrEqualTo(4));
            Assert.That(door.Pushes, Is.EqualTo(pushes));
        }

        [Test]
        public void ConLaPuertaAbiertaNoHaceNada()
        {
            var door = new DoorCrossing();
            FirstPush(door, 3f, 1f, true, true);
            var action = door.Tick(Frame, true, true, 1f, true, true);
            Assert.That(door.Phase, Is.EqualTo(DoorPhase.Idle));
            Assert.That(action.Push || action.Reach || action.Face, Is.False);
        }

        [Test]
        public void SiSePasaOtroClienteAdelanteDejaDeEmpujarYReinicia()
        {
            var door = new DoorCrossing();
            FirstPush(door, 3f, 0f, false, false);
            door.Tick(Frame, false, false, 0f, false, false);
            Assert.That(door.Phase, Is.EqualTo(DoorPhase.Idle));
            Assert.That(door.Pushes, Is.EqualTo(0));
        }

        [Test]
        public void ConLaPuertaAbiertaConservaLosEmpujesHastaQueSeCierra()
        {
            var door = new DoorCrossing();
            for (float t = 0f; t < 4f; t += Frame) door.Tick(Frame, true, false, 0f, false, false);
            int pushes = door.Pushes;
            Assert.That(pushes, Is.GreaterThanOrEqualTo(2));
            door.Tick(Frame, false, true, 0f, false, false); // abierta: camina
            Assert.That(door.Pushes, Is.EqualTo(pushes));
            door.Tick(Frame, false, false, 0f, false, false); // se fue y la puerta cerró
            Assert.That(door.Pushes, Is.EqualTo(0));
        }

        [Test]
        public void SiLaPuertaSeCierraAntesDePasarEmpujaOtraVez()
        {
            var door = new DoorCrossing();
            FirstPush(door, 3f, 1f, true, true);
            for (float t = 0f; t < .5f; t += Frame) door.Tick(Frame, true, true, 1f, true, true); // abierta: camina
            float again = FirstPush(door, 3f, 1f, true, true); // se cerró con él todavía de este lado
            Assert.That(again, Is.InRange(0f, .1f));
        }
    }
}
