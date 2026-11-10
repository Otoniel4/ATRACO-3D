using System;
using System.Collections.Generic;
using Alarma.AI.CityLife;

// Revisión 28: guion del mostrador y clientes que miran, eligen o se van sin comprar.
internal static class CounterTests
{
    private sealed class Motor : IPedestrianMotor
    {
        public bool HasArrived { get; set; } = true;
        public bool MoveTo(CityPoint destination) => true;
        public void Stop() { }
    }

    public static void Run(Action<bool, string> check)
    {
        var timing = CounterTiming.Standard;
        check(CounterChoreography.Blend(-.2f) == 0f && CounterChoreography.Blend(1.2f) == 1f
            && CounterChoreography.Blend(.01f) < .001f && CounterChoreography.Blend(.99f) > .999f,
            "el traspaso conserva sus extremos y acelera y frena suavemente");
        var scanTiming = new CounterTiming { Scan = 4f };
        check(CounterChoreography.Evaluate(PedestrianState.Scanning, 1f, scanTiming, false).Product == ItemPlace.Drop
            && CounterChoreography.Evaluate(PedestrianState.Scanning, 2.4f, scanTiming, false).Product == ItemPlace.CashierHand
            && CounterChoreography.Evaluate(PedestrianState.Scanning, 3.8f, scanTiming, false).Product == ItemPlace.Bag,
            "el producto pasa por el lector antes de llegar a la zona de entrega aunque cambie la duración");
        // Compra: el producto pasa por la mano del cliente, el mostrador, la mano del cajero y queda listo para llevar.
        var places = new List<ItemPlace>();
        foreach (var (state, length) in new[] { (PedestrianState.PickingUp, timing.Pick), (PedestrianState.Placing, timing.Place),
                     (PedestrianState.Scanning, timing.Scan), (PedestrianState.Collecting, timing.Bag) })
            for (float t = 0; t < length; t += .05f)
            {
                var place = CounterChoreography.Evaluate(state, t, timing, false).Product;
                if (places.Count == 0 || places[places.Count - 1] != place) places.Add(place);
            }
        check(string.Join(">", places) == "Shelf>CustomerHand>Drop>CashierHand>Bag>CustomerHand",
            "el producto va del estante a la mano, al mostrador, al cajero y de vuelta al cliente");

        // Pago: el dinero sale del bolsillo, pasa de mano a mano y el vuelto vuelve al cliente.
        var money = new List<ItemPlace>(); var change = new List<ItemPlace>();
        foreach (var (state, length) in new[] { (PedestrianState.Paying, timing.Pay), (PedestrianState.ReceivingReceipt, timing.Change) })
            for (float t = 0; t < length; t += .05f)
            {
                var frame = CounterChoreography.Evaluate(state, t, timing, false);
                if (money.Count == 0 || money[money.Count - 1] != frame.Money) money.Add(frame.Money);
                if (change.Count == 0 || change[change.Count - 1] != frame.Change) change.Add(frame.Change);
            }
        check(string.Join(">", money) == "Hidden>CustomerHand>CashierHand>Hidden", "el cliente entrega el dinero en la mano del cajero");
        check(string.Join(">", change) == "Hidden>CashierHand>CustomerHand>Hidden", "el cajero devuelve el vuelto en la mano y el cliente lo guarda");
        var handover = CounterChoreography.Evaluate(PedestrianState.Paying, 1.25f, timing, false);
        check(handover.Customer == HandGoal.Handoff && handover.Cashier == HandGoal.Handoff, "al pasar el dinero las dos manos se juntan sobre el mostrador");
        check(!CounterChoreography.Evaluate(PedestrianState.Queueing, 0, timing, false).CashierBusy
              && CounterChoreography.Evaluate(PedestrianState.Scanning, .3f, timing, false).CashierBusy,
            "el cajero solo trabaja con el cliente que está en el mostrador");

        // Banco: el número de turno y el efectivo pasan por la bandeja de la ventanilla.
        var ticket = new List<ItemPlace>(); var cash = new List<ItemPlace>();
        foreach (var (state, length) in new[] { (PedestrianState.PickingUp, timing.Pick), (PedestrianState.Placing, timing.Place),
                     (PedestrianState.Scanning, timing.Scan), (PedestrianState.Paying, timing.Pay) })
            for (float t = 0; t < length; t += .05f)
            {
                var frame = CounterChoreography.Evaluate(state, t, timing, true);
                if (ticket.Count == 0 || ticket[ticket.Count - 1] != frame.Ticket) ticket.Add(frame.Ticket);
                if (cash.Count == 0 || cash[cash.Count - 1] != frame.Money) cash.Add(frame.Money);
            }
        check(string.Join(">", ticket) == "Hidden>CustomerHand>Drop>CashierHand>Hidden", "en el banco el número se entrega por la bandeja");
        check(string.Join(">", cash) == "Hidden>CashierHand>Handoff>CustomerHand>Hidden", "el cajero deja el efectivo en la bandeja y el cliente lo guarda");

        // Rutina: mira otros puestos antes del suyo y respeta los tiempos del mostrador.
        var line = new ShopQueue(1);
        var service = new ShopService("Tienda", line, 3, 5, 700);
        CityPoint[] one = { new CityPoint(0, 0, 0) };
        var stations = new[] { new CityPoint(0, 0, 0), new CityPoint(1, 0, 0), new CityPoint(2, 0, 0) };
        var plan = new PedestrianPlan { Walk = one, Entry = one, BrowseStations = stations, Queue = one, Exit = one, Looks = new[] { 2, 1 }, OneVisit = true, WalletCents = 2000 };
        var visitor = new PedestrianRoutine(5, new Motor(), line, plan, service);
        var seen = new List<int>();
        float paying = 0;
        visitor.Start();
        for (int i = 0; i < 400 && visitor.State != PedestrianState.Completed; i++)
        {
            visitor.Tick(.1f);
            if (visitor.State == PedestrianState.Browsing && (seen.Count == 0 || seen[seen.Count - 1] != visitor.BrowsingStation)) seen.Add(visitor.BrowsingStation);
            if (visitor.State == PedestrianState.Paying) paying = Math.Max(paying, visitor.StateSeconds);
        }
        check(seen.Count == 3 && seen[0] == 2 && seen[1] == 1,
            "mira dos puestos ajenos antes del suyo");
        check(visitor.State == PedestrianState.Completed && service.PurchaseCount == 1 && paying >= timing.Pay - .15f,
            "el pago dura lo que el guion necesita para pasar dinero y vuelto");

        // Quien ya estaba dentro al llegar el jugador empieza en su puesto y completa la compra.
        var insideLine = new ShopQueue(1);
        var insideShop = new ShopService("Tienda", insideLine, 3, 5, 700);
        var shopper = new PedestrianRoutine(7, new Motor(), insideLine,
            new PedestrianPlan { Walk = one, Entry = one, BrowseStations = stations, Queue = one, Exit = one, Looks = new[] { 1 }, OneVisit = true, WalletCents = 2000 }, insideShop);
        int station = shopper.BeginInside();
        bool startsBrowsing = shopper.State == PedestrianState.Browsing && shopper.BrowsingStation == station;
        shopper.ResumeInside();
        for (int i = 0; i < 300 && shopper.State != PedestrianState.Completed; i++) shopper.Tick(.1f);
        check(station == 0 && startsBrowsing && shopper.State == PedestrianState.Completed && insideShop.PurchaseCount == 1,
            "el cliente que ya estaba dentro empieza en su puesto y completa la compra");
        var full = new ShopService("Lleno", new ShopQueue(1), 1, 5, 700);
        full.TryBegin(99, 2000, out _);
        var late = new PedestrianRoutine(8, new Motor(), new ShopQueue(1),
            new PedestrianPlan { Walk = one, Entry = one, BrowseStations = stations, Queue = one, Exit = one, OneVisit = true, WalletCents = 2000 }, full);
        check(late.BeginInside() < 0 && late.Session == null, "no se crea un cliente dentro si el local está lleno");

        // Algunos se van sin comprar: miran, dejan el producto y salen.
        var browseLine = new ShopQueue(1);
        var browsing = new ShopService("Tienda", browseLine, 3, 5, 700);
        var window = new PedestrianRoutine(6, new Motor(), browseLine,
            new PedestrianPlan { Walk = one, Entry = one, BrowseStations = stations, Queue = one, Exit = one, Buys = false, OneVisit = true, WalletCents = 2000 }, browsing);
        bool picked = false;
        window.Start();
        for (int i = 0; i < 200 && window.State != PedestrianState.Completed; i++)
        {
            window.Tick(.1f);
            picked |= window.State == PedestrianState.PickingUp;
        }
        check(window.State == PedestrianState.Completed && !picked && browsing.PurchaseCount == 0 && browsing.Stock == 5 && browsing.Find(6) == null,
            "el cliente que solo mira se va sin comprar y libera su lugar");
    }
}
