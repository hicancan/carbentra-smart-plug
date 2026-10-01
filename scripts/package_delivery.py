"""Create auditable delivery archives from tracked Git files, never local credentials.
Run after final commit and passing digital checks. Outputs live outside repository.
Large archives receive SHA-256 verified 20 MiB chunks plus Windows join script.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
R=Path(__file__).resolve().parents[1]
CHUNK=20*1024*1024

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def chunks(p):
 result=[]
 if p.stat().st_size<=CHUNK:return result
 with p.open('rb') as f:
  i=1
  while b:=f.read(CHUNK):
   part=p.with_name(p.name+f'.part{i:03}')
   part.write_bytes(b);result.append({'name':part.name,'bytes':len(b),'sha256':digest(part)});i+=1
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
 out=Path(a.output).resolve()
 if out==R or R in out.parents:raise SystemExit('Output must be outside the Git repository')
 report=json.loads((R/'release/digital_checks_rev_b.json').read_text(encoding='utf-8'))
 if not report.get('passed'):raise SystemExit('Final digital checks have not passed')
 dirty=subprocess.check_output(['git','status','--porcelain'],cwd=R,text=True)
 if dirty.strip():raise SystemExit('Commit final project changes before packaging')
 out.mkdir(parents=True,exist_ok=True)
 paths=[Path(x.decode()) for x in subprocess.check_output(['git','ls-files','-z'],cwd=R).split(b'\0') if x]
 groups={
  'CARBENTRA_RevB_Engineering.zip':lambda p: str(p).startswith(('mechanical/rev_b/','electronics/rev_b/','firmware/','edge/','docs/','tests/','scripts/','assets/')) or str(p) in ['README.md','release/START_HERE.md','release/digital_checks_rev_b.json','release/firmware_evidence_checks.json','release/light_glb_import_check.json','release/review_pdf_qa.json','release/publish_hygiene.json','release/rev_b_review_manifest.json'],
  'CARBENTRA_RevB_VisualSources.zip':lambda p: str(p).startswith('visuals/scripts/') or (str(p).startswith('visuals/rev_b/') and '/renders/' not in str(p) and p.suffix!='.mp4'),
  'CARBENTRA_RevB_ReviewMedia.zip':lambda p: (str(p).startswith('visuals/rev_b/') and ('/renders/' in str(p) or p.suffix=='.mp4')) or str(p)=='release/CARBENTRA_RevB_Design_Review_CN.pdf',
 }
 manifest={'product':'CARBENTRA','revision':'CARBENTRA-P16-EVT-B','commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'digital_only':True,'files':[]}
 for name,select in groups.items():
  target=out/name
  with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
   for p in paths:
    if select(p):z.write(R/p,Path('carbentra-smart-plug')/p)
  with zipfile.ZipFile(target) as z:
   bad=z.testzip()
   if bad:raise RuntimeError('Corrupt ZIP entry: '+bad)
  manifest['files'].append({'name':name,'bytes':target.stat().st_size,'sha256':digest(target),'parts':chunks(target)})
 bundle=out/'CARBENTRA-history.bundle'
 subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=R,check=True)
 subprocess.run(['git','bundle','verify',str(bundle)],cwd=R,check=True)
 manifest['files'].append({'name':bundle.name,'bytes':bundle.stat().st_size,'sha256':digest(bundle),'parts':chunks(bundle)})
 (out/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n', encoding='utf-8', newline='\n')
 (out/'SHA256SUMS.txt').write_text(''.join(f"{x['sha256']}  {x['name']}\n" for x in manifest['files']), encoding='utf-8', newline='\n')
 # Streams all chunks; verifies each and the rebuilt whole before promoting it.
 ps=r'''$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$m = Get-Content (Join-Path $root 'DELIVERY_MANIFEST.json') -Raw | ConvertFrom-Json
foreach ($item in $m.files) {
  if ($item.parts.Count -eq 0) { continue }
  $dest = Join-Path $root $item.name
  if (Test-Path $dest) {
    if ((Get-FileHash $dest -Algorithm SHA256).Hash.ToLower() -eq $item.sha256) { continue }
    throw "Existing file has different contents: $($item.name)"
  }
  $tmp = "$dest.rebuilding"
  $output = [IO.File]::Create($tmp)
  try {
    foreach ($part in $item.parts) {
      $src = Join-Path $root $part.name
      if ((Get-FileHash $src -Algorithm SHA256).Hash.ToLower() -ne $part.sha256) { throw "Chunk hash mismatch: $($part.name)" }
      $input = [IO.File]::OpenRead($src)
      try { $input.CopyTo($output) } finally { $input.Dispose() }
    }
  } finally { $output.Dispose() }
  if ((Get-FileHash $tmp -Algorithm SHA256).Hash.ToLower() -ne $item.sha256) { throw "Archive hash mismatch: $($item.name)" }
  Move-Item $tmp $dest
  Write-Output "Verified: $($item.name)"
}
'''
 (out/'Reassemble-Windows.ps1').write_text(ps,encoding='utf-8-sig', newline='\n')
 print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
