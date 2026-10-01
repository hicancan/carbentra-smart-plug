#!/usr/bin/python3
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];P=R/'candidate_lv.kicad_pcb';b=p.LoadBoard(str(P));net=b.FindNet('L_NC_UNUSED')
if not net:net=p.NETINFO_ITEM(b,'L_NC_UNUSED');b.Add(net)
for f in b.GetFootprints():
 if f.GetReference()=='K1':
  for pad in f.Pads():
   if pad.GetNumber()=='12':pad.SetNetCode(net.GetNetCode())
r=R/'candidate_lv.kicad_dru';s=r.read_text(encoding='utf-8');s=s.replace("A.NetName == 'N')", "A.NetName == 'N' || A.NetName == 'L_NC_UNUSED')");
if "B.NetName == 'L_NC_UNUSED'" not in s:s=s.replace("B.NetName == 'N' ||", "B.NetName == 'N' || B.NetName == 'L_NC_UNUSED' ||")
r.write_text(s, encoding='utf-8', newline='\n')
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
