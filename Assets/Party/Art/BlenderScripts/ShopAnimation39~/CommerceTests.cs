using System;
using Alarma.AI.CityLife;

static class CommerceTests
{
    static int checks;
    static void Check(bool ok,string label) { if(!ok) throw new Exception(label); checks++; }
    sealed class Motor : IPedestrianMotor
    {
        public bool HasArrived => true;
        public bool MoveTo(CityPoint p) => true;
        public void Stop() { }
    }
    static float[] Durations(CounterTiming t) => new[]{t.Pick,t.Place,t.Scan,t.Pay,t.Change,t.Bag};
    static readonly PedestrianState[] States = { PedestrianState.PickingUp,PedestrianState.Placing,PedestrianState.Scanning,
        PedestrianState.Paying,PedestrianState.ReceivingReceipt,PedestrianState.Collecting };
    static string Pose(ExchangeFrame f) => $"{f.Customer}/{f.Cashier}/{f.Product}/{f.Money}/{f.Change}/{f.Ticket}";
    static void Main()
    {
        CounterArrival();
        foreach(var timing in Profiles.All)
        foreach(bool bank in new[]{false,true})
        {
            var duration=Durations(timing);var standard=Durations(CounterTiming.Standard);
            for(int stage=0;stage<States.Length;stage++)
                for(int i=0;i<99;i++)
                {
                    float fraction=(i+.123f)/100f;
                    Check(Pose(CounterChoreography.Evaluate(States[stage],fraction*duration[stage],timing,bank))
                        ==Pose(CounterChoreography.Evaluate(States[stage],fraction*standard[stage],CounterTiming.Standard,bank)),
                        "Un perfil cambia el orden de los traspasos: "+States[stage]);
                }
            foreach(float dt in new[]{1f/60,1f/30,.1f}) Complete(timing,bank,dt);
        }
        float previous=0;
        for(int i=0;i<=1000;i++)
        {
            float t=i/1000f,v=CounterChoreography.Blend(t);
            Check(v>=previous-.000001f && v>=-.000001f && v<=1.000001f,"Interpolación sin retroceso ni sobrepaso");previous=v;
        }
        Check(CounterChoreography.Blend(.001f)<.00000002f && CounterChoreography.Blend(.999f)>.999999f,
            "Velocidad y aceleración suaves al apoyar y retirar objetos");
        Console.WriteLine("PASS perfiles: 6; compra/retiro completos: 36; 3 cajas y 3 clientes simultáneos por caso");
        Console.WriteLine("COMMERCE_CHECKS_PASSED "+checks);
    }
    sealed class DelayedMotor : IPedestrianMotor
    {
        public bool HasArrived { get; set; } = true;
        public CityPoint Destination;
        public bool MoveTo(CityPoint p) { Destination=p; HasArrived=p.X<100; return true; }
        public void Stop() { }
    }
    static void CounterArrival()
    {
        foreach(bool bank in new[]{false,true})
        {
            var lanes=new CheckoutLanes(1,1);var service=new ShopService("Mostrador",lanes,1,3,700,bank);
            var motor=new DelayedMotor();var p=new[]{new CityPoint(0,0,0)};
            var plan=new PedestrianPlan{Walk=p,Entry=p,BrowseStations=p,Exit=p,Queues=new[]{p},Counters=new[]{new CityPoint(100,0,4)},
                BrowseSeconds=.1f,OneVisit=true,WalletCents=10000};
            var routine=new PedestrianRoutine(7,motor,lanes,plan,service);routine.Start();
            for(int i=0;i<100 && routine.State!=PedestrianState.ApproachingCounter;i++)routine.Tick(.1f);
            Check(routine.State==PedestrianState.ApproachingCounter && motor.Destination.X==100,"Camina al mostrador después de llegar a la cabecera de fila");
            routine.Tick(3f);
            Check(routine.State==PedestrianState.ApproachingCounter && routine.Session.Stage==ShoppingStage.InHand,"No coloca ni cobra durante el trayecto");
            motor.HasArrived=true;routine.Tick(.1f);
            Check(routine.State==PedestrianState.Placing,"Solo empieza a colocar cuando llega");
            for(int i=0;i<300 && routine.State!=PedestrianState.ReceivingReceipt;i++)routine.Tick(.1f);
            Check(routine.Session.Stage==ShoppingStage.Paid,"Pago preparado para comprobar devolución");
            routine.CancelInteraction();
            Check(routine.State==PedestrianState.Leaving && lanes[0].Count==0,"Contacto imposible libera caja y salida");
            Check(routine.WalletCents==10000 && service.Stock==3 && service.PurchaseCount==0 && service.WithdrawalCount==0,
                "No cobra una operación cuya entrega se canceló");
            Check(service.TillCents==(bank?2100:0),"Restaura efectivo del comercio o banco");
        }
    }
    static void Complete(CounterTiming timing,bool bank,float dt)
    {
        var lanes=new CheckoutLanes(3,2);var service=new ShopService("Prueba",lanes,3,20,700,bank);
        var one=new[]{new CityPoint(0,0,0)};
        var queue=new[]{new CityPoint(0,0,0),new CityPoint(0,0,1)};
        var people=new PedestrianRoutine[3];
        for(int i=0;i<people.Length;i++)
        {
            var plan=new PedestrianPlan{Walk=one,Entry=one,BrowseStations=new[]{new CityPoint(0,0,0),new CityPoint(1,0,0),new CityPoint(2,0,0)},
                Queues=new[]{queue,queue,queue},Exit=one,Timing=timing,OneVisit=true,WalletCents=10000,BrowseSeconds=.1f};
            people[i]=new PedestrianRoutine(i,new Motor(),lanes,plan,service);people[i].Start();
        }
        for(int n=0;n<(int)(60/dt);n++)foreach(var person in people) person.Tick(dt);
        foreach(var p in people) Check(p.State==PedestrianState.Completed,"El servicio termina sin estancamiento");
        Check((bank?service.WithdrawalCount:service.PurchaseCount)==3,"Un solo cobro/retiro por cliente");
        for(int i=0;i<3;i++)Check(lanes[i].Count==0,"Libera las tres cajas al salir");
    }
}
