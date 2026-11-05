using System;
using System.Collections.Generic;
using Alarma.AI.CityLife;
using Alarma.AI.Street;
using UnityEngine;

namespace Alarma.AI.CityLife
{
    public class PedestrianSettings { }
    public class ShopTaskSettings { public bool IsWithdrawal; public int PriceCents = 700, CustomerWalletCents = 1500; }
    public class ShopActivity : MonoBehaviour
    {
        public bool IsConfigured = true;
        public ShopService Service = new ShopService("test", new ShopQueue(1), 1, 3, 700);
        public ShopTaskSettings Tasks = new ShopTaskSettings();
        public object Traffic;
    }
    public class PedestrianActor
    {
        public bool Failed;
        public PedestrianState CurrentState;
        public int WalletCents = 1200;
        public int Begins;
        public bool Begin(int id, Vector3 position, ShopActivity shop, PedestrianSettings settings, bool shopper, int marker,
            object traffic, bool oneVisit, int? wallet)
        {
            Begins++;
            CurrentState = PedestrianState.Entering;
            return oneVisit;
        }
        public void TryLeaveVisit() { }
        public void Suspend() => CurrentState = PedestrianState.Inactive;
    }
}

internal static class VisitTests
{
    private sealed class Motor : IPedestrianMotor
    {
        public bool HasArrived { get; set; } = true;
        public bool MoveTo(CityPoint destination) => true;
        public void Stop() { }
    }

    public static void Run(Action<bool,string> check, Action<SidewalkWalker[]> tick)
    {
        var nodes = new Vector2[10];
        var edges = new List<(int,int,int,int)>();
        for (int i = 0; i < nodes.Length; i++)
        {
            nodes[i] = new Vector2(i * 2, 0);
            if (i > 0) edges.Add((i - 1, i, i == 3 ? SidewalkGraph.FreeCrossing : SidewalkGraph.Sidewalk, -1));
        }
        var graph = new SidewalkGraph();
        graph.Build(nodes, edges, 4);
        check(graph.CanSpawn(1) && !graph.CanSpawn(2) && !graph.CanSpawn(3), "aparición fuera de la boca del cruce");
        var sameSide = new SidewalkVisit(new ShopActivity(), 1, 0, new Vector3(2,.175f,1.7f));
        var across = new SidewalkVisit(new ShopActivity(), 3, 0, new Vector3(6,.175f,1.7f));
        var planner = new SidewalkVisitPlanner();
        var path = new List<int>();
        check(planner.Find(graph, 0, new[]{across,sameSide}, 1000, path) == sameSide && path.Count == 1 && path[0] == 1,
            "elige local alcanzable por la acera del mismo lado");
        check(planner.Find(graph, 0, new[]{across}, 1000, path) == null, "no cruza la calzada para atajar a un comercio");
        check(planner.Find(graph, 0, new[]{sameSide}, 100, path) == null, "omite una compra fuera del presupuesto");
        var walker = new SidewalkWalker { Component = new PedestrianActor() };
        var shopper = (PedestrianActor)walker.Component;
        walker.Configure(new Animator());
        var walkable = new SidewalkGraph();
        edges[2] = (2, 3, SidewalkGraph.Sidewalk, -1);
        walkable.Build(nodes, edges, 4);
        walker.Begin(walkable, null, 0, 8, planner, new[]{sameSide}, new PedestrianSettings(), 11);
        for (int i = 0; i < 150 && shopper.Begins == 0; i++) tick(new[]{walker});
        check(shopper.Begins == 1 && (walker.transform.position - sameSide.Approach).sqrMagnitude < .0001f,
            "el peatón llega andando y activa la visita en el mismo cuerpo");
        check(planner.Find(graph, 0, new[]{sameSide}, 1000, path) == null, "un local ocupado no acumula otra visita");
        shopper.CurrentState = PedestrianState.Completed;
        for (int i = 0; i < 19; i++) tick(new[]{walker});
        check(shopper.Begins == 1 && shopper.CurrentState == PedestrianState.Inactive && Math.Abs(walker.transform.position.z) <= .28f,
            "el mismo actor vuelve a la acera después de la visita");
        walker.End();
        CheckTransaction(false, check);
        CheckTransaction(true, check);
    }

    private static void CheckTransaction(bool withdrawal, Action<bool,string> check)
    {
        var queue = new ShopQueue(1);
        var service = new ShopService(withdrawal ? "Banco" : "Tienda", queue, 1, 2, 700, withdrawal);
        CityPoint[] route = {new CityPoint(0,0,0)};
        var plan = new PedestrianPlan
        {
            Walk = route, Entry = route, BrowseStations = route, Queue = route, Exit = route,
            OneVisit = true, WalletCents = 2000
        };
        var visitor = new PedestrianRoutine(8, new Motor(), queue, plan, service);
        bool browsed = false;
        visitor.StateChanged += state => browsed |= state == PedestrianState.Browsing;
        visitor.Start();
        for (int i = 0; i < 160; i++) visitor.Tick(.1f);
        int expectedWallet = withdrawal ? 2700 : 1300;
        check(visitor.State == PedestrianState.Completed && visitor.WalletCents == expectedWallet
            && service.Stock == 1 && service.TillCents == 700 && browsed != withdrawal
            && (withdrawal ? service.WithdrawalCount == 1 && service.PurchaseCount == 0 : service.PurchaseCount == 1 && service.WithdrawalCount == 0),
            withdrawal ? "retira efectivo del banco y completa la visita una vez" : "elige, paga y completa la compra una vez");
        check(queue.IndexOf(8) < 0 && service.Find(8) == null, "libera caja y sesión al salir " + (withdrawal ? "del banco" : "de tienda"));
    }
}
