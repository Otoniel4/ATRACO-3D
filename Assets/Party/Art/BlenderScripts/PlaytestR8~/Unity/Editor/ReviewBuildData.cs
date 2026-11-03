using System;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    [Serializable] public sealed class WorldBuildPart
    {
        public string node,source,role;
        public int collision;
        public float[] treeCenter;
        public float radius,height;
        public bool heroRoof,wind;
    }
    [Serializable] public sealed class WorldBuildCell
    {
        public string id,file;
        public float[] origin,center,size;
        public bool always;
        public WorldBuildPart[] parts;
    }
    [Serializable] public sealed class WorldBuildLeaf {public float[] position;public float yaw;}
    [Serializable] public sealed class WorldBuildDoor {public string id,file;public bool single;public WorldBuildLeaf[] leaves;public float[] threshold;}
    [Serializable] public sealed class WorldBuildNode {public float[] v;public int[] links;}
    [Serializable] public sealed class WorldBuildShop
    {
        public string id,product;public int priceCents,staffVariant;public float staffYaw;
        public float[] origin,staff,staffWorld,counter,scan,receipt,till;
        public PointData[] walk,entry,queue,exit,browseStations,products;
        public WorldBuildNode[] nodes;
    }
    [Serializable] public sealed class WorldBuildDestination {public string id,label;public float[] position;public float yaw;}
    [Serializable] public sealed class WorldBuildData
    {
        public string version;public float[] worldSize;
        public WorldBuildCell[] cells;public WorldBuildDoor[] doors;public WorldBuildShop[] shops;public WorldBuildDestination[] pois;
    }
    [Serializable] public sealed class ReviewBuildRecord
    {
        public bool complete;public string version,scene,folder,assetFolder,error;
        public int worldParts,characters,models,shops;
    }
}
