using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewSpatialImport
    {
        [Serializable] private sealed class Entry{public string model;public int a,b,c,d;public double offsetX,offsetZ,error;}
        [Serializable] private sealed class Entries{public Entry[] models;}
        private static readonly List<Entry> entries=new List<Entry>();
        public static void Begin()=>entries.Clear();
        public static void Save(string folder)=>System.IO.File.WriteAllText(folder+"/SpatialCalibration.json",JsonUtility.ToJson(new Entries{models=entries.ToArray()},true));
        public static PlanarFit Normalize(GameObject imported,WorldBuildCell cell=null)
        {
            var transforms=imported.GetComponentsInChildren<Transform>(true);var source=new List<PlanePoint>();var target=new List<PlanePoint>();
            foreach(var entry in new[]{("R9_Anchor_Origin",0d,0d),("R9_Anchor_X",1d,0d),("R9_Anchor_Front",0d,1d)})
            {
                var t=transforms.FirstOrDefault(p=>p.name==entry.Item1);if(t==null)continue;Vector3 p=imported.transform.parent.InverseTransformPoint(t.position);source.Add(new PlanePoint(p.x,p.z));target.Add(new PlanePoint(entry.Item2,entry.Item3));
            }
            if(source.Count<3 && cell!=null)
            {
                source.Clear();target.Clear();var parts=cell.parts.Where(p=>p.treeCenter!=null).ToArray();
                foreach(var part in parts)
                {
                    var t=transforms.FirstOrDefault(p=>p.name==part.node);var filter=t!=null?t.GetComponent<MeshFilter>():null;if(filter==null)continue;
                    Vector3 p=imported.transform.parent.InverseTransformPoint(t.TransformPoint(filter.sharedMesh.bounds.center));source.Add(new PlanePoint(p.x,p.z));target.Add(new PlanePoint(part.treeCenter[0],part.treeCenter[2]));
                }
            }
            var fit=SpatialAlignment.Solve(source.ToArray(),target.ToArray());var parent=imported.transform.parent;
            entries.Add(new Entry{model=cell!=null?cell.id:imported.name,a=fit.A,b=fit.B,c=fit.C,d=fit.D,offsetX=fit.X,offsetZ=fit.Z,error=fit.MaximumError});
            var wrapper=new GameObject("Ejes calibrados").transform;wrapper.SetParent(parent,false);imported.transform.SetParent(wrapper,true);
            Vector3 forward=new Vector3(fit.B,0,fit.D);wrapper.localRotation=Quaternion.LookRotation(forward,Vector3.up);wrapper.localScale=new Vector3(fit.A*fit.D-fit.B*fit.C,1,1);wrapper.localPosition=new Vector3((float)fit.X,0,(float)fit.Z);
            return fit;
        }
    }
}
