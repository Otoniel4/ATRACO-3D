"""Reimporta suelo, sector comercial y puertas. Contrasta nombres, límites y máscaras con los metadatos."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;world=json.loads((B/'world.json').read_text(encoding='utf-8'));report=[]
for identifier in ['Globals','Cell_07_06','Cell_07_07','Wide_R2_CorporatePublicSpace_Sector_04_04']:
    row=next(c for c in world['cells'] if c['id']==identifier);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export'/row['file']))
    lookup={o.name:o for o in bpy.context.scene.objects};missing=[p['node'] for p in row['parts'] if p['node'] not in lookup];assert not missing,(identifier,missing[:4])
    masks=sum(bool(o.data.color_attributes.get('WindMask')) for o in bpy.context.scene.objects if o.type=='MESH');expected=sum(p['wind'] for p in row['parts']);assert masks==expected,(identifier,masks,expected)
    low=[math.inf]*3;high=[-math.inf]*3
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        for corner in obj.bound_box:
            p=obj.matrix_world@Vector(corner)
            for i in range(3):low[i]=min(low[i],p[i]);high[i]=max(high[i],p[i])
    # La importación vuelve a Z arriba; los metadatos de juego usan Y arriba.
    o=row['origin'];c=row['center'];size=row['size'];origin=[o[0],-o[2],o[1]];center=[c[0],-c[2],c[1]];extent=[size[0]/2,size[2]/2,size[1]/2]
    assert all(abs(low[i]+origin[i]-(center[i]-extent[i]))<1 and abs(high[i]+origin[i]-(center[i]+extent[i]))<1 for i in range(3)),(identifier,low,high)
    report.append({'id':identifier,'objects':len(row['parts']),'masks':masks,'bounds_match':True});print('FBX_PART_VERIFIED',identifier,flush=True)
for door in world['doors']:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B/'export'/door['file']));objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert objects and all(o.parent is None or o.parent.type in ['EMPTY','MESH'] for o in objects)
    points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];height=max(p.z for p in points)-min(p.z for p in points);assert 2<height<4.5,(door['id'],height)
(B/'fbx_validation.json').write_text(json.dumps({'passed':True,'sampled_parts':report,'doors':9,'geometry_units_verified':True},indent=2));print('PLAYTEST_FBX_VALIDATED',flush=True)
