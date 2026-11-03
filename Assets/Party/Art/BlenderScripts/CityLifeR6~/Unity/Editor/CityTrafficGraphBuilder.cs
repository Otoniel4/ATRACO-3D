using System;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using Unity.AI.Navigation;
namespace Alarma.AI.CityLife.Editor
{
    public static class CityTrafficGraphBuilder
    {
        public static void Bake(NavMeshSurface surface,Transform root)
        {
            var settings=NavMesh.GetSettingsByID(surface.agentTypeID);settings.agentRadius=.24f;settings.agentHeight=1.9f;settings.overrideVoxelSize=true;settings.voxelSize=.055f;
            var sources=new List<NavMeshBuildSource>();NavMeshBuilder.CollectSources(root,~0,NavMeshCollectGeometry.PhysicsColliders,0,new List<NavMeshBuildMarkup>(),sources);
            surface.navMeshData=NavMeshBuilder.BuildNavMeshData(settings,sources,new Bounds(new Vector3(0,2,2),new Vector3(80,12,30)),Vector3.zero,Quaternion.identity);surface.AddData();
        }
        public static TrafficGraph Create()
        {
            const float pitch=.7f;var cells=new List<TrafficCell>();var ids=new Dictionary<Vector2Int,int>();
            for(int y=0;y<21;y++)for(int x=0;x<103;x++)
            {
                Vector3 p=new Vector3(-35.7f+x*pitch,.16f,9.1f-y*pitch);
                if(!NavMesh.SamplePosition(p,out var hit,.13f,NavMesh.AllAreas) || new Vector2(hit.position.x-p.x,hit.position.z-p.z).sqrMagnitude>.0009f)continue;
                ids[new Vector2Int(x,y)]=cells.Count;cells.Add(new TrafficCell{Position=hit.position});
            }
            foreach(var pair in ids)
            {
                var links=new List<int>();foreach(var offset in new[]{Vector2Int.up,Vector2Int.down,Vector2Int.left,Vector2Int.right})
                    if(ids.TryGetValue(pair.Key+offset,out int i) && !NavMesh.Raycast(cells[pair.Value].Position,cells[i].Position,out var hit,NavMesh.AllAreas))links.Add(i);
                cells[pair.Value].Links=links.ToArray();
            }
            if(cells.Count<300)throw new InvalidOperationException("Grafo peatonal incompleto: revisar NavMesh y altura de suelo.");
            var graph=ScriptableObject.CreateInstance<TrafficGraph>();graph.Cells=cells.ToArray();return graph;
        }
        public static void Validate(TrafficGraph graph,IEnumerable<Transform> positions)
        {
            var indices=new HashSet<int>();foreach(var marker in positions)
            {
                int cell=graph.Nearest(marker.position,.55f);if(cell<0 || !indices.Add(cell))throw new InvalidOperationException("Puesto inaccesible o compartido en el grafo: "+marker.parent.name+"/"+marker.name);
            }
        }
        public static void ValidateRoutes(TrafficGraph graph,Transform origin,IEnumerable<Transform> positions)
        {
            int start=graph.Nearest(origin.position,.55f);var traffic=new PedestrianTraffic(graph);
            if(start<0 || !traffic.TryAdd(-1,start))throw new InvalidOperationException("Entrada fuera del grafo peatonal.");
            foreach(var marker in positions)
            {
                int cell=graph.Nearest(marker.position,.55f);
                if(cell<0 || !traffic.SetGoal(-1,cell))throw new InvalidOperationException("Ruta desconectada en el grafo: "+marker.parent.name+"/"+marker.name);
            }
        }
    }
}
