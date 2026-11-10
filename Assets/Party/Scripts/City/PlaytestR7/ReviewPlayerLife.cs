using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
using Alarma.Player.Health;
using Alarma.Player.Items;
namespace Alarma.City.Playtest
{
    // Lo que le pasa al cuerpo del jugador de prueba según su vida (PlayerHealth): derribado o arrestado no camina ni
    // usa objetos y cae con el clip de caída de su personaje; al quedar libre tras un arresto vuelve al escondite.
    // El clip se reproduce por encima del Animator (Playables) y al terminar el Animator sigue como estaba.
    public sealed class ReviewPlayerLife:MonoBehaviour
    {
        [SerializeField] private PlayerHealth health;
        [SerializeField] private ReviewPlayerMotor motor;
        [SerializeField] private ItemUser items;
        [SerializeField] private ReviewCharacterView character;
        [SerializeField,Tooltip("Clip de caída de cada rol, en el mismo orden que los modelos.")] private AnimationClip[] downClips=System.Array.Empty<AnimationClip>();
        [SerializeField] private Vector3 respawn;
        private PlayableGraph graph;private AnimationClipPlayable falling;private float fallLength;
        public void Configure(PlayerHealth playerHealth,ReviewPlayerMotor body,ItemUser itemUser,ReviewCharacterView view,AnimationClip[] clips,Vector3 respawnPoint)
        {health=playerHealth;motor=body;items=itemUser;character=view;downClips=clips;respawn=respawnPoint;}
        private void OnEnable(){if(health!=null)health.StateChanged+=OnState;if(character!=null)character.RigChanged+=StopFall;}
        private void OnDisable(){if(health!=null)health.StateChanged-=OnState;if(character!=null)character.RigChanged-=StopFall;StopFall();}
        private void OnState(LifeState previous,LifeState next)
        {
            bool free=next==LifeState.Alive;
            if(motor!=null)motor.Blocked=!free;
            if(items!=null)items.enabled=free;
            if(next==LifeState.Downed)Fall();
            if(!free)return;
            StopFall();
            if(previous==LifeState.Arrested && motor!=null)motor.Teleport(respawn);
        }
        private void Fall()
        {
            StopFall();
            var animator=character!=null?character.CurrentAnimator:null;
            var clip=character!=null && character.Role<downClips.Length?downClips[character.Role]:null;
            if(animator==null || clip==null)return;
            falling=AnimationPlayableUtilities.PlayClip(animator,clip,out graph);fallLength=clip.length;
        }
        // Al llegar al final se queda en el último cuadro (tendido), aunque el clip esté importado en bucle.
        private void Update(){if(graph.IsValid() && falling.GetSpeed()>0 && falling.GetTime()>=fallLength-.04f)falling.SetSpeed(0);}
        private void StopFall(){if(graph.IsValid())graph.Destroy();}
    }
}
