using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Alarma.AI.CityLife
{
    // Encuentra un hueso en cualquiera de los esqueletos del elenco: el avatar Humanoid si existe;
    // si no, el nombre del esqueleto propio (Blender) o del de los packs modulares de Quaternius.
    public static class RigBones
    {
        private static readonly Dictionary<HumanBodyBones,string[]> Names=new Dictionary<HumanBodyBones,string[]>
        {
            {HumanBodyBones.RightUpperArm,new[]{"RightUpperArm","UpperArm.R"}},
            {HumanBodyBones.RightLowerArm,new[]{"RightLowerArm","LowerArm.R"}},
            {HumanBodyBones.Spine,new[]{"Spine","Abdomen"}},
            {HumanBodyBones.LeftFoot,new[]{"LeftFoot","Foot.L"}},
        };
        public static Transform Find(Transform root,HumanBodyBones bone)
        {
            var animator=root.GetComponentInChildren<Animator>(true);
            if(animator!=null && animator.isHuman){Transform human=animator.GetBoneTransform(bone);if(human!=null)return human;}
            if(!Names.TryGetValue(bone,out string[] names))return null;
            return root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>Array.IndexOf(names,t.name)>=0);
        }
    }
}
