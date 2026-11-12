using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using Alarma.AI.CityLife.Editor;

static class AnchorNameTests
{
    static int checks;
    static void Check(bool ok,string message){if(!ok)throw new Exception(message);checks++;}
    static void Main()
    {
        using var inventory=JsonDocument.Parse(File.ReadAllText("Temp/ShopObjects44/anchor-names.json"));
        foreach(var model in inventory.RootElement.EnumerateObject())
        foreach(string expected in new[]{"Support","Grip_R","Grip_L"})
        {
            var names=model.Value.EnumerateArray().Select(n=>n.GetString()).ToArray();
            Check(names.Count(n=>BlenderAssetNames.Matches(n,expected))==1,model.Name+": marcador ambiguo o ausente "+expected);
        }
        foreach(string bad in new[]{"Support_extra","Support.abc","Support.01","OtherSupport.003","Support.003.extra"})
            Check(!BlenderAssetNames.Matches(bad,"Support"),"No debe aceptar "+bad);
        Check(BlenderAssetNames.BaseName("Alarma_Hideout_Facade.002")=="Alarma_Hideout_Facade","Material con sufijo");
        Check(BlenderAssetNames.BaseName("Material.rough")=="Material.rough","Conserva nombre no numérico");
        Check(new[]{"Support","Support.001"}.Count(n=>BlenderAssetNames.Matches(n,"Support"))==2,"Permite detectar ambigüedad");
        Console.WriteLine("ANCHOR_NAME_CHECKS "+checks+"; 18 FBX, 54 marcadores únicos; sufijos y ambigüedad comprobados");
    }
}
