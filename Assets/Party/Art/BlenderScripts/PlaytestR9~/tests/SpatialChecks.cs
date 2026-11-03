using System;
using Alarma.City.Playtest;
static class SpatialChecks
{
    public static void Run()
    {
        var source=new[]{new PlanePoint(0,0),new PlanePoint(1,0),new PlanePoint(0,1),new PlanePoint(-120,93)};
        int[,] maps={{1,0,0,1},{1,0,0,-1},{-1,0,0,1},{-1,0,0,-1},{0,1,1,0},{0,1,-1,0},{0,-1,1,0},{0,-1,-1,0}};
        for(int i=0;i<8;i++)
        {
            var actual=new PlanePoint[source.Length];for(int n=0;n<source.Length;n++)actual[n]=new PlanePoint(maps[i,0]*source[n].X+maps[i,1]*source[n].Z+14,maps[i,2]*source[n].X+maps[i,3]*source[n].Z-8);
            var fit=SpatialAlignment.Solve(actual,source);for(int n=0;n<source.Length;n++){var p=fit.Apply(actual[n]);if(Math.Abs(p.X-source[n].X)+Math.Abs(p.Z-source[n].Z)>.00001)throw new Exception("Fallo de calibración de ejes "+i);}
        }
        bool rejected=false;try{SpatialAlignment.Solve(source,new[]{source[0],new PlanePoint(10,0),source[2],source[3]});}catch(InvalidOperationException){rejected=true;}
        if(!rejected)throw new Exception("Se aceptaron puertas con anclas incoherentes.");Console.WriteLine("PASS: ocho orientaciones FBX y rechazo de anclas incoherentes.");
    }
}
