"""Mitigación local reversible del indexador Search. Ejecutar con Unity cerrado."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[4]
STATE = PROJECT / 'Library/Alarma/SearchRecovery'
FILES = ('Search.index', 'Search.settings')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('disable', 'restore', 'status'))
    args = parser.parse_args()
    index = PROJECT / 'UserSettings/Search.index'
    settings = PROJECT / 'UserSettings/Search.settings'
    if args.action == 'status':
        print('roots:', json.loads(index.read_text(encoding='utf-8-sig'))['roots'])
        print(next(line for line in settings.read_text().splitlines() if line.startswith('indexOnEditorStartup')))
        return
    processes = subprocess.check_output(['powershell', '-NoProfile', '-Command',
        'Get-Process Unity -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path'], text=True)
    if '\\editor\\unity.exe' in processes.lower():
        raise RuntimeError('Cerrar Unity Editor antes de cambiar sus preferencias.')
    STATE.mkdir(parents=True, exist_ok=True)
    manifest = STATE / 'last-backup.json'
    if args.action == 'restore':
        record = json.loads(manifest.read_text())
        backup = Path(record['directory']).resolve()
        assert backup.is_relative_to(STATE.resolve()), 'Respaldo fuera del directorio previsto.'
        for name in FILES:
            assert sha(backup / name) == record['hashes'][name], 'Respaldo alterado: ' + name
        for name in FILES:
            shutil.copy2(backup / name, PROJECT / 'UserSettings' / name)
        print('Preferencias originales restauradas. Abrir Unity para comprobar.')
        return
    data = json.loads(index.read_text(encoding='utf-8-sig'))
    text = settings.read_text(encoding='utf-8-sig')
    updated, count = re.subn(r'(?m)^indexOnEditorStartup\s*=\s*(true|false)\s*$',
                             'indexOnEditorStartup = false', text)
    assert count == 1, 'Se esperaba una única preferencia indexOnEditorStartup.'
    if data['roots'] == [] and updated == text:
        print('La mitigación ya está aplicada; se conserva el respaldo original.')
        return
    backup = STATE / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    backup.mkdir()
    for name in FILES:
        shutil.copy2(PROJECT / 'UserSettings' / name, backup / name)
    record = {'directory': str(backup), 'hashes': {name: sha(backup / name) for name in FILES}}
    manifest.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    data['roots'] = []
    index.write_text(json.dumps(data, indent=4) + '\n', encoding='utf-8')
    settings.write_text(updated, encoding='utf-8')
    assert json.loads(index.read_text())['roots'] == []
    assert 'indexOnEditorStartup = false' in settings.read_text()
    print('Indexado local desactivado. Respaldo:', backup)

if __name__ == '__main__':
    main()
