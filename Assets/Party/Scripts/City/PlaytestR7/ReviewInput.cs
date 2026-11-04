using UnityEngine;
using UnityEngine.InputSystem;
namespace Alarma.City.Playtest
{
    // Controles de la prueba: WASD, Shift, ratón, E (puertas), M (mapa), Esc (menú) y F1–F4 (personaje, sin mostrar en pantalla).
    [DefaultExecutionOrder(-300)]
    public sealed class ReviewInput:MonoBehaviour
    {
        public bool MenuOpen{get;private set;}
        public bool Active=>!MenuOpen;
        public Vector2 Move{get;private set;}
        public Vector2 Look{get;private set;}
        public bool Run{get;private set;}
        public bool InteractPressed{get;private set;}
        public bool MapPressed{get;private set;}
        public bool PausePressed{get;private set;}
        public int RolePressed{get;private set;}=-1;
        private void Start()=>ApplyCursor();
        public void SetMenu(bool open){MenuOpen=open;ApplyCursor();}
        private void ApplyCursor(){Cursor.lockState=MenuOpen?CursorLockMode.None:CursorLockMode.Locked;Cursor.visible=MenuOpen;}
        private void Update()
        {
            var k=Keyboard.current;var m=Mouse.current;Move=Look=Vector2.zero;RolePressed=-1;InteractPressed=MapPressed=PausePressed=false;Run=false;
            if(k==null || m==null)return;
            PausePressed=k.escapeKey.wasPressedThisFrame;MapPressed=k.mKey.wasPressedThisFrame;
            if(!Active)return;
            Move=new Vector2((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0),(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0));Move=Vector2.ClampMagnitude(Move,1);
            Look=m.delta.ReadValue();Run=k.leftShiftKey.isPressed;InteractPressed=k.eKey.wasPressedThisFrame;
            if(k.f1Key.wasPressedThisFrame)RolePressed=0;if(k.f2Key.wasPressedThisFrame)RolePressed=1;if(k.f3Key.wasPressedThisFrame)RolePressed=2;if(k.f4Key.wasPressedThisFrame)RolePressed=3;
        }
        private void OnDisable(){Cursor.lockState=CursorLockMode.None;Cursor.visible=true;}
    }
}
