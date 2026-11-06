using UnityEngine;
using UnityEngine.InputSystem;
using Alarma.Player.Items;
namespace Alarma.City.Playtest
{
    // Controles de la prueba: WASD, Shift, ratón, E (puertas), M (mapa), Esc (menú), 1–5 y rueda (barra rápida), Tab (inventario)
    // clic derecho (apuntar), clic izquierdo (disparar o usar) y F1–F4 (personaje, sin mostrar en pantalla).
    [DefaultExecutionOrder(-300)]
    public sealed class ReviewInput:MonoBehaviour,IItemControls
    {
        public bool MenuOpen{get;private set;}
        public bool Active=>!MenuOpen;
        public Vector2 Move{get;private set;}
        public Vector2 Look{get;private set;}
        public bool Run{get;private set;}
        public bool InteractPressed{get;private set;}
        public bool MapPressed{get;private set;}
        public bool PausePressed{get;private set;}
        public bool InventoryPressed{get;private set;}
        public int SlotPressed{get;private set;}=-1; // 0 a 4 con las teclas 1 a 5
        public int Scroll{get;private set;}         // +1 rueda arriba, -1 rueda abajo
        public bool AimHeld{get;private set;}
        public bool UsePressed{get;private set;}
        public bool UseHeld{get;private set;}
        public int RolePressed{get;private set;}=-1;
        private void Start()=>ApplyCursor();
        public void SetMenu(bool open){MenuOpen=open;ApplyCursor();}
        private void ApplyCursor(){Cursor.lockState=MenuOpen?CursorLockMode.None:CursorLockMode.Locked;Cursor.visible=MenuOpen;}
        private void Update()
        {
            var k=Keyboard.current;var m=Mouse.current;Move=Look=Vector2.zero;RolePressed=SlotPressed=-1;Scroll=0;InteractPressed=MapPressed=PausePressed=InventoryPressed=AimHeld=UsePressed=UseHeld=false;Run=false;
            if(k==null || m==null)return;
            PausePressed=k.escapeKey.wasPressedThisFrame;MapPressed=k.mKey.wasPressedThisFrame;InventoryPressed=k.tabKey.wasPressedThisFrame;
            if(!Active)return;
            Move=new Vector2((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0),(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0));Move=Vector2.ClampMagnitude(Move,1);
            Look=m.delta.ReadValue();Run=k.leftShiftKey.isPressed;InteractPressed=k.eKey.wasPressedThisFrame;
            for(int i=0;i<5;i++)if(k[Key.Digit1+i].wasPressedThisFrame)SlotPressed=i;
            float wheel=m.scroll.ReadValue().y;Scroll=wheel>0?1:wheel<0?-1:0;
            AimHeld=m.rightButton.isPressed;UsePressed=m.leftButton.wasPressedThisFrame;UseHeld=m.leftButton.isPressed;
            if(k.f1Key.wasPressedThisFrame)RolePressed=0;if(k.f2Key.wasPressedThisFrame)RolePressed=1;if(k.f3Key.wasPressedThisFrame)RolePressed=2;if(k.f4Key.wasPressedThisFrame)RolePressed=3;
        }
        private void OnDisable(){Cursor.lockState=CursorLockMode.None;Cursor.visible=true;}
    }
}
