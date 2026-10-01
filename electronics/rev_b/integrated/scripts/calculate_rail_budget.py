#!/usr/bin/python3
"""Engineering reservation cases, deliberately not a claimed guaranteed all-PVT current maximum."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
V5=5.125;V33=3.4;I33=.55;eta=.80
loads={'AP63203_input_for_550mA_3V3_reservation_W':V33*I33/eta,'R05CT_200mA_input_W':V5*.200,'relay_100mA_reservation_W':V5*.100,'misc_5V_2mA_reservation_W':V5*.002};total=sum(loads.values())
r={'status':'DESIGN RESERVATION ONLY / assembled thermal and transient validation HOLD','assumptions':{'5V_high_V':V5,'3V3_planning_high_V':V33,'ESP_current_capacity_reservation_A':.5,'other_3V3_plus_margin_A':.05,'buck_efficiency_assumed_lower_bound':eta,'buck_efficiency_is_manufacturer_guarantee':False,'coil_current_reservation_A':.1,'coil_reservation_scope':'nominal/warm enclosure operation; cold-soak coil/current tolerance check remains separate','R05CT_input_current_datasheet_max_A':.2},'loads_W':loads,'total_5V_output_power_W':total,'current_equivalent_at_4p875V_A':total/4.875,'hot_3V3_budget_mA':{'ATM90E26_design_reservation':15,'ATM90E26_datasheet_typical_only':5.8,'ASV_8p192MHz_datasheet_max':10,'ISO6741_side2_50Mbps_15pF_max':12.1,'other_pullups_reserve':2,'total_reserved':39.1,'R05CT_low_input_4p5V_output_limit_mA':110,'hot_load_not_added_twice_to_5V':True},'ambient_cases':[],'evidence':'RAIL_BUDGET.md'}
for t,p5,p10 in [(50,5,10),(60,3.75,7.5),(70,2.5,5),(80,1,2.3),(85,.25,1)]:r['ambient_cases'].append({'module_ambient_C':t,'IRM05_available_W':p5,'IRM10_available_W':p10,'IRM05_margin_W':p5-total,'IRM10_margin_W':p10-total})
(R/'validation/rail_budget.json').write_text(json.dumps(r,indent=2), encoding='utf-8', newline='\n');print(json.dumps(r,indent=2))
