using System;

namespace Alarma.AI.CityLife
{
    public readonly struct CityPoint
    {
        public readonly float X, Y, Z;
        public CityPoint(float x, float y, float z) { X = x; Y = y; Z = z; }
    }

    public interface IPedestrianMotor
    {
        bool MoveTo(CityPoint destination);
        bool HasArrived { get; }
        void Stop();
    }

    public enum PedestrianState { Inactive, Walking, Entering, Browsing, WaitingForSpace, Queueing, Paying, ClearingCounter, Leaving, Resting, Failed }

    public sealed class PedestrianPlan
    {
        public CityPoint[] Walk = Array.Empty<CityPoint>();
        public CityPoint[] Entry = Array.Empty<CityPoint>();
        public CityPoint Browse;
        public CityPoint[] Queue = Array.Empty<CityPoint>();
        public CityPoint[] Exit = Array.Empty<CityPoint>();
        public float BrowseSeconds = 3f, PaySeconds = 2f, RestSeconds = 2f;
        public float TravelTimeout = 35f, QueueTimeout = 25f;
        public bool VisitsShop = true;
    }

    // Decide la rutina; movimiento, presentación, cola y población tienen otras responsabilidades.
    public sealed class PedestrianRoutine
    {
        private readonly int id;
        private readonly IPedestrianMotor motor;
        private readonly ShopQueue queue;
        private readonly PedestrianPlan plan;
        private int point, queueIndex = -1;
        private float stateTime;
        private bool browseStarted;
        public PedestrianState State { get; private set; } = PedestrianState.Inactive;
        public bool Carrying { get; private set; }
        public event Action<PedestrianState> StateChanged;
        public event Action Purchased;
        public event Action Failed;

        public PedestrianRoutine(int id, IPedestrianMotor motor, ShopQueue queue, PedestrianPlan plan)
        {
            this.id = id;
            this.motor = motor ?? throw new ArgumentNullException(nameof(motor));
            this.queue = queue ?? throw new ArgumentNullException(nameof(queue));
            this.plan = plan ?? throw new ArgumentNullException(nameof(plan));
        }

        public void Start()
        {
            if (plan.Walk.Length == 0 || (plan.VisitsShop && (plan.Entry.Length == 0 || plan.Queue.Length < queue.Capacity || plan.Exit.Length == 0)))
            { Fail(); return; }
            Carrying = false; point = 0; Change(PedestrianState.Walking);
            Move(plan.Walk[point]);
        }

        public void Tick(float deltaTime)
        {
            if (deltaTime < 0 || float.IsNaN(deltaTime) || float.IsInfinity(deltaTime)) throw new ArgumentOutOfRangeException(nameof(deltaTime));
            stateTime += deltaTime;
            switch (State)
            {
                case PedestrianState.Walking:
                    if (TimedOut()) break;
                    if (!motor.HasArrived) break;
                    if (++point < plan.Walk.Length) Move(plan.Walk[point]);
                    else if (plan.VisitsShop)
                    { Carrying = false; point = 0; Change(PedestrianState.Entering); Move(plan.Entry[point]); }
                    else { motor.Stop(); Change(PedestrianState.Resting); }
                    break;
                case PedestrianState.Entering:
                    if (TimedOut()) break;
                    if (!motor.HasArrived) break;
                    if (++point < plan.Entry.Length) Move(plan.Entry[point]);
                    else { browseStarted = false; Change(PedestrianState.Browsing); Move(plan.Browse); }
                    break;
                case PedestrianState.Browsing:
                    if (!motor.HasArrived) { TimedOut(); break; }
                    if (!browseStarted) { browseStarted = true; stateTime = 0; }
                    if (stateTime < plan.BrowseSeconds) break;
                    motor.Stop(); Change(PedestrianState.WaitingForSpace);
                    break;
                case PedestrianState.WaitingForSpace:
                    if (queue.TryJoin(id)) { queueIndex = -1; Change(PedestrianState.Queueing); UpdateQueueTarget(); }
                    else if (stateTime > plan.QueueTimeout) BeginExit();
                    break;
                case PedestrianState.Queueing:
                    if (stateTime > plan.QueueTimeout) { BeginExit(); break; }
                    UpdateQueueTarget();
                    if (State != PedestrianState.Queueing) break;
                    if (queueIndex == 0 && motor.HasArrived) { motor.Stop(); Change(PedestrianState.Paying); }
                    break;
                case PedestrianState.Paying:
                    if (stateTime < plan.PaySeconds) break;
                    Carrying = true; Purchased?.Invoke(); point = 0;
                    // Se conserva el primer puesto hasta apartarse del mostrador.
                    Change(PedestrianState.ClearingCounter); Move(plan.Exit[point]);
                    break;
                case PedestrianState.ClearingCounter:
                    if (TimedOut()) break;
                    if (!motor.HasArrived) break;
                    queue.Release(id); Change(PedestrianState.Leaving);
                    if (++point < plan.Exit.Length) Move(plan.Exit[point]);
                    else { motor.Stop(); Change(PedestrianState.Resting); }
                    break;
                case PedestrianState.Leaving:
                    if (TimedOut()) break;
                    if (!motor.HasArrived) break;
                    if (++point < plan.Exit.Length) Move(plan.Exit[point]);
                    else { motor.Stop(); Change(PedestrianState.Resting); }
                    break;
                case PedestrianState.Resting:
                    if (stateTime < plan.RestSeconds) break;
                    point = 0; Change(PedestrianState.Walking); Move(plan.Walk[point]);
                    break;
            }
        }

        private void UpdateQueueTarget()
        {
            int index = queue.IndexOf(id);
            if (index < 0 || index >= plan.Queue.Length) { Fail(); return; }
            if (index == queueIndex) return;
            queueIndex = index; Move(plan.Queue[index]);
        }

        private void BeginExit()
        {
            queue.Release(id); point = 0;
            if (plan.Exit.Length == 0) { motor.Stop(); Change(PedestrianState.Resting); return; }
            Change(PedestrianState.Leaving); Move(plan.Exit[point]);
        }

        private bool TimedOut()
        {
            if (stateTime <= plan.TravelTimeout) return false;
            Fail(); return true;
        }

        private void Move(CityPoint point)
        {
            stateTime = 0;
            if (!motor.MoveTo(point)) Fail();
        }

        private void Change(PedestrianState state) { State = state; stateTime = 0; StateChanged?.Invoke(state); }
        private void Fail() { queue.Release(id); motor.Stop(); Change(PedestrianState.Failed); Failed?.Invoke(); }
        public void Reset() { queue.Release(id); motor.Stop(); Carrying = false; queueIndex = -1; Change(PedestrianState.Inactive); }
    }
}
