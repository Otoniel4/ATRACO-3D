from pathlib import Path
import subprocess,json,re
BASE=Path(__file__).resolve().parent
result=subprocess.run(['dotnet','run','--project',str(BASE/'tests/DomainChecks.csproj'),'--configfile',str(BASE/'tests/NuGet.Config')],capture_output=True,text=True)
(BASE/'domain_checks.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stdout+result.stderr
match=re.search(r'DOMAIN_CHECKS_PASSED (\d+)',result.stdout);assert match
(BASE/'domain_validation.json').write_text(json.dumps({'assertions_passed':int(match[1]),'framework':'.NET 10, no Unity engine execution','passed':True},indent=2),encoding='utf-8')
print(result.stdout.strip())
