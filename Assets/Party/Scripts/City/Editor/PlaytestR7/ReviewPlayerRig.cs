using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Alarma.Animation;
using Alarma.Core.Contracts;
using Alarma.Core.Editor;
using Alarma.Core.Settings;
using Alarma.Player.Editor;
using Alarma.Player.Health;
using Alarma.Player.Items;
using Alarma.UI.Hud;
using Alarma.UI.Map;
using Alarma.UI.Pause;
namespace Alarma.City.Playtest.Editor
{
    // Arma el jugador de prueba sobre cualquier ciudad que cumpla IPlayableWorld: controles, cuerpo, cámara, roles, inventario, mapa, menú e interfaz.
    public static class ReviewPlayerRig
    {
        public sealed class Parts{public ReviewInput Input;public ReviewPlayerMotor Player;public ReviewCamera Camera;public ReviewCharacterView Character;public PlayerInventory Inventory;public ItemUser Items;public PlayerHealth Health;}
        public static Parts Create(IPlayableWorld world,Vector3 spawn,GameObject[] roles,float farClip,GameSettings settings)
        {
            var input=new GameObject("Controles de la prueba").AddComponent<ReviewInput>();
            var playerObject=new GameObject("Jugador de revisión");playerObject.layer=30;
            var controller=playerObject.AddComponent<CharacterController>();controller.height=1.75f;controller.center=new Vector3(0,.875f,0);controller.radius=.24f;controller.skinWidth=.025f;controller.stepOffset=.28f;controller.slopeLimit=50;controller.minMoveDistance=0;
            var player=playerObject.AddComponent<ReviewPlayerMotor>();var character=playerObject.AddComponent<ReviewCharacterView>();
            var cameraObject=new GameObject("Main Camera");cameraObject.tag="MainCamera";var camera=cameraObject.AddComponent<Camera>();cameraObject.AddComponent<AudioListener>();camera.cullingMask=~(1<<31);camera.farClipPlane=farClip;camera.nearClipPlane=.08f;camera.backgroundColor=new Color(.64f,.78f,.88f);
            var cameraRig=cameraObject.AddComponent<ReviewCamera>();
            player.Configure(input,cameraRig,world,spawn);cameraRig.Configure(input,player.transform,settings);character.Configure(input,player,roles);
            // Inventario (barra rápida 1–5, mochila con Tab) y el objeto elegido en la mano.
            var (rules,loadout,poses)=ItemAssets.Prepare();
            // Clips de cuerpo para usar objetos (capas Acciones del Animator de cada rol).
            ItemActionAnimatorAssets.AddTo(roles);
            var inventory=playerObject.AddComponent<PlayerInventory>();inventory.Configure(rules,loadout);
            var held=playerObject.AddComponent<HeldItemView>();held.Configure(inventory,character,poses);
            // Clic derecho apunta y clic izquierdo dispara o usa la herramienta (ItemUser), con la mira desde la cámara.
            var user=playerObject.AddComponent<ItemUser>();user.Configure(inventory,held,input,cameraObject.transform);
            playerObject.AddComponent<ItemActionAnimator>().Configure(user,character);
            playerObject.AddComponent<ReviewInventoryControls>().Configure(input,inventory,user,cameraRig,player);
            // Vida (Task 18 y 19): la policía lo encuentra por el conjunto de sospechosos; derribado o arrestado no se mueve.
            var chest=new GameObject("Punto de detección").transform;chest.SetParent(playerObject.transform,false);chest.localPosition=new Vector3(0,1.25f,0);
            var health=playerObject.AddComponent<PlayerHealth>();health.Configure(HealthAssets.Settings(),EventAssets.Suspects(),chest);
            playerObject.AddComponent<ReviewPlayerLife>().Configure(health,player,user,character,roles.Select(DownClip).ToArray(),spawn);
            return new Parts{Input=input,Player=player,Camera=cameraRig,Character=character,Inventory=inventory,Items=user,Health=health};
        }
        // Clip de caída («Death») del modelo de un rol; null si no lo trae (entonces queda quieto sin caer).
        private static AnimationClip DownClip(GameObject role)
        {
            var skin=role!=null?role.GetComponentInChildren<SkinnedMeshRenderer>(true):null;
            string model=skin!=null && skin.sharedMesh!=null?AssetDatabase.GetAssetPath(skin.sharedMesh):null;
            return string.IsNullOrEmpty(model)?null:AssetDatabase.LoadAllAssetsAtPath(model).OfType<AnimationClip>().FirstOrDefault(c=>c.name=="Death" || c.name.EndsWith("|Death",System.StringComparison.Ordinal));
        }
        public static ReviewInterface CreateInterface(Parts rig,IPlayableWorld world,ReviewDoorInteraction doors,CityMapDefinition map,GameSettings settings)
        {
            new GameObject("Ajustes del juego").AddComponent<GameSettingsApplier>().Configure(settings);
            var pause=new GameObject("Menú de pausa").AddComponent<PauseMenuScreen>();pause.Configure(settings);
            var mapObject=new GameObject("Mapa y minimapa");
            var screen=mapObject.AddComponent<CityMapScreen>();screen.Configure(map,rig.Player.transform);
            var minimap=mapObject.AddComponent<CityMinimap>();minimap.Configure(map,rig.Player.transform);
            var items=new GameObject("Inventario");
            var hotbar=items.AddComponent<HotbarView>();hotbar.Configure(rig.Inventory,rig.Items);
            items.AddComponent<CrosshairView>().Configure(rig.Items);
            // Aviso en pantalla cuando un testigo termina de llamar a la policía.
            items.AddComponent<CrimeAlertView>().Configure(EventAssets.CrimeReports());
            // Vida del jugador y avisos de la policía (cuenta regresiva, llegada y retirada).
            items.AddComponent<HealthView>().Configure(rig.Health);
            items.AddComponent<PoliceAlertView>().Configure(EventAssets.PoliceResponse());
            var backpack=items.AddComponent<InventoryScreen>();backpack.Configure(rig.Inventory);
            var ui=new GameObject("Interfaz de revisión").AddComponent<ReviewInterface>();ui.Configure(rig.Input,rig.Player,world,doors,screen,minimap,pause,backpack,hotbar);
            return ui;
        }
        // Sol, luz ambiente y niebla; la niebla oculta el borde de lo que la cámara dibuja.
        public static Light Lighting(float fogStart,float fogEnd)
        {
            var sun=new GameObject("Sol").AddComponent<Light>();sun.type=LightType.Directional;sun.intensity=1.25f;sun.shadows=LightShadows.Soft;sun.cullingMask=~(1<<31);sun.transform.rotation=Quaternion.Euler(48,-30,0);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.58f,.64f,.69f);RenderSettings.sun=sun;RenderSettings.fog=true;RenderSettings.fogMode=FogMode.Linear;RenderSettings.fogColor=new Color(.65f,.76f,.83f);RenderSettings.fogStartDistance=fogStart;RenderSettings.fogEndDistance=fogEnd;
            return sun;
        }
    }
}
