"""Human-readable mechanical inventory, distinct from procurement quantities."""
import json,os,csv
B=os.path.dirname(os.path.abspath(__file__))
def decorate(data):
 labels={'RFServiceSlackEnvelope':'Non-physical44mm coax service-slack reservation','RearShell':'Rear housing with PCB and fuse supports','FrontLid':'Front housing with button/LED guides','Carrier':'Insulating contact and thermal-pickup carrier','PEChannel':'Retained protective-earth routing channel','PEBus':'Continuous protective-earth copper link','ThermalPad':'0.5 mm isolated sensor pickup pad','MainFuseHolder':'Custom insulating carrier for CQP clips','MainFuseCeramic':'SHF main-fuse cartridge ceramic envelope','MainFuseRetainer':'Main-fuse retaining frame','ThermalBody':'TF1 independent one-shot thermal cutoff envelope','ThermalSleeve':'TF1 0.5 mm radial dielectric thermal sleeve','ThermalRetainer':'TF1 insulated retaining saddle','AuxFuseCradle':'Underside 1 A auxiliary-fuse two-saddle cradle','AuxFuseRetainer':'Auxiliary-fuse retaining bridge','LocalButton':'Local operating-button plunger','RearmButton':'Recessed independent thermal-latch rearm plunger','StatusLightGuide':'Status LED optical guide','RFAntenna':'Taoglas FXP73.07.0100A antenna envelope','RFCoax':'1.13 mm coax nominal routed segment','RFConnectorEnvelope':'Mated RF connector clearance envelope','HeadConnectorEnvelope':'Sensor-header mating-housing clearance envelope','Pawl_L':'Left mechanical pawl at N aperture','Pawl_N':'Right mechanical pawl at L aperture'}
 for p in data['parts']:
  n=p['id'];p['name']=labels.get(n,n)
  if n.startswith('HeadPigtail_'):p['name']='Isolated sensor pigtail '+n[-1];p['material']='Insulated low-current copper lead envelope';p['color']=[[.65,.07,.045],[.025,.03,.03],[.04,.4,.18]][int(n[-1])]
  if n.startswith('PowerCore_') or n=='PEBus' or n.startswith('MainFuseCollector'):p['material']='Cu-ETP candidate; forming/joint qualification pending'
  if n.startswith('Contact_'):p['material']='Spring-temper copper-alloy candidate; 0.4 mm leaves, temper/plating unqualified';p['name']='Dual-leaf '+n[-1]+' receptacle spring candidate'
  if n.startswith('Blade_'):p['material']='Conductive copper-alloy rear-blade candidate; interface and joint qualification pending'
  if n.startswith('MainFuseClip'):p['name']='SCHURTER CQP8040.0003 clip envelope';p['material']='Silver-plated conductive spring clip';p['color']=[.66,.69,.7]
  if n.startswith('MainFuseCap'):p['name']='SHF8020.5080 cartridge end-cap envelope';p['color']=[.68,.70,.71]
  if n=='MainFuseCeramic':p['material']='Ceramic cartridge envelope';p['color']=[.82,.82,.76]
  if n=='RFCoax':p['material']='Insulated coax routed segment; remaining44mm allocated in retained service-loop reservation'
  if n=='RFServiceSlackEnvelope':p['material']='NON-PHYSICAL ROUTING RESERVATION; exclude from mass/procurement and default renders';p['color']=[.9,.55,.04];p['geometry_role']='clearance_envelope';p['render_default']=False
  if n=='RFAntenna':p['material']='Flexible RF antenna laminate and adhesive envelope'
  if n in ['RFConnectorEnvelope','HeadConnectorEnvelope']:p['material']='Provisional mating/strain-relief envelope, not vendor detailed CAD'
  p['qualification']='Engineering development; no production or energizing release'
 return data
if __name__=='__main__':
 path=B+'/parts_manifest.json';d=decorate(json.load(open(path)));json.dump(d,open(path,'w'),indent=2)
 with open(B+'/MECHANICAL_PART_INVENTORY.csv','w',newline='') as f:
  w=csv.writer(f);w.writerow(['CAD_ID','Description','Assembly_group','Material_or_envelope','Volume_mm3','Solid_count','Status'])
  for p in d['parts']:w.writerow([p['id'],p['name'],p['group'],p['material'],round(p['volume_mm3'],6),p['solids'],p['qualification']])
