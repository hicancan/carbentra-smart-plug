import route_signals as r
p=r.p
for z in r.b.Zones():
 if z.GetIsRuleArea():z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
pairs=[('+3V3_ISO',(65.8,68.945),(67,68.9125),3,0),('+3V3_ISO',(65.8,68.945),(67,70),3,1),('+3V3_ISO',(65.8,61.325),(67,63.95),3,0),('+3V3_ISO',(65.8,61.325),(65.8,68.945),3,3),('GND_ISO',(67,62.05),(65.8,60.055),0,3),('SPI_CS',(67,67.0875),(65.8,63.865),0,3)]
for n,a,z,al,zl in pairs:r.route(n,a,z,al,zl);p.SaveBoard(str(r.P),r.b)
p.ZONE_FILLER(r.b).Fill(r.b.Zones());p.SaveBoard(str(r.P),r.b)
