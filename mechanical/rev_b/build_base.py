#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Generate only the provisional Rev B mechanical base while PCB layout is being frozen."""
import os,sys,json
BASE=os.path.dirname(os.path.abspath(__file__))
sys.path.extend([FREECAD_LIB,BASE])
import FreeCAD as App,Part
from socket_b_features import SocketBPart,P
D=App.newDocument('CARBENTRA_P16_EVT_B')
s=D.addObject('Spreadsheet::Sheet','Parameters')
for i,(n,v) in enumerate([('Width',108),('Height',93),('Depth',65),('ShutterTravel',0),('LeftPawlStroke',0),('RightPawlStroke',0),('ContactGap',1.7)],1):s.set('A'+str(i),n);s.set('B'+str(i),str(v)+' mm');s.setAlias('B'+str(i),n)
ids=['RearShell','FrontLid','SeamRing','RearFinish','Carrier','ThermalPad','PEChannel','PEBus','ShutterGuide','ShutterSlider','Pawl_L','Pawl_N','PawlSpring_L','PawlSpring_N','ShutterReturnSpring','LocalButton','RearmButton','StatusLightGuide','BladeSleeve_L','BladeSleeve_N']+[a+b for a in ['Blade_','Contact_'] for b in ['L','N','PE']]+['Screw_'+str(i) for i in range(4)]
report=[]
for k in ids:
 o=D.addObject('Part::FeaturePython',k);SocketBPart(o,k)
 for n in ['Width','Height','Depth','ShutterTravel','LeftPawlStroke','RightPawlStroke','ContactGap']:o.setExpression(n,'Parameters.'+n)
 D.recompute();report.append({'id':k,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
# Additional complete power-path hardware
extra=['RFServiceSlackEnvelope','RFAntenna','RFCoax','RFConnectorEnvelope','HeadConnectorEnvelope']+['HeadPigtail_'+str(i) for i in range(3)]+['AuxFuseCradle','AuxFuseRetainer']+['Power'+kind+'_'+n for n in __import__('power_links').ROUTES for kind in ['Core','Carrier']]+['MainFuseHolder','MainFuseCeramic','MainFuseCap1','MainFuseCap2','MainFuseClip1','MainFuseClip2','MainFuseCollector1','MainFuseCollector2','MainFuseRetainer']+['FuseRetainerScrew_'+str(i) for i in range(4)]+['ThermalBody','ThermalLead1','ThermalLead2','ThermalSleeve','ThermalRetainer']+['ThermalRetainerScrew_'+str(i) for i in range(2)]
for k in extra:
 o=D.addObject('Part::FeaturePython',k);SocketBPart(o,k)
 for n in ['Width','Height','Depth','ShutterTravel','LeftPawlStroke','RightPawlStroke','ContactGap']:o.setExpression(n,'Parameters.'+n)
 D.recompute();report.append({'id':k,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
D.saveAs(BASE+'/CARBENTRA-P16-B-base-provisional.FCStd')
json.dump({'status':'PROVISIONAL BASE; NOT FROZEN FINAL ASSEMBLY','parts':report},open(BASE+'/base_geometry_report.json','w'),indent=2)
print(json.dumps(report,indent=2))
