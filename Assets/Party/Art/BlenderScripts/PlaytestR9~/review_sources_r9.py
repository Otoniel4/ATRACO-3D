"""Encuentra las revisiones propias guardadas junto a R9 o en el proyecto."""
from pathlib import Path
import os

B = Path(__file__).resolve().parent
PROJECT = Path(os.environ.get('ALARMA_PROJECT', 'C:/Users/Alain/Atraco3D'))
RECIPES = PROJECT / 'Assets/Party/Art/BlenderScripts'

def locate(work, installed, sentinel):
    for folder in (B.parent / work, B.parent / installed, RECIPES / installed):
        if (folder / sentinel).is_file():
            return folder
    raise FileNotFoundError('Falta la fuente propia ' + installed + '/' + sentinel)

def r6(): return locate('city_life_r6', 'CityLifeR6~', 'Villa_Alarma_Compras_R6.blend')
def r7(): return locate('playtest_r7', 'PlaytestR7~', 'world.json')
def r8(): return locate('playtest_r8', 'PlaytestR8~', 'Elenco_Corregido_R8.blend')
def map1(): return locate('map4km', 'Map4Km~', 'layout.json')
def map2(): return locate('map4km_r2', 'Map4KmModernR2~', 'building_footprints_r2.json')
def plants(): return locate('planters_grass_r4', 'PlantersGrassR4~', 'Macetas_Pasto_Viento_R4.blend')
