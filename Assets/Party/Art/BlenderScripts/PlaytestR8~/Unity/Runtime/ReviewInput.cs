using UnityEngine;
using UnityEngine.InputSystem;
namespace Alarma.City.Playtest
{
    [DefaultExecutionOrder(-300)]
    public sealed class ReviewInput:MonoBehaviour
    {
        public bool MenuOpen{get;private set;}
        public bool CursorFree{get;private set;}
        public bool Active=>!MenuOpen && !CursorFree;
        public Vector2 Move{get;private set;}
        public Vector2 Look{get;private set;}
        public float Lift{get;private set;}
        public bool Run{get;private set;}
        public bool FlyPressed{get;private set;}
        public bool MapPressed{get;private set;}
        public bool CatalogPressed{get;private set;}
        public int RolePressed{get;private set;}=-1;
        private void Start()=>ApplyCursor();
        public void SetMenu(bool open){MenuOpen=open;ApplyCursor();}
        private void ApplyCursor(){bool free=MenuOpen || CursorFree;Cursor.lockState=free?CursorLockMode.None:CursorLockMode.Locked;Cursor.visible=free;}
        private void Update()
        {
            var k=Keyboard.current;var m=Mouse.current;Move=Look=Vector2.zero;Lift=0;RolePressed=-1;FlyPressed=MapPressed=CatalogPressed=false;Run=false;
            if(k==null || m==null)return;
            if(k.escapeKey.wasPressedThisFrame){CursorFree=!CursorFree;ApplyCursor();}
            if(CursorFree && !MenuOpen && m.rightButton.wasPressedThisFrame){CursorFree=false;ApplyCursor();}
            MapPressed=k.mKey.wasPressedThisFrame;CatalogPressed=k.f6Key.wasPressedThisFrame;
            if(!Active)return;
            Move=new Vector2((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0),(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0));Move=Vector2.ClampMagnitude(Move,1);
            Look=m.delta.ReadValue();Lift=(k.eKey.isPressed?1:0)-(k.qKey.isPressed?1:0);Run=k.leftShiftKey.isPressed;FlyPressed=k.vKey.wasPressedThisFrame;
            if(k.f1Key.wasPressedThisFrame)RolePressed=0;if(k.f2Key.wasPressedThisFrame)RolePressed=1;if(k.f3Key.wasPressedThisFrame)RolePressed=2;if(k.f4Key.wasPressedThisFrame)RolePressed=3;
        }
        private void OnDisable(){Cursor.lockState=CursorLockMode.None;Cursor.visible=true;}
    }
}
