using System;
using System.Collections.Generic;

namespace Alarma.AI.CityLife
{
    public enum ShoppingStage { Reserved, InHand, OnCounter, Scanned, Paid, Collected, Cancelled }
    public enum ShopAction { Reserved, PickedUp, Placed, Scanned, Paid, Receipt, Collected, Cancelled }
    public sealed class ShoppingSession
    {
        public int Customer { get; internal set; }
        public int Station { get; internal set; }
        public int PriceCents { get; internal set; }
        public int WalletCents { get; internal set; }
        public string ReceiptId { get; internal set; }
        public ShoppingStage Stage { get; internal set; }
    }

    // Inventario y caja ambiental, separados de la economía de banda. Una sesión produce un solo recibo.
    public sealed class ShopService
    {
        private readonly string shopId;
        private readonly ShopQueue queue;
        private readonly int stationCount,price;
        private readonly Dictionary<int,ShoppingSession> sessions=new Dictionary<int,ShoppingSession>();
        private int sequence;
        public int Stock { get; private set; }
        public int TillCents { get; private set; }
        public int PurchaseCount { get; private set; }
        public event Action<ShoppingSession,ShopAction> Changed;
        public ShopService(string shopId,ShopQueue queue,int stations,int stock,int priceCents)
        {
            if(stations<1 || stock<0 || priceCents<1)throw new ArgumentOutOfRangeException(nameof(stations));
            this.shopId=shopId;this.queue=queue??throw new ArgumentNullException(nameof(queue));stationCount=stations;Stock=stock;price=priceCents;
        }
        public ShoppingSession Find(int id)=>sessions.TryGetValue(id,out var session)?session:null;
        public bool IsStationBusy(int station){foreach(var session in sessions.Values)if(session.Station==station)return true;return false;}
        public bool TryBegin(int id,int walletCents,out ShoppingSession session)
        {
            if(sessions.TryGetValue(id,out session))return true;
            int reserved=0;var stations=new HashSet<int>();
            foreach(var current in sessions.Values) {stations.Add(current.Station);if(current.Stage<ShoppingStage.Paid)reserved++;}
            if(sessions.Count>=stationCount || Stock-reserved<=0 || walletCents<price){session=null;return false;}
            int station=0;while(stations.Contains(station))station++;
            session=new ShoppingSession {Customer=id,Station=station,PriceCents=price,WalletCents=walletCents,Stage=ShoppingStage.Reserved};
            sessions.Add(id,session);Changed?.Invoke(session,ShopAction.Reserved);return true;
        }
        private bool Change(int id,ShoppingStage before,ShoppingStage after,ShopAction action,bool counter=false)
        {
            var s=Find(id);if(s==null || s.Stage!=before || (counter && queue.IndexOf(id)!=0))return false;
            s.Stage=after;Changed?.Invoke(s,action);return true;
        }
        public bool PickUp(int id)=>Change(id,ShoppingStage.Reserved,ShoppingStage.InHand,ShopAction.PickedUp);
        public bool Place(int id)=>Change(id,ShoppingStage.InHand,ShoppingStage.OnCounter,ShopAction.Placed,true);
        public bool Scan(int id)=>Change(id,ShoppingStage.OnCounter,ShoppingStage.Scanned,ShopAction.Scanned,true);
        public bool Pay(int id)
        {
            var s=Find(id);if(s==null || s.Stage!=ShoppingStage.Scanned || queue.IndexOf(id)!=0 || s.WalletCents<price || Stock<1)return false;
            s.WalletCents-=price;Stock--;TillCents+=price;PurchaseCount++;s.ReceiptId=shopId+"-"+(++sequence).ToString("D6");s.Stage=ShoppingStage.Paid;
            Changed?.Invoke(s,ShopAction.Paid);Changed?.Invoke(s,ShopAction.Receipt);return true;
        }
        public bool Collect(int id)=>Change(id,ShoppingStage.Paid,ShoppingStage.Collected,ShopAction.Collected,true);
        public void Release(int id)
        {
            var s=Find(id);if(s==null)return;
            if(s.Stage<ShoppingStage.Paid){s.Stage=ShoppingStage.Cancelled;Changed?.Invoke(s,ShopAction.Cancelled);}
            sessions.Remove(id);
        }
        public void Clear(){foreach(int id in new List<int>(sessions.Keys))Release(id);queue.Clear();}
    }
}
