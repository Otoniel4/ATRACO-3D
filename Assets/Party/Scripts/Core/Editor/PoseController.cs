using System;
using System.Collections.Generic;
using UnityEditor.Animations;
using UnityEngine;

namespace Alarma.Core.Editor
{
    // Animator Controller de posturas: un estado por valor del enum (mismo nombre), al que se entra desde cualquier
    // otro cuando el parámetro entero vale su número. Lo usan los dobles de reacción de los civiles y la policía.
    public static class PoseController
    {
        // «instant»: posturas que entran sin transición (levantarse: la mezcla desde la caída la hace NpcRagdoll).
        public static AnimatorController Create<TPose>(string path, string parameter, IReadOnlyDictionary<TPose, Motion> motions, TPose rest, Func<TPose, bool> instant)
            where TPose : struct, Enum
        {
            var controller = AnimatorController.CreateAnimatorControllerAtPath(path);
            controller.AddParameter(parameter, AnimatorControllerParameterType.Int);
            var machine = controller.layers[0].stateMachine;
            foreach (TPose pose in Enum.GetValues(typeof(TPose)))
            {
                if (!motions.TryGetValue(pose, out var motion)) throw new InvalidOperationException("Falta el clip de la postura " + pose);
                var state = machine.AddState(pose.ToString());
                state.motion = motion;
                if (EqualityComparer<TPose>.Default.Equals(pose, rest)) machine.defaultState = state;
                var enter = machine.AddAnyStateTransition(state);
                enter.hasExitTime = false; enter.duration = instant(pose) ? 0f : .2f; enter.canTransitionToSelf = false;
                enter.AddCondition(AnimatorConditionMode.Equals, Convert.ToInt32(pose), parameter);
            }
            return controller;
        }
    }
}
