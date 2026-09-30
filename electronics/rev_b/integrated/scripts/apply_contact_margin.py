import route_signals as r
p=r.p
for f in r.b.GetFootprints():
 if f.GetReference()=='RS201':f.SetPosition(p.VECTOR2I(p.FromMM(40),p.FromMM(64.5)))
 if f.GetReference()=='PS101':
  f.SetValue('IRM-10-5');f.SetFPID(p.LIB_ID('Converter_ACDC','Converter_ACDC_MeanWell_IRM-10-xx_THT'))
r.W=2.4;r.seg((44.16,47.5),(41.5,46.5),'HOT_SWITCHED',0);r.W=4.8;r.seg((41.5,46.5),(39,45.76),'HOT_SWITCHED',0);r.W=.15
r.route('HOT_CS',(50.4125,59.8),(54.125,63.865))
r.route('HOT_GND',(46.5,59.05),(39.15,60.475))
r.route('HOT_SWITCHED',(7,31),(28.5,45.76))
p.SaveBoard(str(r.P),r.b)
