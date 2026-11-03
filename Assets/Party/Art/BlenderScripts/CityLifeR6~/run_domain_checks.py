"""Ejecuta el dominio real C# fuera de Unity y conserva los resultados verificables."""
from pathlib import Path
import subprocess,json
B=Path(__file__).resolve().parent
result=subprocess.run(['dotnet','run','--project',str(B/'tests/DomainChecks.csproj'),'--',str(B)],capture_output=True,text=True)
(B/'domain_checks.log').write_text(result.stdout+result.stderr,encoding='utf-8');print(result.stdout,end='');assert result.returncode==0,result.stderr
report=json.loads((B/'domain_validation.json').read_text());assert report['passed'] and report['failures']==0 and report['buyers']==12
