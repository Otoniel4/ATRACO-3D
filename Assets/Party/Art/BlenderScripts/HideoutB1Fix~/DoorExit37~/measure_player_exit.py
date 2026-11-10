"""Mide las distancias de acercamiento con los cuatro FBX reales y la palma orientada."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
original=HERE.parent/'DoorReview36~/verify_contacts.py'
source=original.read_text(encoding='utf-8')
source=source.replace("glob('NPC*.fbx')", "glob('Player*.fbx')")
source=source.replace("for height,cell in itertools.product((1.18,1.28),(-.5,0,.5))", "for height,distance_to_door in itertools.product((1.15,1.19,1.28),(.475,.425,.4,.38,.35))")
start=source.index('            contact_x=')
end=source.index('            # Misma',start)
source=source[:start]+'''            lateral=pos('UpperArm.R').dot(right)
            target=right*lateral+forward*(distance_to_door-.035)+up*height
'''+source[end:]
source=source.replace("'arrival_column':cell", "'distance_to_door':distance_to_door")
source=source[:source.index('maximum=max')]+'''
for distance in (.475,.425,.4,.38,.35):
    group=[r for r in results if r['distance_to_door']==distance]
    print('feet_distance',distance,'cases',len(group),'max_error',max(r['error_m'] for r in group))
assert len(results)==180
assert max(r['error_m'] for r in results if r['distance_to_door']==.475)>.035
assert max(r['error_m'] for r in results if r['distance_to_door']==.35)<.008
'''
exec(compile(source,str(original),'exec'),{'__file__':str(HERE/'measure_player_exit.py'),'__name__':'__main__'})
