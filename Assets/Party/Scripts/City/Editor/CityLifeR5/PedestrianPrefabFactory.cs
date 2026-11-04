using System;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;

namespace Alarma.AI.CityLife.Editor
{
    // Prefab de peatón a partir de un modelo del elenco: Animator con Blend Tree de locomoción, colisión, bolsa y agarre.
    public static class PedestrianPrefabFactory
    {
        public static PedestrianActor MakePrefab(string folder,CharacterEntry data)
        {
            string modelPath=folder+"/Art/Characters/"+data.id+".fbx";GameObject model=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var root=new GameObject("Pedestrian_"+data.id);var visual=(GameObject)PrefabUtility.InstantiatePrefab(model);visual.transform.SetParent(root.transform,false);
            Animator animator=visual.GetComponentInChildren<Animator>();if(animator==null)animator=visual.AddComponent<Animator>();
            animator.runtimeAnimatorController=CityLifeAnimatorFactory.Create(folder+"/Controllers/"+data.id+".controller",modelPath);animator.applyRootMotion=false;animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
            foreach(var skin in visual.GetComponentsInChildren<SkinnedMeshRenderer>(true))skin.updateWhenOffscreen=true;
            var actor=root.AddComponent<PedestrianActor>();root.GetComponent<NavMeshAgent>().enabled=false;
            root.layer=29;var bodyCollider=root.AddComponent<CapsuleCollider>();bodyCollider.height=1.7f;bodyCollider.radius=.23f;bodyCollider.center=new Vector3(0,.85f,0);
            Transform bag=visual.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name.StartsWith("ShoppingBag_",StringComparison.Ordinal));
            if(bag==null)throw new InvalidOperationException("Falta la bolsa en "+data.id);
            bag.gameObject.SetActive(false);root.GetComponent<PedestrianPresentation>().Configure(animator,bag.gameObject);
            Transform grip=visual.GetComponentsInChildren<Transform>(true).First(t=>t.name.StartsWith("Grip_R6_",StringComparison.Ordinal));actor.ConfigureGrip(grip);
            GameObject prefab=PrefabUtility.SaveAsPrefabAsset(root,folder+"/Prefabs/"+data.id+".prefab");UnityEngine.Object.DestroyImmediate(root);
            return prefab.GetComponent<PedestrianActor>();
        }
    }
}
