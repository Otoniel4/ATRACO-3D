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
        private readonly CheckoutLanes lanes;
        private readonly int stationCount,price;
        private readonly Dictionary<int,ShoppingSession> sessions=new Dictionary<int,ShoppingSession>();
        private int sequence;
        public int Stock { get; private set; }
        public int TillCents { get; private set; }
        public int PurchaseCount { get; private set; }
        public int WithdrawalCount { get; private set; }
        public bool IsWithdrawal { get; }
        public event Action<ShoppingSession,ShopAction> Changed;
        public ShopService(string shopId,CheckoutLanes lanes,int stations,int stock,int priceCents,bool withdrawal=false)
        {
            if(stations<1 || stock<0 || priceCents<1)throw new ArgumentOutOfRangeException(nameof(stations));
            this.shopId=shopId;this.lanes=lanes??throw new ArgumentNullException(nameof(lanes));stationCount=stations;Stock=stock;price=priceCents;
            IsWithdrawal = withdrawal;
            if (withdrawal) TillCents = checked(stock * priceCents);
        }
        public ShoppingSession Find(int id)=>sessions.TryGetValue(id,out var session)?session:null;
        public bool IsStationBusy(int station){foreach(var session in sessions.Values)if(session.Station==station)return true;return false;}
        public bool TryBegin(int id,int walletCents,out ShoppingSession session)
        {
            if(sessions.TryGetValue(id,out session))return true;
            int reserved=0;var stations=new HashSet<int>();
            foreach(var current in sessions.Values) {stations.Add(current.Station);if(current.Stage<ShoppingStage.Paid)reserved++;}
            if(sessions.Count>=stationCount || Stock-reserved<=0 || !CanTransact(walletCents)){session=null;return false;}
            int station=0;while(stations.Contains(station))station++;
            session=new ShoppingSession {Customer=id,Station=station,PriceCents=price,WalletCents=walletCents,Stage=ShoppingStage.Reserved};
            sessions.Add(id,session);Changed?.Invoke(session,ShopAction.Reserved);return true;
        }
        private bool Change(int id,ShoppingStage before,ShoppingStage after,ShopAction action,bool counter=false)
        {
            var s=Find(id);if(s==null || s.Stage!=before || (counter && !lanes.IsFront(id)))return false;
            s.Stage=after;Changed?.Invoke(s,action);return true;
        }
        public bool PickUp(int id)=>Change(id,ShoppingStage.Reserved,ShoppingStage.InHand,ShopAction.PickedUp);
        public bool Place(int id)=>Change(id,ShoppingStage.InHand,ShoppingStage.OnCounter,ShopAction.Placed,true);
        public bool Scan(int id)=>Change(id,ShoppingStage.OnCounter,ShoppingStage.Scanned,ShopAction.Scanned,true);
        public bool Pay(int id)
        {
            var s=Find(id);if(s==null || s.Stage!=ShoppingStage.Scanned || !lanes.IsFront(id) || !CanTransact(s.WalletCents) || Stock<1)return false;
            if (IsWithdrawal) { s.WalletCents += price; TillCents -= price; WithdrawalCount++; }
            else { s.WalletCents -= price; TillCents += price; PurchaseCount++; }
            Stock--;
            s.ReceiptId=shopId+"-"+(++sequence).ToString("D6");s.Stage=ShoppingStage.Paid;
            Changed?.Invoke(s,ShopAction.Paid);Changed?.Invoke(s,ShopAction.Receipt);return true;
        }
        private bool CanTransact(int wallet) => IsWithdrawal ? wallet <= int.MaxValue - price : wallet >= price;
        public bool Collect(int id)=>Change(id,ShoppingStage.Paid,ShoppingStage.Collected,ShopAction.Collected,true);
        public void CancelUncollected(int id)
        {
            var s = Find(id);
            if (s == null || s.Stage == ShoppingStage.Collected || s.Stage == ShoppingStage.Cancelled) return;
            if (s.Stage == ShoppingStage.Paid)
            {
                if (IsWithdrawal) { s.WalletCents -= price; TillCents += price; WithdrawalCount--; }
                else { s.WalletCents += price; TillCents -= price; PurchaseCount--; }
                Stock++;
            }
            s.Stage = ShoppingStage.Cancelled;
            Changed?.Invoke(s, ShopAction.Cancelled);
        }
        public void Release(int id)
        {
            var s=Find(id);if(s==null)return;
            if(s.Stage<ShoppingStage.Paid){s.Stage=ShoppingStage.Cancelled;Changed?.Invoke(s,ShopAction.Cancelled);}
            sessions.Remove(id);
        }
        public void Clear(){foreach(int id in new List<int>(sessions.Keys))Release(id);lanes.Clear();}
    }
}
