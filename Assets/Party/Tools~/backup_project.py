"""Respaldo portátil del proyecto guardado; no abre Unity ni altera modelos.

snapshot: comprime fuentes demasiado grandes y actualiza el manifiesto.
verify: comprueba todos los archivos y el contenido original de los ZIP.
restore: recupera las fuentes comprimidas y comprueba el respaldo completo.
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Assets/Party/Tools~/backup-manifest.json"
CITY_OUTPUT = "Assets/Party/Generated/Ciudad2km"
SCENE = CITY_OUTPUT + "/Scenes/Ciudad_2km.unity"
LIMIT = 100 * 1024 * 1024
PART_SIZE = 48 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or path == ROOT:
        raise ValueError("Ruta fuera del proyecto: " + relative)
    return path


def record(path):
    data = path.read_bytes()
    # Git puede convertir CRLF en archivos de texto; los binarios nunca se normalizan.
    binary = {".unity", ".blend", ".fbx", ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".wav", ".mp3", ".ogg", ".psd", ".tga", ".exr", ".zip"}
    normalized = path.suffix.lower() not in binary and b"\0" not in data[:8192]
    if normalized:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            normalized = False
    canonical = data.replace(b"\r\n", b"\n") if normalized else data
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data),
                sha256=digest(canonical), normalize_crlf=normalized)


def current_scene():
    report_path = local_path(CITY_OUTPUT + "/BuildReport.json")
    if not report_path.is_file():
        return SCENE
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    scene = report.get("scene", "")
    revision = re.fullmatch(re.escape(CITY_OUTPUT) + r"/Revisiones/R_[0-9a-f]{32}/Scenes/Ciudad_2km\.unity", scene)
    if not report.get("complete") or (scene != SCENE and revision is None) or not local_path(scene).is_file():
        raise ValueError("El informe de ciudad no apunta a una escena publicada.")
    return scene


def snapshot():
    scene = current_scene()
    archives = []
    for source in sorted((ROOT / "Assets/Party/Art").rglob("*.blend")):
        if source.stat().st_size <= LIMIT:
            continue
        archive = source.with_name(source.name + ".zip")
        temporary = archive.with_suffix(".zip.tmp")
        try:
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
                bundle.write(source, source.name)
            with zipfile.ZipFile(temporary) as bundle:
                if digest(bundle.read(source.name)) != digest(source.read_bytes()):
                    raise ValueError("El ZIP no conserva la fuente: " + str(source))
            parts = []
            with temporary.open("rb") as stream:
                while block := stream.read(PART_SIZE):
                    part = archive.with_name(archive.name + f".part{len(parts) + 1:02d}")
                    part_temp = part.with_name(part.name + ".tmp")
                    part_temp.write_bytes(block)
                    part_temp.replace(part)
                    parts.append(part.relative_to(ROOT).as_posix())
            zip_hash = digest(temporary.read_bytes())
            assert digest(b"".join(local_path(p).read_bytes() for p in parts)) == zip_hash
            # Retirar solo fragmentos sobrantes de una versión anterior del mismo archivo.
            for previous in source.parent.glob(archive.name + ".part[0-9][0-9]"):
                if previous.relative_to(ROOT).as_posix() not in parts:
                    previous.unlink()
        finally:
            if temporary.exists():
                temporary.unlink()
        archives.append(dict(parts=parts, zip_sha256=zip_hash,
                             target=source.relative_to(ROOT).as_posix(), entry=source.name,
                             sha256=digest(source.read_bytes()), bytes=source.stat().st_size))
    output = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT)
    files = []
    for relative in sorted(set(output.decode("utf-8").split("\0"))):
        if not relative or relative == MANIFEST.relative_to(ROOT).as_posix():
            continue
        path = local_path(relative)
        if not path.is_file():
            continue
        if path.stat().st_size >= LIMIT:
            raise ValueError("Archivo que GitHub no aceptará: " + relative)
        files.append(record(path))
    if not any(entry["path"] == scene for entry in files):
        raise ValueError("La escena publicada no está incluida en el inventario: " + scene)
    contents = dict(format=1, scene=scene, unity="6000.3.27f2", archives=archives, files=files)
    MANIFEST.write_text(json.dumps(contents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(files=len(files), archives=archives, total_bytes=sum(f["bytes"] for f in files)), ensure_ascii=False))


def verify(restore=False):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    errors = []
    for entry in manifest["archives"]:
        target = local_path(entry["target"])
        try:
            zipped = b"".join(local_path(p).read_bytes() for p in entry["parts"])
            if digest(zipped) != entry["zip_sha256"]:
                raise ValueError("Fragmentos ZIP alterados")
            with zipfile.ZipFile(io.BytesIO(zipped)) as bundle:
                if bundle.namelist() != [entry["entry"]]:
                    raise ValueError("Contenido ZIP inesperado")
                data = bundle.read(entry["entry"])
            if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
                raise ValueError("Fuente comprimida alterada")
            if restore and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(data)
            if target.exists() and digest(target.read_bytes()) != entry["sha256"]:
                raise ValueError("La fuente local es distinta; se conserva sin sobrescribir")
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            errors.append(entry["target"] + ": " + str(error))
    for entry in manifest["files"]:
        path = local_path(entry["path"])
        if not path.is_file():
            errors.append("Falta " + entry["path"])
            continue
        data = path.read_bytes()
        if entry["normalize_crlf"]:
            data = data.replace(b"\r\n", b"\n")
        if digest(data) != entry["sha256"]:
            errors.append("Contenido distinto: " + entry["path"])
    if errors:
        raise SystemExit("\n".join(errors))
    print(json.dumps(dict(verified_files=len(manifest["files"]), verified_archives=len(manifest["archives"]),
                          scene_sha256=digest(local_path(manifest["scene"]).read_bytes())), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["snapshot", "verify", "restore"])
    action = parser.parse_args().action
    if action == "snapshot":
        snapshot()
    else:
        verify(restore=action == "restore")
