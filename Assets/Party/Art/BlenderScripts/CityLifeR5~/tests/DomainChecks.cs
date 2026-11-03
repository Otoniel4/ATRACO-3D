using System;
using Alarma.AI.CityLife;

sealed class Motor : IPedestrianMotor
{
    public bool HasArrived { get; set; } = true;
    public bool Accept = true;
    public CityPoint Last;
    public bool MoveTo(CityPoint point) { Last = point; return Accept; }
    public void Stop() { }
}
static class DomainChecks
{
    static int checks;
    static void Check(bool value, string name) { if (!value) throw new Exception(name); checks++; }
    static PedestrianPlan Plan() => new PedestrianPlan {
        Walk = new[] { new CityPoint(0,0,0) }, Entry = new[] { new CityPoint(1,0,0) },
        Browse = new CityPoint(2,0,0), Queue = new[] { new CityPoint(3,0,0), new CityPoint(4,0,0) },
        Exit = new[] { new CityPoint(5,0,0), new CityPoint(6,0,0) }, BrowseSeconds = 1, PaySeconds = 1, RestSeconds = 1 };
    static void ReachQueue(PedestrianRoutine routine) { routine.Start(); routine.Tick(0); routine.Tick(0); routine.Tick(0); routine.Tick(1.1f); routine.Tick(0); }
    static void Main()
    {
        var queue = new ShopQueue(2); Check(queue.TryJoin(10),"join"); Check(queue.TryJoin(10) && queue.Count==1,"idempotent join");
        Check(queue.TryJoin(11) && !queue.TryJoin(12),"bounded queue"); queue.Release(10); Check(queue.IndexOf(11)==0,"FIFO advance");
        queue.Release(999); Check(queue.Count==1,"cancel missing ticket"); queue.Clear(); Check(queue.Count==0,"clear");
        var aMotor=new Motor(); var bMotor=new Motor(); var a=new PedestrianRoutine(1,aMotor,queue,Plan()); var b=new PedestrianRoutine(2,bMotor,queue,Plan());
        int purchases=0; a.Purchased+=()=>purchases++;
        ReachQueue(a); ReachQueue(b); Check(queue.Count==2 && queue.IndexOf(1)==0,"two residents queued");
        a.Tick(0); b.Tick(0); Check(a.State==PedestrianState.Paying && b.State==PedestrianState.Queueing,"one payer");
        a.Tick(1.1f); Check(purchases==1 && a.Carrying && queue.IndexOf(1)==0,"purchase and reserved exit");
        b.Tick(0); Check(b.State==PedestrianState.Queueing,"next customer waits while payer clears counter");
        a.Tick(0); b.Tick(0); Check(queue.IndexOf(1)<0 && b.State==PedestrianState.Paying,"release after clearance");
        a.Tick(0); Check(a.State==PedestrianState.Resting,"leave building"); a.Reset(); Check(!a.Carrying && a.State==PedestrianState.Inactive,"pool reset");
        b.Reset(); Check(queue.Count==0,"disable releases ticket");
        var blockedMotor=new Motor { HasArrived=false }; var blocked=new PedestrianRoutine(3,blockedMotor,queue,Plan());
        blocked.Start(); blocked.Tick(36); Check(blocked.State==PedestrianState.Failed && queue.Count==0,"travel timeout releases reservation");
        var rejecting=new PedestrianRoutine(4,new Motor { Accept=false },queue,Plan()); rejecting.Start(); Check(rejecting.State==PedestrianState.Failed,"unreachable path");
        var invalid=Plan(); invalid.Walk=Array.Empty<CityPoint>(); var empty=new PedestrianRoutine(5,new Motor(),queue,invalid);empty.Start();Check(empty.State==PedestrianState.Failed,"empty route rejected");
        var browserMotor=new Motor();var browser=new PedestrianRoutine(6,browserMotor,queue,Plan()); browser.Start();browser.Tick(0);browser.Tick(0);
        browserMotor.HasArrived=false;browser.Tick(4);browserMotor.HasArrived=true;browser.Tick(0);
        Check(browser.State==PedestrianState.Browsing,"browse dwell starts on arrival");browser.Tick(.5f);Check(browser.State==PedestrianState.Browsing,"browse minimum dwell");
        bool threw=false;try{browser.Tick(float.NaN);}catch(ArgumentOutOfRangeException){threw=true;}Check(threw,"invalid clock input");
        Console.WriteLine("DOMAIN_CHECKS_PASSED "+checks);
    }
}
