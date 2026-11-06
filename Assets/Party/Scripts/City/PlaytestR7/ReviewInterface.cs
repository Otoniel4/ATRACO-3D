using UnityEngine;
using Alarma.Core.Contracts;
using Alarma.UI.Hud;
using Alarma.UI.Map;
using Alarma.UI.Pause;
namespace Alarma.City.Playtest
{
    // Interfaz de la prueba: menú de pausa (Esc), mapa (M), inventario (Tab), minimapa, barra rápida, aviso de carga y la indicación para abrir puertas.
    public sealed class ReviewInterface:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private ReviewPlayerMotor player;
        [SerializeField] private MonoBehaviour worldSource; // implementa IPlayableWorld
        private IPlayableWorld world;
        [SerializeField] private ReviewDoorInteraction doors;
        [SerializeField] private CityMapScreen map;
        [SerializeField] private CityMinimap minimap;
        [SerializeField] private PauseMenuScreen pause;
        [SerializeField] private InventoryScreen inventory;
        [SerializeField] private HotbarView hotbar;
        private GUIStyle hint;
        public void Configure(ReviewInput controls,ReviewPlayerMotor motor,IPlayableWorld playable,ReviewDoorInteraction access,CityMapScreen screen,CityMinimap corner,PauseMenuScreen menu,InventoryScreen backpack,HotbarView quick)
        {input=controls;player=motor;world=playable;worldSource=playable as MonoBehaviour;doors=access;map=screen;minimap=corner;pause=menu;inventory=backpack;hotbar=quick;}
        private void OnEnable(){world??=worldSource as IPlayableWorld;if(map==null || pause==null || inventory==null)return;map.PlaceSelected+=Travel;map.Toggled+=OnMenuToggled;pause.Toggled+=OnMenuToggled;inventory.Toggled+=OnMenuToggled;pause.QuitRequested+=Quit;}
        private void OnDisable(){if(map==null || pause==null || inventory==null)return;map.PlaceSelected-=Travel;map.Toggled-=OnMenuToggled;pause.Toggled-=OnMenuToggled;inventory.Toggled-=OnMenuToggled;pause.QuitRequested-=Quit;}
        private void Update()
        {
            if(input==null)return;
            // Esc cierra primero el mapa o el inventario; si no hay nada abierto, abre o cierra el menú de pausa.
            if(input.PausePressed){if(map.IsOpen)map.Close();else if(inventory.IsOpen)inventory.Close();else pause.Toggle();}
            else if(input.MapPressed && !pause.IsOpen && !inventory.IsOpen)map.Toggle();
            else if(input.InventoryPressed && !pause.IsOpen && !map.IsOpen)inventory.Toggle();
        }
        private void OnMenuToggled(bool _){bool open=map.IsOpen || pause.IsOpen || inventory.IsOpen;input.SetMenu(open);minimap.SetVisible(!open);hotbar.SetVisible(!open);}
        private static void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying=false;
#else
            Application.Quit();
#endif
        }
        private void Travel(MapPlace place){player.Teleport(place.Position);map.Close();}
        private void OnGUI()
        {
            if(world==null || map.IsOpen || pause.IsOpen || inventory.IsOpen)return;
            hint??=new GUIStyle(GUI.skin.box){fontSize=20,alignment=TextAnchor.MiddleCenter};
            if(!world.ReadyAt(player.transform.position))
                GUI.Box(new Rect(Screen.width*.5f-210,Screen.height*.5f-35,420,70),world.LoadFailed?"No se pudo cargar una parte. Revisa Console.":"Preparando la zona...\nLa primera carga puede tardar.",hint);
            else if(doors!=null && doors.PromptVisible)
                GUI.Box(new Rect(Screen.width*.5f-120,Screen.height-250,240,44),"E  ·  Abrir puerta",hint); // encima de la barra rápida
        }
    }
}
