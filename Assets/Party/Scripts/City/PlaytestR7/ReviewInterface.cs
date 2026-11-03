using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest
{
    public sealed class ReviewInterface:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewPlayerMotor player;
        [SerializeField] private ReviewCamera cameraRig;
        [SerializeField] private ReviewCharacterView character;
        [SerializeField] private WorldReviewStream world;
        [SerializeField] private ReviewCatalog catalog;
        [SerializeField] private ReviewModelPreview preview;
        [SerializeField] private CityPopulationDirector population;
        [SerializeField] private StreetPopulationDirector streetPopulation;
        public void ConfigureStreet(StreetPopulationDirector value){streetPopulation=value;}
        [SerializeField] private ShopActivity[] shops=Array.Empty<ShopActivity>();
        private readonly List<ReviewModel> filtered=new List<ReviewModel>();
        private int panel,category,selection=-1;private Vector2 scroll;private float averageDelta=.016f;
        public void Configure(ReviewInput controls,ReviewPlayerMotor motor,ReviewCamera view,ReviewCharacterView actor,WorldReviewStream stream,ReviewCatalog models,ReviewModelPreview display,CityPopulationDirector citizens,ShopActivity[] businesses)
        {input=controls;player=motor;cameraRig=view;character=actor;world=stream;catalog=models;preview=display;population=citizens;shops=businesses;}
        private void Update()
        {
            averageDelta=Mathf.Lerp(averageDelta,Mathf.Max(.001f,Time.unscaledDeltaTime),.05f);
            if(input==null)return;if(input.MapPressed)Open(panel==1?0:1);if(input.CatalogPressed)Open(panel==2?0:2);
        }
        private void Open(int value){panel=value;input.SetMenu(value!=0);if(value!=2)preview.Hide();else Filter();}
        private void Filter()
        {
            filtered.Clear();foreach(var item in catalog.Models)if((int)item.Category==category)filtered.Add(item);
            selection=filtered.Count>0?0:-1;if(selection>=0)preview.Show(filtered[selection].Prefab);
        }
        private void OnGUI()
        {
            if(world==null || input==null)return;
            GUI.Box(new Rect(12,12,Mathf.Min(Screen.width-24,780),92),GUIContent.none);
            GUI.Label(new Rect(24,20,740,23),"ALARMA · PRUEBA LOCAL     "+Mathf.RoundToInt(1/averageDelta)+" FPS     NPC: "+((population!=null?population.ActiveCount:0)+(streetPopulation!=null?streetPopulation.ActiveCount:0))+"     Partes de ciudad: "+world.LoadedCount);
            GUI.Label(new Rect(24,45,740,22),"WASD: caminar · Shift: correr · Ratón: cámara · V: vuelo · M: mapa · F6: modelos");
            GUI.Label(new Rect(24,69,740,22),"F1–F4: personaje · Esc: liberar ratón · Clic derecho: capturar ratón · Puertas automáticas");
            if(input.CursorFree && panel==0)
            {if(GUI.Button(new Rect(12,112,160,32),"Ver mapa (M)"))Open(1);if(GUI.Button(new Rect(182,112,170,32),"Revisar modelos (F6)"))Open(2);}
            if(!cameraRig.Flying && !world.ReadyAt(player.transform.position))GUI.Box(new Rect(Screen.width*.5f-210,Screen.height*.5f-35,420,70),world.FailedCount>0?"No se pudo cargar una parte. Revisa Console.":"Preparando la zona...\nLa primera carga puede tardar.");
            float y=Screen.height-98;
            foreach(var shop in shops)if(shop!=null && Vector3.Distance(shop.transform.position,player.transform.position)<28)
            {GUI.Box(new Rect(12,y,440,34),shop.name.Replace("Routine_","")+" · Compras: "+shop.PurchaseCount+" · Stock: "+shop.Service.Stock+" · Caja: "+(shop.Service.TillCents/100f).ToString("0.00"));y-=38;}
            if(panel==0)return;
            Rect frame=new Rect(Mathf.Max(12,(Screen.width-1000)*.5f),116,Mathf.Min(1000,Screen.width-24),Mathf.Max(150,Screen.height-136));GUI.Box(frame,GUIContent.none);
            GUILayout.BeginArea(new Rect(frame.x+16,frame.y+12,frame.width-32,frame.height-24));
            GUILayout.BeginHorizontal();GUILayout.Label(panel==1?"MAPA · 3 × 3 km":"CATÁLOGO DE MODELOS",GUILayout.Height(28));if(GUILayout.Button("Cerrar",GUILayout.Width(100)))Open(0);GUILayout.EndHorizontal();
            if(panel==1)DrawMap(frame.width-32,frame.height-70);else DrawCatalog(frame.width-32,frame.height-70,new Vector2(frame.x+16,frame.y+12));
            GUILayout.EndArea();
        }
        private void DrawMap(float width,float height)
        {
            GUILayout.Label("Tu posición y los lugares de la ciudad · Norte arriba");
            GUILayout.BeginHorizontal(GUILayout.Height(Mathf.Max(80,height-60)));
            GUILayout.BeginVertical(GUILayout.Width(Mathf.Min(230,width*.3f)));scroll=GUILayout.BeginScrollView(scroll);
            foreach(var point in world.Data.Destinations)
                GUILayout.Label(point.Label+" · "+Mathf.RoundToInt(Vector3.Distance(point.Position,player.transform.position))+" m",GUILayout.Height(30));
            GUILayout.EndScrollView();GUILayout.EndVertical();
            Rect available=GUILayoutUtility.GetRect(width*.65f,Mathf.Max(80,height-75));float side=Mathf.Min(available.width,available.height);
            Rect map=new Rect(available.center.x-side*.5f,available.center.y-side*.5f,side,side);
            if(world.Data.MapTexture!=null)GUI.DrawTexture(map,world.Data.MapTexture,ScaleMode.StretchToFill,false);else GUI.Box(map,GUIContent.none);
            foreach(var point in world.Data.Destinations)
            {
                Vector2 p=ReviewMapProjection.Normalized(point.Position);
                GUI.Label(new Rect(map.x+p.x*side-5,map.y+p.y*side-8,18,22),new GUIContent("▪",point.Label));
            }
            Vector2 position=ReviewMapProjection.Normalized(player.transform.position);Vector2 marker=new Vector2(map.x+position.x*side,map.y+position.y*side);
            Matrix4x4 previous=GUI.matrix;Color color=GUI.color;GUIUtility.RotateAroundPivot(player.transform.eulerAngles.y,marker);GUI.color=Color.yellow;
            GUI.Label(new Rect(marker.x-8,marker.y-11,30,28),"▲");GUI.matrix=previous;GUI.color=color;
            GUILayout.EndHorizontal();GUILayout.Label("▲ Tú · M para cerrar");
        }
        private void DrawCatalog(float width,float height,Vector2 areaOrigin)
        {
            int next=GUILayout.Toolbar(category,new[]{"Personajes","Vehículos","Armas y herramientas","Accesorios"},GUILayout.Height(30));if(next!=category){category=next;Filter();}
            GUILayout.BeginHorizontal(GUILayout.Height(Mathf.Max(80,height-65)));GUILayout.BeginVertical(GUILayout.Width(Mathf.Min(270,width*.4f)));scroll=GUILayout.BeginScrollView(scroll);
            for(int i=0;i<filtered.Count;i++)if(GUILayout.Button(filtered[i].Label,GUILayout.Height(30))){selection=i;preview.Show(filtered[i].Prefab);}
            GUILayout.EndScrollView();GUILayout.EndVertical();
            Rect display=GUILayoutUtility.GetRect(width*.55f,Mathf.Max(80,height-90));if(preview.Texture!=null)GUI.DrawTexture(display,preview.Texture,ScaleMode.ScaleToFit,false);
            var mouse=Mouse.current;if(mouse!=null && Event.current.type==EventType.Repaint && mouse.leftButton.isPressed && display.Contains(new Vector2(mouse.position.ReadValue().x-areaOrigin.x,Screen.height-mouse.position.ReadValue().y-areaOrigin.y)))preview.Rotate(-mouse.delta.ReadValue().x*.4f);
            GUILayout.EndHorizontal();GUILayout.Label("Arrastra sobre el modelo para girarlo. Aquí revisas su diseño; el catálogo no activa disparos ni conducción.");
            if(category==0){GUILayout.BeginHorizontal();for(int i=0;i<4;i++){int role=i;if(GUILayout.Button(new[]{"Usar Ladrón","Usar Hacker","Usar Distractor","Usar Músculo"}[i]))character.SelectRole(role);}GUILayout.EndHorizontal();}
        }
    }
}
