using UnityEngine;
using Alarma.Player.Items;
namespace Alarma.City.Playtest
{
    // Traduce los controles de la prueba a la barra rápida: teclas 1 a 5 eligen el espacio (la misma tecla otra vez lo
    // guarda) y la rueda pasa al siguiente. Al apuntar, la cámara pasa sobre el hombro y el cuerpo mira hacia la mira.
    // No funciona con un menú abierto (los controles quedan inactivos).
    public sealed class ReviewInventoryControls:MonoBehaviour
    {
        [SerializeField] private ReviewInput input;
        [SerializeField] private PlayerInventory owner;
        [SerializeField] private ItemUser user;
        [SerializeField] private ReviewCamera view;
        [SerializeField] private ReviewPlayerMotor motor;
        public void Configure(ReviewInput controls,PlayerInventory playerInventory,ItemUser itemUser,ReviewCamera camera,ReviewPlayerMotor body){input=controls;owner=playerInventory;user=itemUser;view=camera;motor=body;}
        private void Update()
        {
            float aim=user!=null?user.AimWeight:0;if(view!=null)view.Aim=aim;if(motor!=null){motor.FaceView=aim>.3f;motor.HoldStill=user!=null&&user.HoldsStill;}
            if(input==null || owner==null || owner.Inventory==null || !input.Active)return;
            if(input.SlotPressed>=0)owner.Inventory.Select(input.SlotPressed);
            else if(input.Scroll!=0)owner.Inventory.Cycle(-input.Scroll); // rueda abajo = espacio siguiente
        }
    }
}
