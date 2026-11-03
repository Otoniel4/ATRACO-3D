using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Alarma.AI.CityLife;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewBuildWorld
    {
        public static Vector3 Vector(float[] p)=>new Vector3(p[0],p[1],p[2]);
        public static Vector3 Blender(float[] p)=>new Vector3(p[0],p[2],-p[1]);
        public static WorldReviewData Prepare(string folder,string assetFolder,WorldBuildData source)
        {
            var data=ScriptableObject.CreateInstance<WorldReviewData>();var cells=new List<WorldReviewCell>();string prefix="AlarmaWorld_"+Path.GetFileName(folder);
            string resources=folder+"/Resources/"+prefix;Directory.CreateDirectory(resources);AssetDatabase.Refresh();
            var scene=EditorSceneManager.NewPreviewScene();
            try
            {
                for(int i=0;i<source.cells.Length;i++)
                {
                    var cell=source.cells[i];if(EditorUtility.DisplayCancelableProgressBar("Preparar Alarma","Ciudad: "+(i+1)+" / "+source.cells.Length,.45f+.3f*i/source.cells.Length))throw new OperationCanceledException();
                    var model=AssetDatabase.LoadAssetAtPath<GameObject>(assetFolder+"/Art/"+cell.file);if(model==null)throw new InvalidOperationException("No se importó "+cell.file);
                    var instance=new GameObject("Chunk_"+cell.id);UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(instance,scene);
                    var imported=PrefabUtility.InstantiatePrefab(model,scene) as GameObject;if(imported==null)throw new InvalidOperationException("No se pudo preparar "+cell.id);imported.transform.SetParent(instance.transform,false);
                    try
                    {
                        var nodes=instance.GetComponentsInChildren<Transform>(true).Where(t=>t.name.StartsWith("N_",StringComparison.Ordinal)).ToDictionary(t=>t.name,t=>t,StringComparer.Ordinal);
                        foreach(var part in cell.parts)
                        {
                            if(!nodes.TryGetValue(part.node,out Transform node))throw new InvalidOperationException("Falta la pieza "+part.source+" en "+cell.id);
                            var filter=node.GetComponent<MeshFilter>();var renderer=node.GetComponent<MeshRenderer>();
                            if(part.collision==1 && filter!=null && filter.sharedMesh!=null){var collider=node.gameObject.AddComponent<MeshCollider>();collider.sharedMesh=filter.sharedMesh;}
                            if(part.collision==2)
                            {
                                var trunk=new GameObject("Tronco físico");trunk.transform.SetParent(instance.transform,false);trunk.transform.localPosition=Vector(part.treeCenter);
                                var collider=trunk.AddComponent<CapsuleCollider>();collider.radius=part.radius;collider.height=part.height;
                            }
                            if(part.wind && renderer!=null)node.gameObject.AddComponent<CityVegetationBounds>();
                            if(part.heroRoof && renderer!=null)node.gameObject.AddComponent<ReviewRoof>();
                            node.name=part.source;
                        }
                        if(PrefabUtility.SaveAsPrefabAsset(instance,resources+"/"+cell.id+".prefab")==null)throw new InvalidOperationException("No se pudo guardar "+cell.id);
                    }
                    finally{UnityEngine.Object.DestroyImmediate(instance);}
                    cells.Add(new WorldReviewCell{Resource=prefix+"/"+cell.id,Origin=Vector(cell.origin),Bounds=new Bounds(Vector(cell.center),Vector(cell.size)),Always=cell.always});
                }
            }
            finally{EditorSceneManager.ClosePreviewScene(scene);}
            data.Cells=cells.ToArray();data.Destinations=source.pois.Select(p=>new ReviewDestination{Id=p.id,Label=p.label,Position=Vector(p.position),Yaw=p.yaw}).ToArray();
            AssetDatabase.CreateAsset(data,folder+"/Data/WorldReview.asset");return data;
        }
        public static Dictionary<string,AutomaticShopDoor> Doors(string folder,WorldBuildData source,Transform player)
        {
            var result=new Dictionary<string,AutomaticShopDoor>(StringComparer.Ordinal);var sliding=new List<ReviewSlidingDoor>();
            var root=new GameObject("Puertas de los locales");
            foreach(var door in source.doors)
            {
                var shop=new GameObject("Door_"+door.id);shop.transform.SetParent(root.transform,false);
                var threshold=new GameObject("Acceso").transform;threshold.SetParent(shop.transform);threshold.position=Vector(door.threshold);
                if(door.single)threshold.position=new Vector3(threshold.position.x+2.4f,threshold.position.y,threshold.position.z);
                var model=AssetDatabase.LoadAssetAtPath<GameObject>(folder+"/Art/"+door.file);var leaves=new List<Transform>();
                foreach(var leaf in door.leaves)
                {
                    var instance=new GameObject("Hoja");instance.transform.SetParent(shop.transform,false);instance.transform.position=Vector(leaf.position);
                    var imported=PrefabUtility.InstantiatePrefab(model) as GameObject;if(imported==null)throw new InvalidOperationException("Falta puerta de "+door.id);imported.transform.SetParent(instance.transform,false);
                    Bounds b=new Bounds(instance.transform.position,Vector3.zero);bool first=true;
                    foreach(var renderer in instance.GetComponentsInChildren<Renderer>()){if(first){b=renderer.bounds;first=false;}else b.Encapsulate(renderer.bounds);}
                    var collider=instance.AddComponent<BoxCollider>();collider.center=instance.transform.InverseTransformPoint(b.center);collider.size=new Vector3(Mathf.Max(.06f,b.size.x),Mathf.Max(.06f,b.size.y),Mathf.Max(.08f,b.size.z));
                    instance.transform.rotation=Quaternion.Euler(0,leaf.yaw,0);leaves.Add(instance.transform);
                }
                if(door.single){var shutter=shop.AddComponent<ReviewSlidingDoor>();shutter.Configure(leaves[0],threshold);sliding.Add(shutter);}
                else{var component=shop.AddComponent<AutomaticShopDoor>();component.Configure(leaves[0],leaves[1],threshold);result.Add(door.id,component);}
            }
            root.AddComponent<ReviewDoorAccess>().Configure(player,result.Values.ToArray(),sliding.ToArray());return result;
        }
    }
}
