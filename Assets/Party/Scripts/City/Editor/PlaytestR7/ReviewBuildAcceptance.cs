using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest.Editor
{
    // Estas comprobaciones se ejecutan en Unity cuando Alain pulsa el menú, antes de publicar la escena.
    public static class ReviewBuildAcceptance
    {
        public static void ValidateAnimation(string path)
        {
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);var scene=EditorSceneManager.NewPreviewScene();GameObject instance=null;
            try
            {
                instance=(GameObject)PrefabUtility.InstantiatePrefab(model,scene);
                var foot=instance.GetComponentsInChildren<Transform>(true).First(t=>t.name=="LeftFoot");
                foreach(string mode in new[]{"Walk","Run"})
                {
                    var clip=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().First(c=>c.name==mode);
                    var positions=new Vector3[8];for(int i=0;i<8;i++){clip.SampleAnimation(instance,clip.length*i/8);positions[i]=foot.position;}
                    if(positions.Max(p=>(p-positions[0]).magnitude)<.07f)throw new InvalidOperationException("El clip "+mode+" no mueve el pie al importarlo: "+path);
                }
            }
            finally{if(instance!=null)UnityEngine.Object.DestroyImmediate(instance);EditorSceneManager.ClosePreviewScene(scene);}
        }
        public static void Validate(Scene scene,string folder)
        {
            var roots=scene.GetRootGameObjects();var shops=roots.SelectMany(o=>o.GetComponentsInChildren<ShopActivity>(true)).ToArray();
            if(shops.Length!=5 || shops.Any(s=>!s.IsConfigured || s.Traffic==null))throw new InvalidOperationException("No se prepararon las cinco rutinas de compra.");
            var doors=roots.SelectMany(o=>o.GetComponentsInChildren<AutomaticShopDoor>(true)).ToArray();
            if(doors.Length!=8 || doors.Any(d=>!d.HasCollision))throw new InvalidOperationException("Una puerta no tiene hojas y colisiones completas.");
            foreach(string path in Directory.GetFiles(folder+"/Prefabs","*.prefab"))
            {
                var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);var actor=prefab.GetComponent<PedestrianActor>();
                if(actor!=null && (actor.Grip==null || actor.GetComponent<CapsuleCollider>()==null))throw new InvalidOperationException("Faltan agarre persistido o colisión de NPC: "+path);
            }
            if(roots.SelectMany(o=>o.GetComponentsInChildren<StreetPopulationDirector>(true)).Count()!=1)throw new InvalidOperationException("Falta la población de aceras.");
            File.WriteAllText(folder+"/AcceptanceBuild.json","{\"animation_sampling\":true,\"shop_routines\":5,\"hinged_doors_with_colliders\":8,\"street_population\":true,\"play_tested\":false}");
        }
    }
}
