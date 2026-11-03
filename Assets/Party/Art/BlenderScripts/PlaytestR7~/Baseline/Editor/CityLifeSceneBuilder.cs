using System;
using System.IO;
using System.Linq;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace Alarma.AI.CityLife.Editor
{
    [Serializable] public sealed class PointData { public float[] v; }
    [Serializable] public sealed class BoxData { public float[] position,size; }
    [Serializable] public sealed class ShopData
    {
        public string id,product; public int priceCents; public float[] center,browse,staff,counter,scan,receipt,till; public PointData[] walk,entry,queue,exit,browseStations,products;
        public float staffYaw; public int staffVariant;
    }
    [Serializable] public sealed class DistrictData { public ShopData[] shops; public BoxData[] obstacles,floors; }

    public static class CityLifeSceneBuilder
    {
        [MenuItem("Alarma/Ciudad/Crear demo local R6")]
        public static void Build()
        {
            string review=CityLifeImport.ReviewFolder;
            var config=JsonUtility.FromJson<DistrictData>(File.ReadAllText(review+"/unity_district.json"));
            var characters=JsonUtility.FromJson<CharacterManifest>(File.ReadAllText(review+"/unity_characters.json"));
            if (characters.characters.Length<10) throw new InvalidOperationException("Se requieren al menos diez variantes de civiles.");
            string generated="Assets/Party/Generated/CityLifeR6_"+DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");
            foreach(string child in new[]{"Art","Data","Materials","Controllers","Prefabs","Scenes"}) Directory.CreateDirectory(generated+"/"+child);
            AssetDatabase.Refresh(); CityLifeImport.CopyAssets(generated); CityLifeImport.ConfigureCharacters(generated,characters); CityLifeImport.CreateMaterials(generated);
            Scene scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);SceneManager.SetActiveScene(scene);
            var world=new GameObject("CityLifeWorld_R6");
            var visual=PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(generated+"/Art/District_CityLife_R6.fbx")) as GameObject;
            if(visual==null)throw new InvalidOperationException("Falta el modelo del distrito comercial.");
            visual.transform.SetParent(world.transform,false);
            foreach(Collider collider in visual.GetComponentsInChildren<Collider>(true))UnityEngine.Object.DestroyImmediate(collider);
            foreach(MeshRenderer renderer in visual.GetComponentsInChildren<MeshRenderer>(true))
                if(renderer.sharedMaterials.Any(m=>m!=null && m.shader!=null && m.shader.name=="Alarma/Vegetation/Natural Wind R3"))renderer.gameObject.AddComponent<CityVegetationBounds>();
            foreach(Transform item in visual.GetComponentsInChildren<Transform>(true)) if(item.name.StartsWith("Roof_",StringComparison.Ordinal))item.gameObject.SetActive(false);
            var colliders=new GameObject("NavigationProxies");colliders.transform.SetParent(world.transform,false);
            foreach(BoxData box in config.floors.Concat(config.obstacles))
            {
                var obj=new GameObject("NavigationShape");obj.transform.SetParent(colliders.transform,false);obj.transform.localPosition=Point(box.position);
                obj.AddComponent<BoxCollider>().size=new Vector3(box.size[0],box.size[2],box.size[1]);
            }
            var surface=world.AddComponent<NavMeshSurface>();surface.collectObjects=CollectObjects.Children;surface.useGeometry=NavMeshCollectGeometry.PhysicsColliders;
            CityTrafficGraphBuilder.Bake(surface,colliders.transform);
            if(surface.navMeshData==null)throw new InvalidOperationException("No se pudo construir el NavMesh.");
            AssetDatabase.CreateAsset(surface.navMeshData,generated+"/Data/CityLifeNavMesh.asset");EditorUtility.SetDirty(surface);
            var traffic=world.AddComponent<CityTrafficController>();var graph=CityTrafficGraphBuilder.Create();AssetDatabase.CreateAsset(graph,generated+"/Data/TrafficGraph.asset");traffic.Configure(graph,.7f);
            var settings=ScriptableObject.CreateInstance<PedestrianSettings>();AssetDatabase.CreateAsset(settings,generated+"/Data/PedestrianSettings.asset");
            var variants=new PedestrianActor[characters.characters.Length];
            for(int i=0;i<variants.Length;i++)variants[i]=MakePrefab(generated,characters.characters[i]);
            var shops=new ShopActivity[config.shops.Length];
            for(int i=0;i<shops.Length;i++)
            {
                ShopData data=config.shops[i];var obj=new GameObject("Routine_"+data.id);obj.transform.position=Point(data.center);
                ShopActivity shop=obj.AddComponent<ShopActivity>();shops[i]=shop;
                Transform[] walk=Markers(obj.transform,"Walk",data.walk),entry=Markers(obj.transform,"Entry",data.entry),queue=Markers(obj.transform,"Queue",data.queue),exit=Markers(obj.transform,"Exit",data.exit);
                Transform[] browse=Markers(obj.transform,"Browse",data.browseStations),products=Markers(obj.transform,"Product",data.products);
                Transform counter=Marker(obj.transform,"Counter",data.counter),scan=Marker(obj.transform,"Scan",data.scan),receipt=Marker(obj.transform,"Receipt",data.receipt),till=Marker(obj.transform,"Till",data.till);
                var tasks=ScriptableObject.CreateInstance<ShopTaskSettings>();tasks.ShopId=data.id;tasks.ProductName=data.product;tasks.PriceCents=data.priceCents;
                tasks.ProductPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(generated+"/Art/Props/"+data.product+".fbx");tasks.MoneyPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(generated+"/Art/Props/CashNote.fbx");tasks.ReceiptPrefab=AssetDatabase.LoadAssetAtPath<GameObject>(generated+"/Art/Props/Receipt.fbx");
                if(tasks.ProductPrefab==null || tasks.MoneyPrefab==null || tasks.ReceiptPrefab==null)throw new InvalidOperationException("Faltan productos de compra R6.");
                AssetDatabase.CreateAsset(tasks,generated+"/Data/Shop_"+data.id+".asset");
                shop.Configure(walk,entry,browse,queue,exit,products,counter,scan,receipt,till,tasks);
                var door=obj.AddComponent<AutomaticShopDoor>();Transform gateway=Marker(obj.transform,"Threshold",new[]{0f,-5.12f,.16f});
                Transform left=Find(visual.transform,"Door_"+data.id+"_L"),right=Find(visual.transform,"Door_"+data.id+"_R");
                if(left==null || right==null)throw new InvalidOperationException("Faltan las hojas de puerta de "+data.id);
                door.Configure(left,right,gateway);
                ValidatePaths(entry[0].position,walk.Concat(entry).Concat(queue).Concat(exit).Concat(browse));
                var staffObject=PrefabUtility.InstantiatePrefab(variants[data.staffVariant].gameObject) as GameObject;
                if(staffObject==null)throw new InvalidOperationException("No se pudo crear el dependiente.");
                PedestrianActor staff=staffObject.GetComponent<PedestrianActor>();
                staff.gameObject.name="Staff_"+data.id;staff.enabled=false;staff.transform.position=obj.transform.TransformPoint(Point(data.staff));staff.transform.rotation=Quaternion.Euler(0,data.staffYaw*Mathf.Rad2Deg,0);
                staff.GetComponent<NavMeshAgent>().enabled=false;
                Transform staffGrip=staff.GetComponentsInChildren<Transform>(true).First(t=>t.name.StartsWith("Grip_R6_",StringComparison.Ordinal));shop.ConfigureStaff(data.staffVariant,door,staffGrip);
                CityTrafficGraphBuilder.Validate(graph,queue.Concat(browse));
                CityTrafficGraphBuilder.ValidateRoutes(graph,entry[0],walk.Concat(entry).Concat(queue).Concat(exit).Concat(browse));
                var cashier=staff.gameObject.AddComponent<CashierPresentation>();cashier.Configure(shop,staff.GetComponentInChildren<Animator>());
            }
            var cameraObject=new GameObject("Cámara de revisión");Camera camera=cameraObject.AddComponent<Camera>();cameraObject.AddComponent<AudioListener>();cameraObject.AddComponent<CityLifePreviewCamera>();
            cameraObject.transform.position=new Vector3(-10,11,20);cameraObject.transform.LookAt(new Vector3(-18,1,3));camera.farClipPlane=450;
            var sunlight=new GameObject("Sun");Light light=sunlight.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.2f;light.shadows=LightShadows.Soft;sunlight.transform.rotation=Quaternion.Euler(45,-35,0);
            RenderSettings.ambientLight=new Color(.60f,.66f,.71f);
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.sun=light;
            var population=new GameObject("Población local R6");var director=population.AddComponent<CityPopulationDirector>();var authority=population.AddComponent<LocalCityLifeAuthority>();
            director.Configure(settings,variants,shops,cameraObject.transform,authority,traffic);
            EditorSceneManager.SaveScene(scene,generated+"/Scenes/CityLife_R6.unity");AssetDatabase.SaveAssets();
            Selection.activeGameObject=population;EditorGUIUtility.PingObject(AssetDatabase.LoadAssetAtPath<SceneAsset>(generated+"/Scenes/CityLife_R6.unity"));
            Debug.Log("Alarma R6: demo local creada con "+variants.Length+" variantes, 3 dependientes, rutinas, puertas y NavMesh. Prueba Play y revisa la guía; todavía no sincroniza una sesión online.");
        }

        private static PedestrianActor MakePrefab(string folder,CharacterEntry data)
        {
            string modelPath=folder+"/Art/Characters/"+data.id+".fbx";GameObject model=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var root=new GameObject("Pedestrian_"+data.id);var visual=(GameObject)PrefabUtility.InstantiatePrefab(model);visual.transform.SetParent(root.transform,false);
            Animator animator=visual.GetComponentInChildren<Animator>();if(animator==null)animator=visual.AddComponent<Animator>();
            animator.runtimeAnimatorController=CityLifeAnimatorFactory.Create(folder+"/Controllers/"+data.id+".controller",modelPath);animator.applyRootMotion=false;
            var actor=root.AddComponent<PedestrianActor>();root.GetComponent<NavMeshAgent>().enabled=false;
            Transform bag=visual.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name.StartsWith("ShoppingBag_",StringComparison.Ordinal));
            if(bag==null)throw new InvalidOperationException("Falta la bolsa en "+data.id);
            bag.gameObject.SetActive(false);root.GetComponent<PedestrianPresentation>().Configure(animator,bag.gameObject);
            Transform grip=visual.GetComponentsInChildren<Transform>(true).First(t=>t.name.StartsWith("Grip_R6_",StringComparison.Ordinal));actor.ConfigureGrip(grip);
            GameObject prefab=PrefabUtility.SaveAsPrefabAsset(root,folder+"/Prefabs/"+data.id+".prefab");UnityEngine.Object.DestroyImmediate(root);
            return prefab.GetComponent<PedestrianActor>();
        }
        private static Transform Find(Transform root,string name) => root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name==name);
        private static Vector3 Point(float[] p)=>new Vector3(p[0],p[2],-p[1]);
        private static Transform Marker(Transform parent,string name,float[] p) {var obj=new GameObject(name);obj.transform.SetParent(parent,false);obj.transform.localPosition=Point(p);return obj.transform;}
        private static Transform[] Markers(Transform parent,string name,PointData[] points)=>points.Select((p,i)=>Marker(parent,name+"_"+i,p.v)).ToArray();
        private static void ValidatePaths(Vector3 start,System.Collections.Generic.IEnumerable<Transform> points)
        {
            if(!NavMesh.SamplePosition(start,out NavMeshHit origin,.55f,NavMesh.AllAreas))throw new InvalidOperationException("Entrada fuera del NavMesh.");
            var path=new NavMeshPath();
            foreach(Transform point in points)
                if(!NavMesh.SamplePosition(point.position,out NavMeshHit end,.55f,NavMesh.AllAreas) || !NavMesh.CalculatePath(origin.position,end.position,NavMesh.AllAreas,path) || path.status!=NavMeshPathStatus.PathComplete)
                    throw new InvalidOperationException("Punto de rutina inaccesible: "+point.parent.name+"/"+point.name);
        }
    }
}
