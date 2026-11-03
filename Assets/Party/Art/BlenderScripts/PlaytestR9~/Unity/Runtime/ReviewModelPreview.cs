using UnityEngine;
namespace Alarma.City.Playtest
{
    // El catálogo se dibuja en otra cámara y capa; sus modelos nunca aparecen físicamente en la ciudad.
    public sealed class ReviewModelPreview:MonoBehaviour
    {
        private Camera previewCamera;private GameObject instance;private RenderTexture texture;
        public RenderTexture Texture=>texture;
        private void EnsureCamera()
        {
            if(previewCamera!=null)return;var obj=new GameObject("Cámara del catálogo");obj.transform.SetParent(transform);previewCamera=obj.AddComponent<Camera>();previewCamera.cullingMask=1<<31;previewCamera.clearFlags=CameraClearFlags.SolidColor;previewCamera.backgroundColor=new Color(.08f,.13f,.16f);previewCamera.nearClipPlane=.01f;previewCamera.farClipPlane=100;previewCamera.depth=-5;
            texture=new RenderTexture(640,640,24,RenderTextureFormat.ARGB32);texture.Create();previewCamera.targetTexture=texture;
            var lightObject=new GameObject("Luz del catálogo");lightObject.transform.SetParent(transform);var light=lightObject.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.4f;light.cullingMask=1<<31;lightObject.transform.rotation=Quaternion.Euler(35,-35,0);
        }
        public void Show(GameObject model)
        {
            EnsureCamera();if(instance!=null){instance.SetActive(false);Destroy(instance);}if(model==null)return;
            instance=new GameObject("Modelo de revisión");instance.transform.SetParent(transform,false);instance.transform.position=new Vector3(0,-1000,0);Instantiate(model,instance.transform,false);SetLayer(instance.transform);
            var animator=instance.GetComponentInChildren<Animator>();if(animator!=null){animator.Rebind();animator.Update(0);}
            Bounds bounds=new Bounds(instance.transform.position,Vector3.one);bool found=false;
            foreach(var r in instance.GetComponentsInChildren<Renderer>())if(r.enabled){if(!found){bounds=r.bounds;found=true;}else bounds.Encapsulate(r.bounds);}
            Vector3 target=bounds.center;float size=Mathf.Max(.1f,Mathf.Max(bounds.size.x,Mathf.Max(bounds.size.y,bounds.size.z)));
            previewCamera.transform.position=target+new Vector3(1,.65f,-1.6f).normalized*size*1.7f;previewCamera.transform.LookAt(target);previewCamera.enabled=true;
        }
        private static void SetLayer(Transform t){t.gameObject.layer=31;foreach(Transform c in t)SetLayer(c);}
        public void Rotate(float degrees){if(instance!=null)instance.transform.Rotate(Vector3.up,degrees,Space.World);}
        public void Hide(){if(previewCamera!=null)previewCamera.enabled=false;if(instance!=null){Destroy(instance);instance=null;}}
        private void OnDestroy(){if(texture!=null){texture.Release();Destroy(texture);}}
    }
}
