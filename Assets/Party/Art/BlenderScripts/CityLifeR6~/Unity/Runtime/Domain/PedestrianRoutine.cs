using System;
namespace Alarma.AI.CityLife
{
    public readonly struct CityPoint
    {
        public readonly float X,Y,Z;
        public CityPoint(float x,float y,float z){X=x;Y=y;Z=z;}
    }
    public interface IPedestrianMotor {bool MoveTo(CityPoint destination);bool HasArrived{get;}void Stop();}
    public enum PedestrianState {Inactive,Walking,WaitingForEntry,Entering,Browsing,PickingUp,WaitingForSpace,Queueing,Placing,Scanning,Paying,ReceivingReceipt,Collecting,ClearingCounter,Leaving,Resting,Failed}
    public sealed class PedestrianPlan
    {
        public CityPoint[] Walk=Array.Empty<CityPoint>(),Entry=Array.Empty<CityPoint>(),BrowseStations=Array.Empty<CityPoint>(),Queue=Array.Empty<CityPoint>(),Exit=Array.Empty<CityPoint>();
        public float BrowseSeconds=1.5f,PaySeconds=.9f,RestSeconds=3f,TravelTimeout=80f,QueueTimeout=80f;
        public int WalletCents=10000;
        public bool VisitsShop=true;
    }
    // Máquina de tareas. Los tiempos de interacción empiezan al llegar, nunca durante el trayecto.
    public sealed class PedestrianRoutine
    {
        private readonly int id;private readonly IPedestrianMotor motor;private readonly ShopQueue queue;private readonly ShopService service;private readonly PedestrianPlan plan;
        private int point,queueIndex=-1;private float time;private bool browsing;private ShoppingSession session;
        public PedestrianState State{get;private set;}=PedestrianState.Inactive;
        public ShoppingSession Session=>session;
        public float StateSeconds=>time;
        public bool Carrying=>session!=null && (session.Stage==ShoppingStage.InHand || session.Stage==ShoppingStage.Collected);
        public bool HoldingBag=>session!=null && session.Stage==ShoppingStage.Collected;
        public bool Interaction=>State>=PedestrianState.Placing && State<=PedestrianState.Collecting || State==PedestrianState.PickingUp;
        public event Action<PedestrianState> StateChanged;public event Action Purchased;public event Action Failed;
        public PedestrianRoutine(int id,IPedestrianMotor motor,ShopQueue queue,PedestrianPlan plan,ShopService service)
        {this.id=id;this.motor=motor??throw new ArgumentNullException(nameof(motor));this.queue=queue??throw new ArgumentNullException(nameof(queue));this.plan=plan??throw new ArgumentNullException(nameof(plan));this.service=service??throw new ArgumentNullException(nameof(service));}
        public void Start()
        {
            if(plan.Walk.Length==0 || (plan.VisitsShop && (plan.Entry.Length==0 || plan.BrowseStations.Length==0 || plan.Queue.Length<queue.Capacity || plan.Exit.Length==0))){Fail();return;}
            point=0;Change(PedestrianState.Walking);Move(plan.Walk[0]);
        }
        public void Tick(float deltaTime)
        {
            if(deltaTime<0 || float.IsNaN(deltaTime) || float.IsInfinity(deltaTime))throw new ArgumentOutOfRangeException(nameof(deltaTime));time+=deltaTime;
            switch(State)
            {
                case PedestrianState.Walking:
                    if(Timeout() || !motor.HasArrived)break;
                    if(++point<plan.Walk.Length)Move(plan.Walk[point]);else {motor.Stop();Change(plan.VisitsShop?PedestrianState.WaitingForEntry:PedestrianState.Resting);}break;
                case PedestrianState.WaitingForEntry:
                    if(service.TryBegin(id,plan.WalletCents,out session)){point=0;Change(PedestrianState.Entering);Move(plan.Entry[0]);}
                    else if(time>plan.QueueTimeout)Change(PedestrianState.Resting);break;
                case PedestrianState.Entering:
                    if(Timeout() || !motor.HasArrived)break;
                    if(++point<plan.Entry.Length)Move(plan.Entry[point]);else {browsing=false;Change(PedestrianState.Browsing);Move(plan.BrowseStations[session.Station]);}break;
                case PedestrianState.Browsing:
                    if(!motor.HasArrived){Timeout();break;}
                    if(!browsing){browsing=true;time=0;motor.Stop();}
                    if(time>=plan.BrowseSeconds)Change(PedestrianState.PickingUp);break;
                case PedestrianState.PickingUp:
                    if(time<.8f)break;if(!service.PickUp(id)){Fail();break;}
                    Change(PedestrianState.WaitingForSpace);break;
                case PedestrianState.WaitingForSpace:
                    if(queue.TryJoin(id)){queueIndex=-1;Change(PedestrianState.Queueing);UpdateQueue();}
                    else if(time>plan.QueueTimeout)BeginExit();break;
                case PedestrianState.Queueing:
                    if(time>plan.QueueTimeout){BeginExit();break;}UpdateQueue();
                    if(queueIndex==0 && motor.HasArrived){motor.Stop();Change(PedestrianState.Placing);}break;
                case PedestrianState.Placing:
                    if(time>=.8f){if(service.Place(id))Change(PedestrianState.Scanning);else Fail();}break;
                case PedestrianState.Scanning:
                    if(time>=1.2f){if(service.Scan(id))Change(PedestrianState.Paying);else Fail();}break;
                case PedestrianState.Paying:
                    if(time>=plan.PaySeconds){if(service.Pay(id)){Purchased?.Invoke();plan.WalletCents=session.WalletCents;Change(PedestrianState.ReceivingReceipt);}else BeginExit();}break;
                case PedestrianState.ReceivingReceipt:if(time>=.8f)Change(PedestrianState.Collecting);break;
                case PedestrianState.Collecting:
                    if(time<.8f)break;if(!service.Collect(id)){Fail();break;}point=0;Change(PedestrianState.ClearingCounter);Move(plan.Exit[0]);break;
                case PedestrianState.ClearingCounter:
                    if(Timeout() || !motor.HasArrived)break;
                    queue.Release(id);service.Release(id);NextExit();break;
                case PedestrianState.Leaving:
                    if(!Timeout() && motor.HasArrived)NextExit();break;
                case PedestrianState.Resting:
                    if(time>=plan.RestSeconds){session=null;point=0;Change(PedestrianState.Walking);Move(plan.Walk[0]);}break;
            }
        }
        private void NextExit(){Change(PedestrianState.Leaving);if(++point<plan.Exit.Length)Move(plan.Exit[point]);else {motor.Stop();Change(PedestrianState.Resting);}}
        private void BeginExit(){queue.Release(id);service.Release(id);session=null;point=0;Change(PedestrianState.Leaving);if(plan.Exit.Length>0)Move(plan.Exit[0]);else Change(PedestrianState.Resting);}
        private void UpdateQueue(){int i=queue.IndexOf(id);if(i<0 || i>=plan.Queue.Length){Fail();return;}if(i!=queueIndex){queueIndex=i;Move(plan.Queue[i]);}}
        private bool Timeout(){if(time<=plan.TravelTimeout)return false;Fail();return true;}
        private void Move(CityPoint p){time=0;if(!motor.MoveTo(p))Fail();}
        private void Change(PedestrianState state){State=state;time=0;StateChanged?.Invoke(state);}
        private void Fail(){queue.Release(id);service.Release(id);motor.Stop();Change(PedestrianState.Failed);Failed?.Invoke();}
        public void Reset(){queue.Release(id);service.Release(id);motor.Stop();session=null;queueIndex=-1;Change(PedestrianState.Inactive);}
    }
}
