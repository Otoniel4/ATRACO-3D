"""Resuelve nuestra revisión anterior tanto en el taller como en las dos ubicaciones de entrega."""
from pathlib import Path
def previous_revision():
    parent=Path(__file__).resolve().parent.parent
    for name in ['city_life_r5','CityLifeR5~','Alarma-Ciudad-Viva-R5']:
        candidate=parent/name
        if (candidate/'baseline/Cast_R3.blend').is_file():return candidate
    raise FileNotFoundError('Conserva la entrega propia R5 como carpeta hermana: CityLifeR5~ o Alarma-Ciudad-Viva-R5. No se descargan recursos externos.')
