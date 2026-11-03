from pathlib import Path
B=Path(__file__).resolve().parent
PARTY=Path('C:/Users/Alain/Atraco3D/Assets/Party/Art/BlenderScripts')
def location(work,installed,filename):
    for path in [B.parent/work,B.parent/installed,PARTY/installed]:
        if (path/filename).is_file():return path
    raise FileNotFoundError('Falta una entrega propia necesaria: '+installed+'/'+filename)
def r6():return location('city_life_r6','CityLifeR6~','Elenco_Animado_R6.blend')
def r7():return location('playtest_r7','PlaytestR7~','world.json')
def map1():return location('map4km','Map4Km~','layout.json')
def map2():return location('map4km_r2','Map4KmModernR2~','building_footprints_r2.json')
