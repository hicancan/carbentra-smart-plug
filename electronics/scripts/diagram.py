from pathlib import Path
from html import escape
R=Path(__file__).resolve().parents[1];p=[]
def rect(x,y,w,h,fill,stroke='#24424b',r=14):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def text(x,y,s,size=24,color='#e8f2f4',weight=400):p.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')
def line(x1,y1,x2,y2,col='#61d9c8'):p.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{col}" stroke-width="4" marker-end="url(#a)"/>')
def block(x,y,w,h,title,rows,col='#142d35'):
 rect(x,y,w,h,col);text(x+22,y+40,title,25,'#ffffff',700)
 for i,row in enumerate(rows):text(x+22,y+78+i*29,row,20)
p.append('<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1190" viewBox="0 0 1800 1190"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#61d9c8"/></marker></defs>')
rect(0,0,1800,1190,'#0b1a22','#0b1a22',0);text(60,73,'CARBENTRA / ELECTRICAL ARCHITECTURE',38,'#ffffff',700);text(60,115,'DEV-A   •   220 VAC nominal / 16 A-class target   •   FABRICATION HOLD',24,'#ffbc69')
rect(40,155,750,590,'#2c2421','#9c693c');rect(835,155,925,590,'#102c33','#2a6d70');text(65,197,'HAZARDOUS MAINS DOMAIN',24,'#ffbc69',700);text(860,197,'ISOLATED CONTROL CANDIDATE',24,'#6ae0cd',700)
block(70,230,315,160,'INPUT / PROTECTION',['Single polarized socket','Fuse + thermal cutoff REQUIRED','Candidates; coordination OPEN'],'#382b24');block(435,230,320,160,'RELAY CONTACTS',['K1: 11 → 14 normally open','TE RT314005 candidate','Motor / inrush rating OPEN'],'#382b24');line(385,310,435,310,'#ffbc69')
block(70,445,315,180,'METERING: NOT BUILT',['ADE9153A hot-domain IC','0.5 mΩ Kelvin-shunt concept','Voltage-divider/filter concept','See pin-level metering design'],'#382b24');block(435,455,320,155,'ISOLATION REQUIRED',['ADuM3151 SPI candidate','Separate isolated meter power','No completed daughterboard'],'#382b24');line(385,530,435,530)
block(870,230,340,180,'ESP32-C3-WROOM-02U',['RISC-V edge control + Wi-Fi/BLE','GPIO10 relay / GPIO18 button','GPIO19 status / I²C temperature','External antenna RF review OPEN']);block(1260,230,465,180,'LOCAL HARDWARE',['Q1 low-side coil driver + D1 flyback','SW1 pushbutton / LED1 indication','TMP102 board temperature only','Independent thermal cutoff REQUIRED']);line(1210,310,1260,310)
block(870,475,340,150,'J3 ISOLATED SPI',['1:3V3  2:GND  3:SCLK','4:MOSI  5:MISO  6:CS','Never connect HOT GND here']);line(755,530,870,530);line(1040,475,1040,410)
block(1260,475,465,150,'POWER',['PS1 IRM-03-5 isolated 5 V candidate','U2 AP63203 → 3.3 V buck','Coil + RF peaks / thermal derating OPEN']);line(1260,550,1210,550)
text(70,695,'PE: continuous protective conductor outside PCB; never switched or bonded to control ground',23,'#ffcf8f')
block(55,790,530,250,'END / EDGE / CLOUD',['END: measure + actuate within hardware limits','EDGE: local policy, timeout, watchdog, hold','CLOUD: bounded profile and configuration','Offline operation must not depend on cloud','Profiles cannot increase physical current ratings']);block(625,790,530,250,'WHAT IS REAL IN THIS RELEASE',['KiCad source, pin-connected schematic, BOM','33 real footprints and package envelopes','Low-voltage routing + actual ERC / DRC','STEP / FCStd / OBJ review geometry','Mains and remaining airwires UNROUTED']);block(1195,790,550,250,'RELEASE GATES',['Complete mains protection and metrology','Close routing / DRC / independent review','Qualify terminals, copper, PE, creepage','Test EMC, dielectric, thermal and endurance','No Gerber / drill package; never energize'])
text(60,1110,'Architecture diagram is a review aid, not a wiring instruction or a safety certification',23,'#a1b9c1');text(60,1150,'Sources: Mean Well IRM-03 • TE RT1 • Espressif C3-WROOM-02U • Diodes AP63203 • TI TMP102 • ADI metrology',18,'#a1b9c1');p.append('</svg>')
(R/'exports/electrical_architecture.svg').write_text(''.join(p), encoding='utf-8', newline='\n')
try:
 import cairosvg;cairosvg.svg2pdf(url=str(R/'exports/electrical_architecture.svg'),write_to=str(R/'exports/electrical_architecture.pdf'))
except ImportError:pass
