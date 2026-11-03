using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Alarma.AI.CityLife.Editor
{
    public static class CityLifeAnimatorFactory
    {
        public static AnimatorController Create(string path, string modelPath)
        {
            AnimationClip[] clips = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__",StringComparison.Ordinal)).ToArray();
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);
            controller.AddParameter("Speed",AnimatorControllerParameterType.Float);
            controller.AddParameter(new AnimatorControllerParameter { name="WalkRate",type=AnimatorControllerParameterType.Float,defaultFloat=1 });
            foreach (string flag in new[]{"Browse","Pay","Carry"}) controller.AddParameter(flag,AnimatorControllerParameterType.Bool);
            AnimatorStateMachine graph = controller.layers[0].stateMachine;
            foreach (string mode in CityLifeImport.Modes)
            {
                AnimationClip clip = clips.FirstOrDefault(c=>CityLifeImport.Matches(c.name,mode));
                if (clip == null) throw new InvalidOperationException("Falta clip "+mode+" en "+modelPath);
                AnimatorState state = graph.AddState(mode); state.motion=clip;
                if (mode=="Idle") graph.defaultState=state;
                if (mode=="Walk" || mode=="CarryWalk") { state.speedParameterActive=true;state.speedParameter="WalkRate"; }
            }
            foreach (string mode in new[]{"Pay","Browse","CarryWalk","Walk","Idle"})
            {
                AnimatorState state=graph.states.First(s=>s.state.name==mode).state;
                AnimatorStateTransition transition=graph.AddAnyStateTransition(state);
                transition.hasExitTime=false;transition.duration=.15f;transition.canTransitionToSelf=false;
                if (mode=="Pay") { transition.AddCondition(AnimatorConditionMode.If,0,"Pay"); continue; }
                transition.AddCondition(AnimatorConditionMode.IfNot,0,"Pay");
                if (mode=="Browse") { transition.AddCondition(AnimatorConditionMode.If,0,"Browse");continue; }
                transition.AddCondition(AnimatorConditionMode.IfNot,0,"Browse");
                transition.AddCondition(mode=="Idle"?AnimatorConditionMode.Less:AnimatorConditionMode.Greater,.10f,"Speed");
                if (mode=="Walk" || mode=="CarryWalk") transition.AddCondition(mode=="Walk"?AnimatorConditionMode.IfNot:AnimatorConditionMode.If,0,"Carry");
            }
            return controller;
        }
    }
}
