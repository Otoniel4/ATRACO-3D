using System;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    public sealed class ShopActivity : MonoBehaviour
    {
        [SerializeField] private Transform[] walkRoute=Array.Empty<Transform>(),entryRoute=Array.Empty<Transform>(),browsePoints=Array.Empty<Transform>(),queuePoints=Array.Empty<Transform>(),exitRoute=Array.Empty<Transform>(),productPoints=Array.Empty<Transform>();
        [SerializeField] private int reservedVariant=9;
        [SerializeField] private AutomaticShopDoor door;
        [SerializeField] private ShopTaskSettings tasks;
        [SerializeField] private Transform counterPoint,scanPoint,cashierGrip,receiptPoint,tillPoint;
        private ShopQueue queue;private ShopService service;private GameObject money,receipt;private float moneyUntil,receiptUntil;
        [SerializeField] private int purchaseCount,stock,tillCents;
        [SerializeField] private string lastReceipt;
        public int ReservedVariant=>reservedVariant;
        public ShopQueue Queue=>queue??(queue=new ShopQueue(Mathf.Max(1,queuePoints.Length)));
        public ShopService Service
        {
            get
            {
                if(service==null){service=new ShopService(tasks.ShopId,Queue,browsePoints.Length,tasks.InitialStock,tasks.PriceCents);service.Changed+=OnTransaction;}
                return service;
            }
        }
        public ShopTaskSettings Tasks=>tasks;
        public bool IsConfigured=>tasks!=null && browsePoints.Length>0 && productPoints.Length==browsePoints.Length && counterPoint!=null && scanPoint!=null;
        public Transform[] WalkRoute=>walkRoute;
        public Transform Counter=>counterPoint;
        public Transform Scan=>scanPoint;
        public Transform CashierGrip=>cashierGrip;
        public int PurchaseCount=>service?.PurchaseCount??0;
        public event Action<int> PurchaseCompleted;
        public event Action<ShoppingSession,ShopAction> Transaction;
        public void Configure(Transform[] walk,Transform[] entry,Transform[] browse,Transform[] positions,Transform[] exit,Transform[] products,Transform counter,Transform scan,Transform receiptAnchor,Transform till,ShopTaskSettings settings)
        {walkRoute=walk;entryRoute=entry;browsePoints=browse;queuePoints=positions;exitRoute=exit;productPoints=products;counterPoint=counter;scanPoint=scan;receiptPoint=receiptAnchor;tillPoint=till;tasks=settings;}
        public void ConfigureStaff(int variant,AutomaticShopDoor entrance,Transform grip){reservedVariant=variant;door=entrance;cashierGrip=grip;}
        public void RequestPassage(Vector3 p){if(door!=null)door.RequestNear(p);}
        public Transform ProductPoint(int station)=>productPoints[station];
        public Transform BrowsePoint(int station)=>browsePoints[station];
        public PedestrianPlan CreatePlan(PedestrianSettings settings,bool visits,int start)
        {
            return new PedestrianPlan{Walk=Points(walkRoute,start),Entry=Points(entryRoute),BrowseStations=Points(browsePoints),Queue=Points(queuePoints),Exit=Points(exitRoute),BrowseSeconds=settings.BrowseSeconds,PaySeconds=settings.PaySeconds,TravelTimeout=settings.TravelTimeout,QueueTimeout=settings.QueueTimeout,VisitsShop=visits,WalletCents=tasks.CustomerWalletCents};
        }
        private void OnTransaction(ShoppingSession session,ShopAction action)
        {
            purchaseCount=service.PurchaseCount;stock=service.Stock;tillCents=service.TillCents;lastReceipt=session.ReceiptId??lastReceipt;
            if(action==ShopAction.Paid)
            {
                if(money==null && tasks.MoneyPrefab!=null)money=Instantiate(tasks.MoneyPrefab);
                if(money!=null){money.transform.SetParent(cashierGrip,false);money.SetActive(true);moneyUntil=Time.time+.75f;}
                PurchaseCompleted?.Invoke(PurchaseCount);
            }
            if(action==ShopAction.Receipt)
            {
                if(receipt==null && tasks.ReceiptPrefab!=null)receipt=Instantiate(tasks.ReceiptPrefab,receiptPoint);
                if(receipt!=null){receipt.SetActive(true);receiptUntil=Time.time+1.6f;}
            }
            Transaction?.Invoke(session,action);
        }
        private void Update()
        {
            if(money!=null && money.activeSelf && Time.time>moneyUntil){money.transform.SetParent(tillPoint,false);money.SetActive(false);}
            if(receipt!=null && receipt.activeSelf && Time.time>receiptUntil)receipt.SetActive(false);
        }
        private static CityPoint[] Points(Transform[] source,int start=0)
        {var result=new CityPoint[source.Length];for(int i=0;i<source.Length;i++){Vector3 p=source[(i+start)%source.Length].position;result[i]=new CityPoint(p.x,p.y,p.z);}return result;}
        private void OnDisable(){service?.Clear();if(money!=null)Destroy(money);if(receipt!=null)Destroy(receipt);}
    }
}
