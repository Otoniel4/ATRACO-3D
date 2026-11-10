"""Comprueba la identidad de assets antes de compilar; no necesita abrir Unity."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTY = HERE.parents[2]

def valid_guid(value):
    return re.fullmatch(r'[0-9a-fA-F]{32}', value) is not None

def validate():
    # Regresión: el identificador anterior de 33 caracteres hacía que Unity ignorase el script.
    assert not valid_guid('b95cc68466db44be8acf962a310b429d4')
    assert valid_guid('0123456789abcdef0123456789abcdef')
    identities = {}
    for path in PARTY.rglob('*.meta'):
        text = path.read_text(encoding='utf-8-sig')
        matches = re.findall(r'^guid:\s*([^\r\n]+)', text, re.M)
        assert len(matches) == 1 and valid_guid(matches[0]), f'Meta inválido: {path}'
        guid = matches[0].lower()
        assert guid not in identities, f'GUID duplicado: {path} y {identities.get(guid)}'
        identities[guid] = path
    script = PARTY/'Scripts/AI/CityLifeR5/ShopAnimationProfile.cs.meta'
    guid = re.search(r'^guid: (\w+)', script.read_text(), re.M)[1]
    profiles = list((PARTY/'Data/ShopAnimations').glob('*.asset'))
    assert len(profiles) == 6
    for profile in profiles:
        reference = re.search(r'm_Script: \{fileID: 11500000, guid: (\w+), type: 3\}', profile.read_text())
        assert reference and reference[1] == guid, f'Perfil sin script válido: {profile}'
    generator = (HERE/'create_profiles.py').read_text(encoding='utf-8')
    assert f"PROFILE_GUID = '{guid}'" in generator, 'La receta debe conservar el mismo GUID.'
    result = dict(valid_metadata=len(identities), profiles_linked=len(profiles), profile_guid=guid,
                  previous_invalid_guid_rejected=True, unity_opened_by_agent=False)
    (HERE/'metadata-results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('METADATA_VALID', len(identities), 'PROFILES_LINKED', len(profiles))
    return result

if __name__ == '__main__':
    validate()
