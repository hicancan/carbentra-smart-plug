"""Narrow redacted pre-publication credential check. Never prints matched values.
This is not a guarantee that all possible secrets/private information are absent.
PEM checks require a complete key-like block; NUL-terminated parser labels in TLS
libraries are not credentials.
"""
from pathlib import Path
import subprocess,re,json,sys
R=Path(__file__).resolve().parents[1]
patterns={
 'github_fine_grained_token':re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'),
 'github_classic_or_oauth_token':re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
 'private_key_pem':re.compile(rb'-----BEGIN ((?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY)-----(?:\r?\n|\\n)[^\x00]{64,16384}?-----END \1-----'),
 'aws_access_key_id':re.compile(rb'AKIA[0-9A-Z]{16}')}
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
findings=[];checked=0
# Inspect all reachable historical objects, not only the working tree.
objects={line.split(b' ',1)[0]:line.split(b' ',1)[1].decode('utf-8','replace') if b' ' in line else '' for line in git('rev-list','--objects','--all').splitlines()}
p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for oid,path in objects.items():
 p.stdin.write(oid+b'\n');p.stdin.flush();header=p.stdout.readline().split()
 if len(header)!=3:raise RuntimeError('Unexpected git object response')
 size=int(header[2]);data=p.stdout.read(size);p.stdout.read(1)
 if header[1]!=b'blob':continue
 checked+=1
 for label,pattern in patterns.items():
  if pattern.search(data):findings.append({'scope':'reachable_git_history','path':path,'object':oid.decode(),'kind':label})
p.stdin.close();p.wait()
# Include existing working files that may be staged for the next snapshot.
paths=set(git('ls-files','-z').split(b'\0')+git('ls-files','--others','--exclude-standard','-z').split(b'\0'))
for raw in sorted(paths):
 if not raw:continue
 rel=raw.decode('utf-8','replace');f=R/rel
 if not f.is_file() or f.is_symlink():continue
 checked+=1;data=f.read_bytes()
 for label,pattern in patterns.items():
  if pattern.search(data):findings.append({'scope':'working_tree','path':rel,'kind':label})
result={'status':'PASS' if not findings else 'BLOCKED','objects_and_files_checked':checked,'scope':'Known credential patterns only; matched values are never recorded','findings':findings}
(R/'release').mkdir(exist_ok=True);(R/'release/publish_hygiene.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(1 if findings else 0)
