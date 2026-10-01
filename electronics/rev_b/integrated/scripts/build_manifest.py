#!/usr/bin/python3
from pathlib import Path
import json,re,csv
R=Path(__file__).resolve().parents[1];BASE=R.parent
specs=[('controller','circuit_manifest.json',100,{'J1','J3','J5'}),('meter','circuit_manifest.json',200,{'J2','J3'}),('feedback','pin_net_manifest.json',300,{'J1','J2','J3'}),('thermal','pin_net_manifest.json',400,{'J1'})]
parts=[];removed=[]
def nr(ref,off):
 m=re.fullmatch(r'([^0-9]+)([0-9]+)',ref);assert m,ref
 return m[1]+str(int(m[2])+off)
def nmap(module,n):
 if n is None:return None
 if module=='controller':return {'N':'HOT_N','L_FUSED':'HOT_LOAD','L_SWITCHED':'HOT_SWITCHED','L_AUX_FUSED':'HOT_AUX_FUSED','L_NC_UNUSED':'HOT_NC'}.get(n,n)
 if module=='meter':return {'ISO_GND':'GND_ISO','ISO_3V3':'+3V3_ISO','ISO_5V':'+5V_ISO','ISO_SCLK':'SPI_SCLK','ISO_MOSI':'SPI_MOSI','ISO_MISO':'SPI_MISO','ISO_CS':'SPI_CS'}.get(n,n)
 if module=='feedback':return {'L_POST':'HOT_SWITCHED','N_POST':'HOT_N'}.get(n,n if n in ['+3V3_ISO','GND_ISO','OUTPUT_PRESENT_N'] else 'HOT_FB_'+n)
 if module=='thermal':return n if n in ['+3V3_ISO','GND_ISO','+5V_ISO','COIL_5V'] else 'TH_'+n.lstrip('+')
for module,file,off,drop in specs:
 raw=json.loads((BASE/module/file).read_text(encoding='utf-8'));rows=raw if isinstance(raw,list) else raw['components']
 for c in rows:
  oldref=c['ref']
  if oldref in drop:removed.append({'source_module':module,'source_ref':oldref,'reason':'replaced by integrated wiring'});continue
  srcnets=c.get('nets',c.get('pins'));geometry=c.get('pin_geometry',c.get('pins') if isinstance(c.get('pins'),list) else None)
  if not isinstance(srcnets,dict):raise RuntimeError((module,oldref))
  pin_numbers=[p['number'] for p in geometry] if geometry else list(srcnets)
  nets={pn:nmap(module,srcnets.get(pn)) for pn in pin_numbers}
  if module=='meter' and oldref=='J1':nets={'1':'HOT_GND','2':'HOT_N'}
  name=c.get('name',c.get('symbol'));sym=(c['lib']+':'+name) if c.get('lib') else ('Feedback:' if module=='feedback' else 'Thermal:')+name
  board='remote_sensor' if module=='thermal' and oldref in ['U1','R1','C1','J4'] else 'harness_model' if module=='thermal' and oldref.startswith('W') else 'integrated'
  parts.append({'ref':nr(oldref,off),'source_module':module,'source_folder':'../'+module,'source_ref':oldref,'source_symbol':sym,'symbol_name':name,'pins':nets,'source_pins':{pn:srcnets.get(pn) for pn in pin_numbers},'netmap':{n:nmap(module,n) for n in srcnets.values() if n},'pin_geometry':geometry,'footprint':c.get('fp',c.get('footprint')),'value':'PROTECTED LINE + NEUTRAL INPUT' if module=='meter' and oldref=='J1' else c['value'],'mpn':c.get('mpn',''),'datasheet':c.get('url',c.get('datasheet','')),'height_mm':c.get('height',c.get('height_mm')),'source_schematic_position':c.get('sch',c.get('schematic')),'board_designation':board,'in_bom':board!='harness_model','on_board':board!='harness_model'})
