using System;
namespace Alarma.City.Playtest
{
    public readonly struct PlanePoint
    {
        public readonly double X,Z;
        public PlanePoint(double x,double z){X=x;Z=z;}
    }
    public readonly struct PlanarFit
    {
        public readonly int A,B,C,D;
        public readonly double X,Z,MaximumError;
        public PlanarFit(int a,int b,int c,int d,double x,double z,double error){A=a;B=b;C=c;D=d;X=x;Z=z;MaximumError=error;}
        public PlanePoint Apply(PlanePoint p)=>new PlanePoint(A*p.X+B*p.Z+X,C*p.X+D*p.Z+Z);
    }
    public static class SpatialAlignment
    {
        // Calibra ejes/reflejos con correspondencias geométricas; no presupone cómo importó Unity el FBX.
        public static PlanarFit Solve(PlanePoint[] imported,PlanePoint[] expected,double tolerance=.025)
        {
            if(imported.Length!=expected.Length || imported.Length<3)throw new ArgumentException("Se requieren tres anclas de posición.");
            int[,] variants={{1,0,0,1},{1,0,0,-1},{-1,0,0,1},{-1,0,0,-1},{0,1,1,0},{0,1,-1,0},{0,-1,1,0},{0,-1,-1,0}};
            PlanarFit best=default;double bestError=double.PositiveInfinity;
            for(int v=0;v<8;v++)
            {
                int a=variants[v,0],b=variants[v,1],c=variants[v,2],d=variants[v,3];double x=0,z=0;
                for(int i=0;i<imported.Length;i++){x+=expected[i].X-a*imported[i].X-b*imported[i].Z;z+=expected[i].Z-c*imported[i].X-d*imported[i].Z;}x/=imported.Length;z/=imported.Length;
                double error=0;for(int i=0;i<imported.Length;i++)error=Math.Max(error,Math.Sqrt(Math.Pow(a*imported[i].X+b*imported[i].Z+x-expected[i].X,2)+Math.Pow(c*imported[i].X+d*imported[i].Z+z-expected[i].Z,2)));
                if(error<bestError){bestError=error;best=new PlanarFit(a,b,c,d,x,z,error);}
            }
            if(best.MaximumError>tolerance)throw new InvalidOperationException("Las mallas y las anclas no coinciden: "+best.MaximumError.ToString("0.000")+" m.");
            return best;
        }
    }
}
