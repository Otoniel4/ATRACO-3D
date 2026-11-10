using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
namespace Alarma.AI.CityLife.Editor
{
    public static class CityLifeAnimatorFactory
    {
        // «better» entrega, si los hay, clips de locomoción mejores que los del modelo (Idle, Walk, Run): los de la
        // Universal Animation Library. Vienen a velocidad natural, por eso no se aceleran como los del modelo.
        public static AnimatorController Create(string path,string modelPath,Func<string,AnimationClip> better=null)
        {
            var clips=AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__",StringComparison.Ordinal)).ToArray();
            AnimationClip Clip(string mode)=>better?.Invoke(mode)??clips.FirstOrDefault(c=>CityLifeImport.Matches(c.name,mode))??throw new InvalidOperationException("Falta clip "+mode+" en "+modelPath);
            float Rate(string mode,float own)=>better?.Invoke(mode)!=null?1f:own;
            var controller=AnimatorController.CreateAnimatorControllerAtPath(path);controller.AddParameter("Speed",AnimatorControllerParameterType.Float);
            controller.AddParameter(new AnimatorControllerParameter{name="WalkRate",type=AnimatorControllerParameterType.Float,defaultFloat=1});
            foreach(string flag in new[]{"Browse","Pay","Carry"})controller.AddParameter(flag,AnimatorControllerParameterType.Bool);
            var graph=controller.layers[0].stateMachine;
            var tree=new BlendTree{name="Reposo caminar correr",blendType=BlendTreeType.Simple1D,blendParameter="Speed",useAutomaticThresholds=false};AssetDatabase.AddObjectToAsset(tree,controller);
            tree.AddChild(Clip("Idle"),0);tree.AddChild(Clip("Walk"),1.6f);tree.AddChild(Clip("Run"),3.6f);
            var children=tree.children;children[1].timeScale=Rate("Walk",1.6f);children[2].timeScale=Rate("Run",1.2f);tree.children=children;
            var locomotion=graph.AddState("Locomotion");locomotion.motion=tree;graph.defaultState=locomotion;
            foreach(string name in new[]{"Browse","Pay","CarryWalk"})
            {
                var state=graph.AddState(name);state.motion=Clip(name);
                if(name=="CarryWalk")
                {
                    var holding=new BlendTree{name="Quieto o caminar con compra",blendType=BlendTreeType.Simple1D,blendParameter="Speed",useAutomaticThresholds=false};AssetDatabase.AddObjectToAsset(holding,controller);holding.AddChild(Clip("Idle"),0);holding.AddChild(Clip("CarryWalk"),1.6f);var motions=holding.children;motions[1].timeScale=1.6f;holding.children=motions;state.motion=holding;
                }
                var transition=graph.AddAnyStateTransition(state);transition.hasExitTime=false;transition.duration=.12f;transition.canTransitionToSelf=false;
                if(name=="Pay"){transition.AddCondition(AnimatorConditionMode.If,0,"Pay");continue;}
                transition.AddCondition(AnimatorConditionMode.IfNot,0,"Pay");
                if(name=="Browse"){transition.AddCondition(AnimatorConditionMode.If,0,"Browse");continue;}
                transition.AddCondition(AnimatorConditionMode.IfNot,0,"Browse");transition.AddCondition(AnimatorConditionMode.If,0,"Carry");
            }
            var back=graph.AddAnyStateTransition(locomotion);back.hasExitTime=false;back.duration=.12f;back.canTransitionToSelf=false;
            foreach(string flag in new[]{"Pay","Browse","Carry"})back.AddCondition(AnimatorConditionMode.IfNot,0,flag);
            return controller;
        }
    }
}
