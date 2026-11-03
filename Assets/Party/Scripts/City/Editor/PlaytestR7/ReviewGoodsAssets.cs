using System.IO;
using UnityEditor;
using UnityEngine;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewGoodsAssets
    {
        public static GameObject Prefab(string folder,string name)
        {
            string target=folder+"/Prefabs/Goods_"+name+".prefab";var existing=AssetDatabase.LoadAssetAtPath<GameObject>(target);if(existing!=null)return existing;
            var root=new GameObject(name);var model=AssetDatabase.LoadAssetAtPath<GameObject>(folder+"/Art/Props/"+name+".fbx");if(model==null)throw new FileNotFoundException(name);
            try{var imported=(GameObject)PrefabUtility.InstantiatePrefab(model);imported.transform.SetParent(root.transform,false);ReviewSpatialImport.Normalize(imported);return PrefabUtility.SaveAsPrefabAsset(root,target);}
            finally{Object.DestroyImmediate(root);}
        }
    }
}
