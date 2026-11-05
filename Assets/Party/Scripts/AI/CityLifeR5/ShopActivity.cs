using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
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
        private ShopQueue queue;private ShopService service;private CounterExchange exchange;
        public int ReservedVariant=>reservedVariant;
        public ShopQueue Queue=>queue??(queue=new ShopQueue(Mathf.Max(1,queuePoints.Length)));
        public ShopService Service
        {
            get
            {
                if(service==null){service=new ShopService(tasks.ShopId,Queue,browsePoints.Length,tasks.InitialStock,tasks.PriceCents,tasks.IsWithdrawal);service.Changed+=OnTransaction;}
                return service;
            }
        }
        // Mostrador donde cliente y cajero se pasan producto, dinero y vuelto.
        public CounterExchange Exchange
        {
            get
            {
                if(exchange==null){exchange=GetComponent<CounterExchange>();if(exchange==null)exchange=gameObject.AddComponent<CounterExchange>();exchange.Configure(this);}
                return exchange;
            }
        }
        public CityTrafficController Traffic=>traffic;
        public void ConfigureTraffic(CityTrafficController controller){traffic=controller;}
        public ShopTaskSettings Tasks=>tasks;
        public int StationCount=>productPoints.Length;
        public GameObject ClaimProduct(ShoppingSession session){var display=GetComponent<ShopStockDisplay>();if(display==null){display=gameObject.AddComponent<ShopStockDisplay>();display.Configure(this);}return display.Claim(session);}
        public bool IsConfigured=>tasks!=null && browsePoints.Length>0 && productPoints.Length==browsePoints.Length && counterPoint!=null && scanPoint!=null;
        public Transform[] WalkRoute=>walkRoute;
        public Transform Counter=>counterPoint;
        public Transform Scan=>scanPoint;
        public Transform Till=>tillPoint!=null?tillPoint:scanPoint;
        public Transform CashierGrip=>cashierGrip;
        public int PurchaseCount=>service?.PurchaseCount??0;
        public event Action<int> PurchaseCompleted;
        public event Action<ShoppingSession,ShopAction> Transaction;
        public void Configure(Transform[] walk,Transform[] entry,Transform[] browse,Transform[] positions,Transform[] exit,Transform[] products,Transform counter,Transform scan,Transform receiptAnchor,Transform till,ShopTaskSettings settings)
        {walkRoute=walk;entryRoute=entry;browsePoints=browse;queuePoints=positions;exitRoute=exit;productPoints=products;counterPoint=counter;scanPoint=scan;receiptPoint=receiptAnchor;tillPoint=till;tasks=settings;}
        public void ConfigureStaff(int variant,ShopDoor entrance,Transform grip){reservedVariant=variant;door=entrance;cashierGrip=grip;}
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
            return new PedestrianPlan{Walk=walk,Entry=Points(entryRoute),BrowseStations=Points(browsePoints),Queue=Points(queuePoints),Exit=exit,
                BrowseSeconds=settings.BrowseSeconds,TravelTimeout=settings.TravelTimeout,QueueTimeout=settings.QueueTimeout,
                Looks=chosen,Buys=buys,VisitsShop=visits,OneVisit=oneVisit,WalletCents=wallet??tasks.CustomerWalletCents};
        }
        private void OnTransaction(ShoppingSession session,ShopAction action)
        {
            purchaseCount=service.PurchaseCount;withdrawalCount=service.WithdrawalCount;stock=service.Stock;tillCents=service.TillCents;lastReceipt=session.ReceiptId??lastReceipt;
            if(action==ShopAction.Paid && !tasks.IsWithdrawal)PurchaseCompleted?.Invoke(PurchaseCount);
            Transaction?.Invoke(session,action);
        }
        private static CityPoint[] Points(Transform[] source,int start=0)
        {var result=new CityPoint[source.Length];for(int i=0;i<source.Length;i++){Vector3 p=source[(i+start)%source.Length].position;result[i]=new CityPoint(p.x,p.y,p.z);}return result;}
        private void OnDisable(){service?.Clear();}
    }
}
