using System.Collections.Generic;
using Alarma.Core.Events;
using Alarma.Heist.Alert;
using NUnit.Framework;

namespace Alarma.Heist.Tests
{
    // Alerta del local (GDD 8 y Task 15): sigilo → sospecha → alarma → policía en camino → asalto.
    public sealed class AlertMachineTests
    {
        private const float AlarmSeconds = 3f, CalmSeconds = 20f;

        private static AlertMachine Create() => new AlertMachine(AlarmSeconds, CalmSeconds);

        [Test]
        public void SuspicionFillsAndFadesBackToStealth()
        {
            var machine = Create();
            machine.Tick(.4f, .1f);
            Assert.AreEqual(AlertLevel.Suspicion, machine.Level);
            machine.Tick(0f, .1f);
            Assert.AreEqual(AlertLevel.Stealth, machine.Level);
        }

        [Test]
        public void FullSuspicionOrAReportTriggersTheAlarm()
        {
            var bySuspicion = Create();
            bySuspicion.Tick(1f, .1f);
            Assert.AreEqual(AlertLevel.Alarm, bySuspicion.Level);

            var byReport = Create();
            byReport.Report();
            Assert.AreEqual(AlertLevel.Alarm, byReport.Level);
            Assert.AreEqual(1f, byReport.Suspicion, "Con la alarma, el medidor queda lleno.");
        }

        [Test]
        public void AlarmFollowsThePoliceUntilTheyWithdraw()
        {
            var machine = Create();
            var seen = new List<AlertLevel>();
            machine.LevelChanged += seen.Add;
            machine.Report();
            machine.PoliceUpdate(PoliceResponsePhase.OnTheWay);
            machine.Tick(0f, 1f);
            Assert.AreEqual(AlertLevel.Alarm, machine.Level, "La alarma suena unos segundos antes de avanzar.");
            machine.Tick(0f, AlarmSeconds);
            machine.PoliceUpdate(PoliceResponsePhase.OnScene);
            machine.Tick(0f, .1f);
            machine.PoliceUpdate(PoliceResponsePhase.Withdrawn);
            machine.Tick(0f, .1f);
            CollectionAssert.AreEqual(new[] { AlertLevel.Alarm, AlertLevel.PoliceOnTheWay, AlertLevel.Assault, AlertLevel.Stealth }, seen);
        }

        [Test]
        public void AlarmWithoutPoliceCalmsDown()
        {
            var machine = Create();
            machine.Report();
            machine.Tick(0f, CalmSeconds - 1f);
            Assert.AreEqual(AlertLevel.Alarm, machine.Level);
            machine.Tick(0f, 1f);
            Assert.AreEqual(AlertLevel.Stealth, machine.Level);
        }

        [Test]
        public void PoliceFromAnotherPlaceDoesNotRaiseTheAlert()
        {
            var machine = Create();
            machine.PoliceUpdate(PoliceResponsePhase.OnScene);
            machine.Tick(0f, 10f);
            Assert.AreEqual(AlertLevel.Stealth, machine.Level);
        }
    }
}