parts.append({'ref':'F501','source_module':'integrated','source_folder':'.','source_ref':None,'source_symbol':'Device:Fuse','symbol_name':'Fuse','pins':{'1':'HOT_GND','2':'HOT_AUX_FUSED'},'source_pins':{},'netmap':{},'pin_geometry':[{'number':'1','name':'1','at':[0,3.81,270],'type':'passive'},{'number':'2','name':'2','at':[0,-3.81,90],'type':'passive'}],'footprint':'Integrated:Fuse_215_Axial_P30mm','value':'1A T 250VAC AUX FUSE / HOLD','mpn':'0215001.MXEP','datasheet':'https://www.littelfuse.com/assetdocs/littelfuse_fuse_215_datasheet.pdf?assetguid=990f7193-d9a2-48e4-b760-2b43514249cf','height_mm':7.3,'body_mm':[21.5,5.5],'body_tolerance_mm':[1,.3],'lead_pitch_mm':30,'drill_mm':.9,'standoff_mm':1.5,'board_designation':'integrated','in_bom':True,'on_board':True,'status':'exact footprint authored by parent; application voltage/interruption qualification HOLD'})
for c in parts:
 if c['ref'] in ['J102','J201']:
  c.update(footprint='Integrated:MKDS5_2_7p62',mpn='1868076',datasheet='https://www.phoenixcontact.com/us/products/1868076/pdf',height_mm=21.5,body_mm=[15.24,12.5,21.5],lead_pitch_mm=7.62,drill_mm=1.3,pin_cross_section_mm=[.9,.9],pin_length_mm=5.1)
 if c['ref']=='J201':c['netmap']={'HOT_LOAD':'HOT_GND','HOT_GND':'HOT_N'}
for c in parts:
 if c['ref']=='U101':c.update(height_mm=3.35,body_mm=[18,14.3,3.2],height_basis='Espressif v1.7 Figure10-2:3.2mm total module height plus0.15mm tolerance; includes0.8mm substrate',rf_axis_local_pcb_mm=[6.25,-5.1],rf_axis_source='Figure10-2:2.75mm from rightedge,2.30mm from topedge')
 if c['ref']=='PS101':c.update(source_symbol_original=c['source_symbol'],source_symbol='Converter_ACDC:IRM-10-5',symbol_name='IRM-10-5',value='IRM-10-5',mpn='IRM-10-5',datasheet='https://www.meanwell.com/Upload/PDF/IRM-10/IRM-10-SPEC.PDF',footprint='Integrated:IRM10_Controller_Candidate',body_mm=[45.7,25.4,21.5],height_mm=21.5,symbol_override=True,pin_compatibility='Official case222A bottom-view comparison and exactKiCad footprint pad-coordinate equality checked againstIRM-05')
parts=[c for c in parts if c['ref']!='CX202']
for c in parts:
 if c['ref']=='U201':c['pins']['23']=None
 if c['ref']=='Y201':
  c.update(source_symbol='Oscillator:ASV-xxxMHz',symbol_name='ASV-xxxMHz',pins={'1':'HOT_3V3','2':'HOT_GND','3':'HOT_XIN','4':'HOT_3V3'},footprint='Oscillator:Oscillator_SMD_Abracon_ASV-4Pin_7.0x5.1mm',value='ASV-8.192MHZ-LC-S-T / candidate',mpn='ASV-8.192MHZ-LC-S-T',datasheet='https://abracon.com/Oscillators/ASV.pdf',height_mm=1.8,body_mm=[7,5.1],symbol_override=True,procurement_gate='Exact-frequency orderability confirmation required')
 if c['ref']=='CX201':
  c.update(pins={'1':'HOT_3V3','2':'HOT_GND'},value='100nF 16V X7R',mpn='GRM188R71C104KA01D',datasheet='https://www.murata.com/en-us/products/productdetail?partno=GRM188R71C104KA01D',height_mm=.9)
for c in parts:
 if c['ref'] in ['R201','R202']:c.update(footprint='Resistor_SMD:R_0603_1608Metric',mpn='TNPW0603100RBEEA',value='100R',datasheet='https://www.vishay.com/docs/28758/tnpw_e3.pdf',height_mm=.55,body_mm=[1.6,.8],tolerance_percent=.1,tcr_ppm_per_K=25)

assembly_rows=[
 ('F601','Fuse_Main','F_MAIN / 16A FAST 500VAC','8020.5080',{'1':'RAW_L','2':'HOT_TF_IN'},'https://www.schurter.com/en/datasheet/typ_SHF_6.3x32.pdf'),
 ('TF601','Thermal_Link','THERMAL LINK / Tf110C / SUFFIX HOLD','MICROTEMP G5 Tf110C; exact suffix HOLD',{'1':'HOT_TF_IN','2':'HOT_GND'},'https://www.sensience.com/wp-content/uploads/2022/12/Microtemp_Catalog.pdf'),
 ('J601','Plug_Contacts','PLUG BLADES / L N PE / ASSEMBLY HOLD','Custom mechanical plug blade assembly',{'1':'RAW_L','2':'HOT_N','3':'PE'},''),
 ('J602','Socket_Contacts','SOCKET CONTACTS / L N PE / ASSEMBLY HOLD','Custom mechanical socket contact assembly',{'1':'HOT_SWITCHED','2':'HOT_N','3':'PE'},'')]
