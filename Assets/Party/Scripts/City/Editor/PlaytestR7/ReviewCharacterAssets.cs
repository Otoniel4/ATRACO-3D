using System.IO;
using UnityEditor;
using UnityEngine;
using Alarma.AI.CityLife.Editor;
namespace Alarma.City.Playtest.Editor
{
    public static class ReviewCharacterAssets
    {
        public const string Source="Assets/Party/Art/BlenderScripts/PlaytestR9~";
        public static void Prepare(string folder,string prepared,CharacterManifest characters)
        {
            foreach(var character in characters.characters)ReviewBuildAcceptance.ValidateAnimation(folder+"/Art/Characters/"+character.id+".fbx");
            File.Copy(Source+"/city_map.png",folder+"/Art/city_map.png",true);AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var texture=(TextureImporter)AssetImporter.GetAtPath(folder+"/Art/city_map.png");texture.textureCompression=TextureImporterCompression.Uncompressed;texture.mipmapEnabled=false;texture.wrapMode=TextureWrapMode.Clamp;texture.maxTextureSize=2048;texture.SaveAndReimport();
        }
    }
}
