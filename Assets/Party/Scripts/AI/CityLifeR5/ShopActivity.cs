using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    // Puntos de una caja: su fila, dónde se para el cliente, el escáner, la boleta, la caja registradora y la mano del cajero.
    [Serializable]
    public sealed class CheckoutStation
    {
        public Transform[] queue = Array.Empty<Transform>();
        public Transform counter, scan, receipt, till, cashierGrip, workspace;
        public Transform Till => till != null ? till : scan;
    }

    public sealed class ShopActivity : MonoBehaviour
    {
        [SerializeField] private Transform[] walkRoute=Array.Empty<Transform>(),entryRoute=Array.Empty<Transform>(),browsePoints=Array.Empty<Transform>(),queuePoints=Array.Empty<Transform>(),exitRoute=Array.Empty<Transform>(),productPoints=Array.Empty<Transform>();
        [SerializeField] private int reservedVariant=9;
        [SerializeField] private ShopDoor door;
        [SerializeField] private ShopTaskSettings tasks;
        [SerializeField] private Transform counterPoint,scanPoint,cashierGrip,receiptPoint,tillPoint;
        [SerializeField] private int purchaseCount, withdrawalCount, stock,tillCents;
        [SerializeField] private string lastReceipt;
        [SerializeField] private CityTrafficController traffic;
        [SerializeField, Tooltip("Cajas además de la principal (supermercado, banco): cada una con su fila y su cajero.")]
        private CheckoutStation[] extraCheckouts = Array.Empty<CheckoutStation>();
        [SerializeField] private Transform mainWorkspace;
        private CheckoutLanes lanes;private ShopService service;private CounterExchange[] exchanges;private CheckoutStation main;
        public int ReservedVariant=>reservedVariant;
        public int CheckoutCount=>1+extraCheckouts.Length;
        // Caja 0 = la principal (campos de siempre); las demás, en el orden de extraCheckouts.
        public CheckoutStation Checkout(int lane)
        {
            if(lane>0 && lane<CheckoutCount)return extraCheckouts[lane-1];
            return main??(main=new CheckoutStation{queue=queuePoints,counter=counterPoint,scan=scanPoint,receipt=receiptPoint,till=tillPoint,cashierGrip=cashierGrip,workspace=mainWorkspace});
        }
        // Filas de todas las cajas, con lugar para la fila más corta.
        public CheckoutLanes Lanes
        {
            get
            {
                if(lanes!=null)return lanes;
                int capacity=queuePoints.Length;
                foreach(var extra in extraCheckouts)capacity=Mathf.Min(capacity,extra.queue.Length);
                return lanes=new CheckoutLanes(CheckoutCount,Mathf.Max(1,capacity));
            }
        }
        public ShopService Service
        {
            get
            {
                if(service==null){service=new ShopService(tasks.ShopId,Lanes,browsePoints.Length,tasks.InitialStock,tasks.PriceCents,tasks.IsWithdrawal);service.Changed+=OnTransaction;}
                return service;
            }
        }
        // Mostrador de cada caja, donde cliente y cajero se pasan producto, dinero y vuelto (fuera de rango: la principal).
        public CounterExchange ExchangeFor(int lane)
        {
            if(exchanges==null || exchanges.Length!=CheckoutCount)
            {
                exchanges=new CounterExchange[CheckoutCount];
                var existing=GetComponents<CounterExchange>();
                for(int i=0;i<exchanges.Length;i++)
                {
                    exchanges[i]=i<existing.Length?existing[i]:gameObject.AddComponent<CounterExchange>();
                    exchanges[i].Configure(this,Checkout(i));
                }
            }
            return exchanges[lane>=0 && lane<exchanges.Length?lane:0];
        }
        public CityTrafficController Traffic=>traffic;
        public void ConfigureTraffic(CityTrafficController controller){traffic=controller;}
        public ShopTaskSettings Tasks=>tasks;
        public int StationCount=>productPoints.Length;
        public GameObject ClaimProduct(ShoppingSession session){var display=GetComponent<ShopStockDisplay>();if(display==null){display=gameObject.AddComponent<ShopStockDisplay>();display.Configure(this);}return display.Claim(session);}
        public bool IsConfigured=>tasks!=null && browsePoints.Length>0 && productPoints.Length==browsePoints.Length && counterPoint!=null && scanPoint!=null;
        public Transform[] WalkRoute=>walkRoute;
        // De adentro de la puerta a la acera: también es por donde escapan los civiles asustados.
        public Transform[] ExitRoute=>exitRoute;
        public Transform Scan=>scanPoint;
        public int PurchaseCount=>service?.PurchaseCount??0;
        public event Action<int> PurchaseCompleted;
        public event Action<ShoppingSession,ShopAction> Transaction;
        public void Configure(Transform[] walk,Transform[] entry,Transform[] browse,Transform[] positions,Transform[] exit,Transform[] products,Transform counter,Transform scan,Transform receiptAnchor,Transform till,ShopTaskSettings settings)
        {walkRoute=walk;entryRoute=entry;browsePoints=browse;queuePoints=positions;exitRoute=exit;productPoints=products;counterPoint=counter;scanPoint=scan;receiptPoint=receiptAnchor;tillPoint=till;tasks=settings;}
        public void ConfigureStaff(int variant,ShopDoor entrance,Transform grip){reservedVariant=variant;door=entrance;cashierGrip=grip;main=null;}
        public void ConfigureCheckouts(CheckoutStation[] extra){extraCheckouts=extra??Array.Empty<CheckoutStation>();lanes=null;exchanges=null;}
        public void ConfigureWorkspace(int lane, Transform workspace)
        {
            if(lane == 0) mainWorkspace = workspace;
            Checkout(lane).workspace = workspace;
        }
        // Quien llega a la puerta la empuja; devuelve true si estaba cerrada (el NPC hace el gesto de abrir).
        public bool PushDoor(Vector3 p){if(door==null || !door.InReach(p))return false;bool closed=!door.IsOpen;door.PushFrom(p);return closed;}
        public ShopDoor Entrance => door;
        public Transform DoorHandle=>door!=null?door.Handle:null;
        public Transform ProductPoint(int station)=>productPoints[station];
        public Transform BrowsePoint(int station)=>browsePoints[station];

        // Cada cliente mira algunos puestos ajenos y decide si compra; la semilla hace repetible su visita.
        public PedestrianPlan CreatePlan(PedestrianSettings settings,bool visits,int start,bool oneVisit=false,int? wallet=null,int seed=0)
        {
            var walk = Points(walkRoute,start);
            var exit = Points(exitRoute);
            if (oneVisit)
            {
                Array.Resize(ref walk, 1);
                Array.Resize(ref exit, exit.Length + 1);
                exit[exit.Length - 1] = walk[0];
            }
            var random=new System.Random(seed);
            int looks=Mathf.Min(random.Next(settings.MaxLooks+1),browsePoints.Length-1);
            var chosen=new int[Mathf.Max(0,looks)];
            for(int i=0;i<chosen.Length;i++)chosen[i]=random.Next(browsePoints.Length);
            bool buys=tasks.IsWithdrawal || random.NextDouble()<settings.BuyChance;
            return new PedestrianPlan{Walk=walk,Entry=Points(entryRoute),BrowseStations=Points(browsePoints),Queues=QueuePoints(),Counters=CounterPoints(),Exit=exit,
                BrowseSeconds=settings.BrowseSeconds,TravelTimeout=settings.TravelTimeout,QueueTimeout=settings.QueueTimeout,
                Timing=tasks.Animation != null ? tasks.Animation.Timing : CounterTiming.Standard,
                Looks=chosen,Buys=buys,VisitsShop=visits,OneVisit=oneVisit,WalletCents=wallet??tasks.CustomerWalletCents};
        }
        private void OnTransaction(ShoppingSession session,ShopAction action)
        {
            purchaseCount=service.PurchaseCount;withdrawalCount=service.WithdrawalCount;stock=service.Stock;tillCents=service.TillCents;lastReceipt=session.ReceiptId??lastReceipt;
            if(action==ShopAction.Paid && !tasks.IsWithdrawal)PurchaseCompleted?.Invoke(PurchaseCount);
            Transaction?.Invoke(session,action);
        }
        private CityPoint[][] QueuePoints(){var result=new CityPoint[CheckoutCount][];for(int i=0;i<result.Length;i++)result[i]=Points(Checkout(i).queue);return result;}
        private CityPoint[] CounterPoints(){var result=new CityPoint[CheckoutCount];for(int i=0;i<result.Length;i++){var p=Checkout(i).counter.position;result[i]=new CityPoint(p.x,p.y,p.z);}return result;}
        private static CityPoint[] Points(Transform[] source,int start=0)
        {var result=new CityPoint[source.Length];for(int i=0;i<source.Length;i++){Vector3 p=source[(i+start)%source.Length].position;result[i]=new CityPoint(p.x,p.y,p.z);}return result;}
        private void OnDisable(){service?.Clear();}
    }
}
