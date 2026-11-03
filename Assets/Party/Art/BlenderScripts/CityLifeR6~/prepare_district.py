from pathlib import Path
import json
B=Path(__file__).resolve().parent;from sources import previous_revision;old=previous_revision()
script=(old/'build_district.py').read_text(encoding='utf-8')
script=script.replace("BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))","BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE));from sources import previous_revision;OLD=previous_revision()")
for filename in ['prop_catalog.json','interior_placements.json','Objetos_Locales_R5.blend','baseline/City_Plants_R4.blend']:script=script.replace("BASE/'"+filename+"'","OLD/'"+filename+"'")
script=script.replace('Clothing','MallJewelry').replace('LifeR5','LifeR6').replace('CityLifeR5','CityLifeR6').replace('Distrito_Comercial_R5','Distrito_Comercial_R6').replace('Calle_Comercial_R5','Calle_Comercial_R6')
# Las rutas finales se calibran despuÃ©s de crear los obstÃ¡culos reales.
script=script.replace("for serial,item in enumerate(placements[shop]):","for serial,item in enumerate(placements[shop]):\n        if shop=='MallJewelry' and item['asset']=='JewelryCase' and item['position_blender'][:2]==[0,2.5]:continue # libera el acceso a caja")
(B/'build_district.py').write_text(script,encoding='utf-8')
print('DISTRICT_RECIPE_READY')
