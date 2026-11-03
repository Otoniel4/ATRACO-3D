"""Ubica las entregas propias anteriores sin rutas absolutas del taller."""
from pathlib import Path
def revision(number):
    names={6:['city_life_r6','CityLifeR6~','Alarma-Ciudad-Compras-R6'],5:['city_life_r5','CityLifeR5~','Alarma-Ciudad-Viva-R5']}
    for name in names[number]:
        path=Path(__file__).resolve().parent.parent/name
        if path.is_dir():return path
    raise FileNotFoundError('Conserva la revisión propia R'+str(number)+' como carpeta hermana.')
