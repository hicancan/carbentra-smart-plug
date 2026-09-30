from pathlib import Path
import subprocess,io,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from pypdf import PdfReader,PdfWriter,Transformation
R=Path(__file__).resolve().parents[1];E=R/'exports';(E/'copper').mkdir(exist_ok=True);(E/'copper_pdf').mkdir(exist_ok=True)
subprocess.run(['kicad-cli','pcb','export','svg',str(R/'integrated.kicad_pcb'),'--layers','F.Cu,In1.Cu,In2.Cu,B.Cu','--common-layers','Edge.Cuts','--mode-multi','--exclude-drawing-sheet','--page-size-mode','2','-o',str(E/'copper/')+'/'],check=True)
writer=PdfWriter();sha=hashlib.sha256((R/'integrated.kicad_pcb').read_bytes()).hexdigest()
for layer in ('F_Cu','In1_Cu','In2_Cu','B_Cu'):
 svg=E/'copper'/f'integrated-{layer}.svg';pdf=E/'copper_pdf'/f'integrated-{layer}.pdf';subprocess.run(['inkscape',str(svg),'--export-filename='+str(pdf)],check=True,capture_output=True)
 drawing=PdfReader(str(pdf)).pages[0];buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=landscape(A4));w,h=landscape(A4);c.setTitle('CARBENTRA CARBENTRA-P16-EVT-B copper routing review');c.setFont('Helvetica-Bold',13);c.drawString(14*mm,h-12*mm,'CARBENTRA  |  CARBENTRA-P16-EVT-B  |  '+layer.replace('_','.'));c.setFont('Helvetica',8);c.drawRightString(w-14*mm,h-12*mm,'DEVELOPMENT HOLD');c.setLineWidth(.4);c.line(14*mm,h-15*mm,w-14*mm,h-15*mm);c.setFont('Helvetica',8);c.drawString(14*mm,12*mm,'ROUTING REVIEW ONLY - NO FABRICATION OR ENERGIZATION');c.drawRightString(w-14*mm,12*mm,'Scale 2:1 reference; dimensions in mm');c.setFont('Helvetica',6.7);c.drawString(14*mm,7*mm,'PCB SHA256: '+sha);c.showPage();c.save();buf.seek(0);page=PdfReader(buf).pages[0];scale=2;dw=float(drawing.mediabox.width)*scale;dh=float(drawing.mediabox.height)*scale;page.merge_transformed_page(drawing,Transformation().scale(scale).translate((w-dw)/2,(h-dh)/2),over=False);writer.add_page(page)
writer.add_metadata({'/Title':'CARBENTRA CARBENTRA-P16-EVT-B copper routing review','/Subject':'Development candidate; no manufacturing release','/Author':'CARBENTRA engineering design'})
with(E/'copper_review.pdf').open('wb')as f:writer.write(f)
