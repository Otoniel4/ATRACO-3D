"""Datos editables de atención para los seis negocios; no abre Unity ni altera escenas."""
import json
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTY = HERE.parents[2]
PROFILE_GUID = 'c23ed4745e805050a32211f174492b7b'
PROFILES = {
    'minimarket': dict(times=[1.6,1.8,3.0,3.6,1.6,1.6],speed=1.25,smooth=.12,transfer=.3,lift=.035,inspect=.08,sweep=.10,tilt=12),
    'supermercado': dict(times=[1.6,1.8,3.2,3.6,1.6,1.6],speed=1.3,smooth=.10,transfer=.3,lift=.04,inspect=.07,sweep=.20,tilt=18),
    'joyeria': dict(times=[2.0,2.0,4.4,4.0,1.8,2.0],speed=.9,smooth=.16,transfer=.42,lift=.025,inspect=.17,sweep=.04,tilt=26),
    'banco': dict(times=[1.6,1.8,3.4,5.0,1.6,1.4],speed=1.05,smooth=.14,transfer=.35,lift=.015,inspect=.02,sweep=0,tilt=0),
    'comida': dict(times=[1.8,2.0,3.5,3.6,1.6,1.8],speed=1.05,smooth=.15,transfer=.4,lift=.025,inspect=.05,sweep=.03,tilt=0),
    'ropa': dict(times=[1.8,2.0,4.0,3.6,1.6,1.8],speed=1.05,smooth=.14,transfer=.38,lift=.03,inspect=.09,sweep=.14,tilt=5),
}

def guid(name): return uuid.uuid5(uuid.NAMESPACE_URL, 'Alarma/ShopAnimation39/' + name).hex
def meta(path, kind='asset'):
    extra = 'folderAsset: yes\n' if kind == 'folder' else ''
    Path(str(path)+'.meta').write_text(f'fileFormatVersion: 2\nguid: {guid(path.name)}\n{extra}', encoding='utf-8')

if __name__ == '__main__':
    directory = PARTY/'Data/ShopAnimations'
    directory.mkdir(parents=True, exist_ok=True)
    meta(directory,'folder')
    for name,p in PROFILES.items():
        path=directory/(name+'.asset')
        if path.exists(): raise RuntimeError(f'No se sobrescriben ajustes existentes: {path}')
        fields=dict(HandSpeed=p['speed'],HandSmoothing=p['smooth'],TransferSeconds=p['transfer'],TransferLift=p['lift'],
                    InspectionLift=p['inspect'],InspectionSweep=p['sweep'],InspectionTilt=p['tilt'],GripHeight=0)
        text='%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\nMonoBehaviour:\n'
        text+='  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n  m_GameObject: {fileID: 0}\n  m_Enabled: 1\n  m_EditorHideFlags: 0\n'
        text+=f'  m_Script: {{fileID: 11500000, guid: {PROFILE_GUID}, type: 3}}\n  m_Name: {name}\n  m_EditorClassIdentifier: \n  Timing:\n'
        text+=''.join(f'    {field}: {value}\n' for field,value in zip(['Pick','Place','Scan','Pay','Change','Bag'],p['times']))
        text+=''.join(f'  {field}: {value}\n' for field,value in fields.items())
        if name=='joyeria': text+='  ProductParts:\n  - Ring\n  - Gem\n'
        path.write_text(text, encoding='utf-8');meta(path)
    (HERE/'profiles.json').write_text(json.dumps(PROFILES,indent=2)+'\n',encoding='utf-8')
    print('Creados 6 perfiles; tiempos y trayectorias por negocio.')