for ref,name,val,mpn,pins,url in assembly_rows:
 parts.append({'ref':ref,'source_module':'assembly','source_folder':'.','source_ref':ref,'source_symbol':'IntegratedAssembly:'+name,'symbol_name':name,'pins':pins,'source_pins':pins,'netmap':{n:n for n in pins.values()},'pin_geometry':None,'footprint':'','value':val,'mpn':mpn,'datasheet':url,'height_mm':None,'board_designation':'off_board_assembly','in_bom':True,'on_board':False,'mechanical_status':'Off-PCB internal assembly; Custom contact geometry / installed holder support and wiring qualification HOLD','pin_numbering':'Assembly wiring identifiers for contacts/thermal link; not a claim about unselected vendor contact numbering'})
next(c for c in parts if c['ref']=='F601').update(manufacturer='SCHURTER',family='SHF 6.3x32',interrupting_rating='1500 A at 250 VAC cos(phi)0.7-0.8; 1500 A at500 VAC cos(phi)0.99-1; footnote3; actual prospective-current coordination HOLD',nominal_melting_I2t_A2s=760,I2t_definition='Typical melting/pre-arcing at10xIn, NOT total clearing energy or downstream withstand bound',active_current_limit=False,body_nominal_mm=[31.8,6.35],holder={'manufacturer':'SCHURTER','mpn':'8040.0003','quantity':2,'family':'CQP','type':'silver plated heavy-duty6.3x32 fuse clip','datasheet':'https://www.schurter.com/en/datasheet/typ_CQP.pdf','nominal_current_A':32,'rated_voltage_VAC':600,'ambient_range_C':[-55,155],'clip_width_mm':7.85,'clip_height_above_carrier_mm':10.3,'clip_height_including_pins_mm':13.9,'clip_center_spacing_mm':27.3,'outer_pin_span_mm':34.9,'pin_pitch_within_clip_mm':7.6,'drill_mm':1.8,'mechanical_status':'Two clips on separate45x16x2 insulating carrier, dedicated4x1.2mm copper collectors; fit accepted by mechanics, assembly qualification HOLD'},duration_limits_at_16A={'16A':'240min minimum pre-arcing test duration, not lifetime endurance','33.6A':'30min maximum','44A':'0.1-5s','64A':'0.02-1s','160A':'0.05s maximum'},supersedes={'fuse':'0216016.MXP','holder':'OGN0031.8201','reason':'OGN full-current heat acceptance~2.8W@50C/~2.4W@60C below old216 rated-current dissipation ceiling3.2W','old_nominal_melting_I2t_A2s':462.5},mechanical_status='Mechanics confirms no shell growth;45x16x2 carrier and copper collectors; physical thermal/insulation/retention testing HOLD')
next(c for c in parts if c['ref']=='TF601').update(Tf_C=110,Th_C=95,Tm_C=225,body_nominal_mm=[14.7,4.0],safety_status='Distinct one-shot thermal device; assembly response and exact order suffix unqualified')
out={'schema_version':1,'status':'EARLY PIN-NET MANIFEST; integrated schematic/ERC pending','target_main_board_mm':[100,85,1.6],'components':parts,'removed_module_connectors':removed,'board_designations':{'integrated':'place on main PCB','remote_sensor':'separate 12x12 sensor head; do not place on main PCB','harness_model':'off-board conductor models; not PCB/BOM','off_board_assembly':'Internal plug/socket/main-fuse/thermal-cutout assembly; not PCB-mounted'},'notes':['HOT_GND means protected line potential, never SELV or protective earth.','Reference designators are module-offset and true device pad numbers remain unchanged.','Provisional operating proposal is 220VAC +/-10% (198-242VAC), pending parent/user confirmation. 264VAC is measurement-analysis headroom only, not a product rating. F501 is a 250VAC component.']}
(R/'electrical_manifest.json').write_text(json.dumps(out,indent=2), encoding='utf-8', newline='\n');print('Published',len(parts),'components;',sum(c['board_designation']=='integrated' for c in parts),'main;',sum(c['board_designation']=='remote_sensor' for c in parts),'head;',sum(c['board_designation']=='harness_model' for c in parts),'wire models;',sum(c['board_designation']=='off_board_assembly' for c in parts),'off-board assemblies')

with (R/'electrical_bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Board','Reference','Source module','Original reference','Value','MPN candidate','Footprint','Height mm','Source URL','Assembly accessory MPN','Accessory quantity'])
 for c in parts:
  if c['in_bom']:w.writerow([c['board_designation'],c['ref'],c['source_module'],c['source_ref'],c['value'],c['mpn'],c['footprint'],c['height_mm'],c['datasheet'],c.get('holder',{}).get('mpn',''),c.get('holder',{}).get('quantity','')])
