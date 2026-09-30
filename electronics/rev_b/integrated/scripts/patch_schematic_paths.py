#!/usr/bin/python3
"""Dry-run by default. Parent applies only after routing is paused. Only (path) bytes change."""
import json,re,hashlib,argparse,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def parse(s):
 stack=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def cs(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
def ch(x,k):return next(iter(cs(x,k)),None)
def prop(x,name):return next(v[2] for v in cs(x,'property') if v[1]==name)
main={c['ref'] for c in json.loads((R/'electrical_manifest.json').read_text())['components'] if c['board_designation']=='integrated'}
paths={}
def walk(file,path=None):
 tree=parse(file.read_text());path=path or '/'+ch(tree,'uuid')[1]
 for sym in cs(tree,'symbol'):
  ref=prop(sym,'Reference')
  if ref in main:
   assert ref not in paths
   paths[ref]=path+'/'+ch(sym,'uuid')[1]
 for sh in cs(tree,'sheet'):walk(file.parent/prop(sh,'Sheetfile'),path+'/'+ch(sh,'uuid')[1])
walk(R/'integrated.kicad_sch');assert set(paths)==main
ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args();pcb=R/'integrated.kicad_pcb';raw=pcb.read_bytes();s=raw.decode();patches=[];changes=[];refs=set()
# Balanced token spans retain every byte outside the footprint path fields.
tokens=list(re.finditer(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s));depth=0;fpstart=None;fplevel=None
for i,t in enumerate(tokens):
 if t.group()=='(':
  depth+=1
  if i+1<len(tokens) and tokens[i+1].group()=='footprint':fpstart=t.start();fplevel=depth
 elif t.group()==')':
  if fplevel==depth:
   end=t.end();block=s[fpstart:end];tree=parse(block);ref=prop(tree,'Reference')
   if ref not in paths:
    assert ref in {'H1','H2','H3','H4'} and all(p[1]=='' and p[2]=='np_thru_hole' and ch(p,'net') is None for p in cs(tree,'pad')),ref
    fpstart=fplevel=None;depth-=1;continue
   refs.add(ref)
   old=ch(tree,'path');assert old is not None,ref
   matches=list(re.finditer(r'\(path\s+"(?:\\.|[^"\\])*"\)',block));assert len(matches)==1,ref
   if old[1]!=paths[ref]:
    m=matches[0];patches.append((fpstart+m.start(),fpstart+m.end(),'(path '+json.dumps(paths[ref])+')'));changes.append({'ref':ref,'old':old[1],'new':paths[ref]})
   fpstart=fplevel=None
  depth-=1
assert refs==main
for a,b,new in reversed(patches):s=s[:a]+new+s[b:]
# Prove the entire parsed document, excluding exactly the intended paths, is unchanged.
before=parse(raw.decode());after=parse(s)
for tree in (before,after):
 for fp in cs(tree,'footprint'):
  if prop(fp,'Reference') in main:ch(fp,'path')[1]='__PATH_ONLY__'
assert before==after,'Unexpected non-path PCB change'
stable_snapshot=pcb.read_bytes()==raw
if args.apply:assert stable_snapshot,'PCB changed while preparing paths; retry when routing is paused'
report={'mode':'apply' if args.apply else 'dry-run','footprints_checked':len(refs),'path_changes':len(changes),'changes':changes,'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(s.encode()).hexdigest(),'non_path_geometry_nets_routes_unchanged':True,'input_snapshot_still_current':stable_snapshot}
if args.output:args.output.write_text(s)
if args.apply:
 tmp=pcb.with_suffix('.pathfix.tmp');tmp.write_text(s);assert pcb.read_bytes()==raw,'Concurrent routing write detected';os.replace(tmp,pcb)
(R/'validation/schematic_path_patch.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='changes'},indent=2))
