"""Materiales y shader listos para copiar a Party. No abre Unity ni modifica escenas existentes."""
from pathlib import Path
import json,shutil,uuid,re
BASE=Path(__file__).resolve().parent;C=json.loads((BASE/'settings.json').read_text(encoding='utf-8'))
OUT=BASE/'Unity';(OUT/'Materials').mkdir(parents=True,exist_ok=True)
shader=OUT/'TreeWindURP.shader';shutil.copy2(BASE/'TreeWindURP.shader',shader)
guid=uuid.uuid5(uuid.NAMESPACE_URL,'Alarma/Vegetation/NaturalWindR3').hex
shader.with_suffix('.shader.meta').write_text(f'fileFormatVersion: 2\nguid: {guid}\nShaderImporter:\n  externalObjects: {{}}\n  defaultTextures: []\n  nonModifiableTextures: []\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n',encoding='utf-8')
for name,value in C['palette'].items():
    rgb=[int(value[i:i+2],16)/255 for i in [0,2,4]];matname='WindTree_'+name
    floats={'_WindStrength':C['wind_strength'],'_WindSpeed':C['wind_speed'],'_WindPeriod':C['loop_seconds'],
        '_PrimaryAmplitude':C['primary_amplitude_m'],'_BranchAmplitude':C['branch_amplitude_m'],
        '_LeafAmplitude':C['leaf_amplitude_m'],'_LeafVerticalAmplitude':C['leaf_vertical_amplitude_m']}
    text='%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n'
    text+=f'  serializedVersion: 8\n  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {{fileID: 0}}\n  m_PrefabInstance: {{fileID: 0}}\n  m_PrefabAsset: {{fileID: 0}}\n  m_Name: {matname}\n'
    text+=f'  m_Shader: {{fileID: 4800000, guid: {guid}, type: 3}}\n  m_Parent: {{fileID: 0}}\n  m_ModifiedSerializedProperties: 0\n  m_ValidKeywords: []\n  m_InvalidKeywords: []\n  m_LightmapFlags: 4\n  m_EnableInstancingVariants: 1\n  m_DoubleSidedGI: 1\n  m_CustomRenderQueue: -1\n  stringTagMap: {{}}\n  disabledShaderPasses: []\n  m_LockedProperties: \n  m_SavedProperties:\n    serializedVersion: 3\n    m_TexEnvs: []\n    m_Ints: []\n    m_Floats:\n'
    text+=''.join(f'    - {k}: {v}\n' for k,v in floats.items())
    text+=f'    m_Colors:\n    - _BaseColor: {{r: {rgb[0]}, g: {rgb[1]}, b: {rgb[2]}, a: 1}}\n    - _WindDirection: {{r: 0.93, g: 0, b: 0.35, a: 0}}\n  m_BuildTextureStacks: []\n'
    path=OUT/'Materials'/(matname+'.mat');path.write_text(text,encoding='utf-8')
    matguid=uuid.uuid5(uuid.NAMESPACE_URL,'Alarma/Vegetation/R3/'+matname).hex
    path.with_suffix('.mat.meta').write_text(f'fileFormatVersion: 2\nguid: {matguid}\nNativeFormatImporter:\n  externalObjects: {{}}\n  mainObjectFileID: 2100000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n',encoding='utf-8')
# Se comprueban los includes reales del paquete instalado, sin simular una compilación de Unity.
cache=Path('C:/Users/Alain/Atraco3D/Library/PackageCache');source=shader.read_text(encoding='utf-8');checked=[]
for include in re.findall(r'#include "([^"]+)"',source):
    _,package,relative=include.split('/',2);candidates=list(cache.glob(package+'@*'));found=any((p/relative).is_file() for p in candidates)
    assert found,include;checked.append(include)
for token in ['ApplyShadowClamping','GetAdditionalLight','GetMainLight','PackNormalOctQuadEncode']:
    assert any(token in p.read_text(encoding='utf-8',errors='ignore') for d in cache.glob('com.unity.render-pipelines.*@*') for p in d.glob('ShaderLibrary/*.hlsl')),token
(BASE/'unity_static_validation.json').write_text(json.dumps({'includes_found':checked,'material_count':len(C['palette']),
    'shader_compiled_in_unity':False,'game_verified':False,'note':'Compilation, imported vertex colors and rendering must be checked by Alain in Unity 6000.3.27f2.'},indent=2),encoding='utf-8')
print('UNITY_WIND_FILES_PREPARED',len(C['palette']),'materials; Unity compilation pending')
