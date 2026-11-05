from pathlib import Path
import hashlib
import subprocess

folder = Path(__file__).resolve().parent
root = folder.parents[6]
source = root / "Assets/Party/Scripts/AI/CityLifeR5/ShopDoor.cs"
out = root / "Temp/ShopDoorRegressionReplay"
out.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
dotnet = Path("C:/Program Files/dotnet/dotnet.exe")
csc = Path("C:/Program Files/dotnet/sdk/10.0.402/Roslyn/bincore/csc.dll")
ref = Path("C:/Program Files/dotnet/packs/Microsoft.NETCore.App.Ref/10.0.13/ref/net10.0")
exe = out / "ShopDoorRegression.dll"
rsp = out / "compile.rsp"
rsp.write_text("\n".join(["/nologo", "/target:exe", f'/out:"{exe}"']
                         + [f'/r:"{p}"' for p in sorted(ref.glob("*.dll"))]
                         + [f'"{p}"' for p in (source, folder / "UnityStubs.cs", folder / "Regression.cs")]))
(out / "ShopDoorRegression.runtimeconfig.json").write_text(
    '{"runtimeOptions":{"tfm":"net10.0","framework":{"name":"Microsoft.NETCore.App","version":"10.0.13"}}}')
subprocess.run([str(dotnet), str(csc), "@" + str(rsp)], check=True)
run = subprocess.run([str(dotnet), str(exe)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     encoding="utf-8", errors="replace")
results = run.stdout + "ShopDoor.cs SHA-256 " + source_hash + "\n"
print(results, end="")
(folder / "results.txt").write_text(results, encoding="utf-8")
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash, "ShopDoor.cs cambió mientras se ejecutaba"
run.check_returncode()
