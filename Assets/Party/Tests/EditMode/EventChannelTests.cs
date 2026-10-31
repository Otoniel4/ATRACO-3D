using System;
using System.Collections.Generic;
using Alarma.Core.Events;
using NUnit.Framework;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Alarma.Core.Tests
{
    public sealed class EventChannelTests
    {
        private readonly List<ScriptableObject> channels = new List<ScriptableObject>();

        [TearDown]
        public void TearDown()
        {
            foreach (ScriptableObject channel in channels)
            {
                Object.DestroyImmediate(channel);
            }

            channels.Clear();
        }

        [Test]
        public void RaiseWithoutSubscribersDoesNotThrow()
        {
            VoidEventChannel signal = CreateChannel<VoidEventChannel>();
            IntEventChannel number = CreateChannel<IntEventChannel>();

            Assert.DoesNotThrow(signal.Raise);
            Assert.DoesNotThrow(() => number.Raise(42));
        }

        [Test]
        public void VoidEventNotifiesIndependentSubscribers()
        {
            VoidEventChannel channel = CreateChannel<VoidEventChannel>();
            int firstCalls = 0;
            int secondCalls = 0;
            channel.Raised += () => firstCalls++;
            channel.Raised += () => secondCalls++;

            channel.Raise();

            Assert.That(firstCalls, Is.EqualTo(1));
            Assert.That(secondCalls, Is.EqualTo(1));
        }

        [Test]
        public void RemovedSubscriberReceivesNoFurtherNotifications()
        {
            IntEventChannel channel = CreateChannel<IntEventChannel>();
            var received = new List<int>();
            Action<int> listener = received.Add;
            channel.Raised += listener;
            channel.Raise(10);
            channel.Raised -= listener;

            channel.Raise(20);

            Assert.That(received, Is.EqualTo(new[] { 10 }));
        }

        [Test]
        public void SubscriberCanUnsubscribeDuringNotification()
        {
            VoidEventChannel channel = CreateChannel<VoidEventChannel>();
            int oneShotCalls = 0;
            int persistentCalls = 0;
            Action oneShot = null;
            oneShot = () =>
            {
                oneShotCalls++;
                channel.Raised -= oneShot;
            };
            channel.Raised += oneShot;
            channel.Raised += () => persistentCalls++;

            channel.Raise();
            channel.Raise();

            Assert.That(oneShotCalls, Is.EqualTo(1));
            Assert.That(persistentCalls, Is.EqualTo(2));
        }

        [Test]
        public void SeparateAssetsDoNotShareSubscribers()
        {
            VoidEventChannel first = CreateChannel<VoidEventChannel>();
            VoidEventChannel second = CreateChannel<VoidEventChannel>();
            int calls = 0;
            first.Raised += () => calls++;

            second.Raise();

            Assert.That(calls, Is.Zero);
        }

        [TestCase(-12)]
        [TestCase(0)]
        [TestCase(42)]
        public void IntegerPayloadReachesSubscribersUnchanged(int expected)
        {
            IntEventChannel channel = CreateChannel<IntEventChannel>();
            int? received = null;
            channel.Raised += value => received = value;

            channel.Raise(expected);

            Assert.That(received, Is.EqualTo(expected));
        }

        [Test]
        public void FloatPayloadPreservesFractionalValues()
        {
            FloatEventChannel channel = CreateChannel<FloatEventChannel>();
            float? received = null;
            channel.Raised += value => received = value;

            channel.Raise(0.25f);

            Assert.That(received, Is.EqualTo(0.25f));
        }

        private T CreateChannel<T>() where T : ScriptableObject
        {
            T channel = ScriptableObject.CreateInstance<T>();
            channels.Add(channel);
            return channel;
        }
    }
}
