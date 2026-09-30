from pathlib import Path
import json, sys
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
R=Path(__file__).resolve().parents[1]; O=R/'release'; O.mkdir(exist_ok=True)
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
W,H=595.28,841.89
DRAFT='--draft' in sys.argv
TARGET=O/('CarbonMirror_Design_Review_DRAFT.pdf' if DRAFT else 'CarbonMirror_Design_Review_CN.pdf')
C=canvas.Canvas(str(TARGET),pagesize=(W,H))
C.setTitle('碳镜校园统一自适应智能插座设计审阅册');C.setAuthor('CarbonMirror project')
style=ParagraphStyle('body',fontName='STSong-Light',fontSize=11,leading=18,textColor='#213a3c',wordWrap='CJK')
small=ParagraphStyle('small',parent=style,fontSize=9,leading=14,textColor='#566868')
page=0

def base(title,sub):
 global page
 page+=1;C.setFillColorRGB(.965,.973,.969);C.rect(0,0,W,H,fill=1,stroke=0)
 C.setFillColorRGB(.05,.18,.17);C.setFont('Helvetica-Bold',10);C.drawString(42,H-40,'CARBONMIRROR / ENGINEERING DEVELOPMENT')
 C.setFont('STSong-Light',23);C.drawString(42,H-80,title)
 para(sub,42,H-110,W-84,small)
 C.setFillColorRGB(.3,.4,.4);C.setFont('Helvetica',8);C.drawString(42,28,'CM-S16-EVT-A   |   2026-09-30   |   NOT FOR ENERGIZATION');C.drawRightString(W-42,28,f'{page:02d}')

def para(s,x,y,w,st=style):
 p=Paragraph(s,st);_,h=p.wrap(w,1000);p.drawOn(C,x,y-h);return y-h-12

def image(path,x,y,w,h):
 p=Path(path)
 if not p.exists() and DRAFT: p=p.with_name('00_'+p.name)
 if not p.exists():raise FileNotFoundError(p)
 iw,ih=Image.open(p).size;scale=min(w/iw,h/ih);ww=iw*scale;hh=ih*scale
 C.drawImage(ImageReader(str(p)),x+(w-ww)/2,y+(h-hh)/2,width=ww,height=hh,mask='auto')

def end():C.showPage()
def bullet(title,text,y):
 C.setFillColorRGB(.02,.18,.16);C.setFont('STSong-Light',14);C.drawString(42,y,title)
 return para(text,42,y-12,W-84)-9

base('统一自适应智能插座设计审阅册','一款硬件平台，以负载能力模型连接端侧感知、边缘自治与校园级能源协同。')
image(R/'visuals/renders/01_hero_ivory.png',28,248,W-56,450)
y=para('本册配合完整 Git 工程使用，重点展示外观、装配、内部板件与数字孪生交付，并说明真实完成的数字检查和仍需关闭的工程问题。',42,230,W-84)
y=para('发布状态：工程开发设计。产品尚未制造、标定或通过市电安全验证；电路放行条件以 electronics 与发布说明为准。禁止据此直接接入 220V。',42,y,W-84)
end()

base('设计规格与产品边界','统一硬件采用负载配置实现差异化控制；不以算法绕过物理接口和额定约束。')
image(R/'visuals/renders/02_hero_detail.png',42,390,W-84,295)
y=365
for a,b in [('结构包络','自主设计外壳 88 × 88 × 55 mm；背部插脚向后延伸 20 mm。PCB 设计包络 72 × 68 mm。接口量规尺寸尚待标准与实物确认。'),('设计目标','220V AC 场景、16A 等级候选规格。该数值不是已测试的额定能力，不代表所有空调或负载可直接接入。'),('统一能力','采集计量、状态感知、本地交互、策略约束、网络接入与平台数据映射采用统一体系。插座不执行面向任意负载的电压调制。'),('参考与原创','用户提供的米家空调伴侣2资料用于外形和功能参考。当前尺寸、结构及品牌为自主设计，未声称复刻其内部硬件。')]:y=bullet(a,b,y)
end()

base('装配结构与内部层次','装配零件具有独立标识与共同坐标；物理层次与平台功能层次分别描述。')
image(R/'visuals/renders/06_exploded_raw.png',30,225,W-60,475)
y=205
y=para('主要层次：前盖与交互件、保护门结构包络、绝缘承载件及触点、电子板件、后壳与固定件、背部插脚及独立保护接地路径。',42,y,W-84)
y=para('爆炸图说明零件位置，不代表已验证装配工艺、保护门防触电效果或插拔寿命。保护接地的几何连接不等于接地连续性实测。',42,y,W-84)
end()

base('内部板件与空间设计','器件候选、封装与包络由电路文件管理，装配模型使用共同的板件坐标。')
image(R/'visuals/renders/04_internal_architecture.png',28,305,W-56,380)
y=285
y=bullet('已经形成的工程配套','KiCad 原理图与板件、候选器件清单、机械装配位置和三维导出。以最终检查记录区分已连接、未布线和待验证项目。',y)
y=bullet('必须保留的电气边界','市电相关区域、隔离电源和安全低压控制区域需要按适用条件完整审查。继电器的标称电流不能直接证明其适用于空调启动或长期运行。',y)
y=bullet('放行条件','计量方案、绝缘配合、载流路径、接触发热、保护设计及制造工艺未完成专业审查与实测前，禁止生产放行和通电。',y)
end()

base('剖切观察与控制板布局','剖切是展示操作，保留原始 CAD；板件来自同一份电路布局。')
image(R/'visuals/renders/08_section_raw.png',30,385,W-60,305)
image(R/'visuals/renders/09_pcb_assembly.png',65,100,W-130,270)
para('上图观察壳体与内部层次，下图展示控制板。器件外形包括名义包络，未全部使用厂商精细 CAD。铜层展示不等于电路已完成安全放行。',42,95,W-84,small)
end()

base('多视角工程表达','同一装配输出不同视图，展示源文件和工程几何的一致性。')
names=[('front','正面'),('rear','背面'),('left','左侧'),('right','右侧'),('top','顶部'),('bottom','底部')]
for i,(n,label) in enumerate(names):
 x=42+(i%2)*262;y=500-(i//2)*203
 image(R/f'visuals/renders/view_{n}.png',x,y,249,183)
 C.setFont('STSong-Light',11);C.setFillColorRGB(.08,.19,.18);C.drawString(x,y-5,label)
para('详细尺寸与量规限制请查看 mechanical 中的尺寸图及说明。渲染视图不替代加工图纸。',42,73,W-84,small)
end()

base('云边端协同与数字孪生','端侧保留约束，边缘协同区域负载，云端管理预测与全局目标。')
y=690
for a,b in [('端侧','统一设备身份、功率与电量数据、按键和状态灯、本地策略、缓存及故障优先。未知或未获准负载只能监测。'),('边缘侧','汇总房间或楼宇内的设备状态，执行授权范围内的区域协调；云端不可用时维持预先批准的策略。'),('云端','结合需求和环境信息进行预测、策略评估与调度；展示数字孪生状态、追溯历史和核算口径。'),('闭环','目标下发后保留设备回执、实际状态和拒绝原因。已发送红外指令不等于负载已经执行。三维模型本身不是完整运行的数字孪生。'),('电碳边界','按有来源的因子计算用电相关排放；插座分表与楼宇总表用于分解校核，不重复相加。节能与削峰必须基于可比较基线验证。'),('参考实现','随附可执行策略模拟与测试，演示过期指令、未知负载、重放、断网和本地保护等处理。认证字段为测试桩，不是已经实现的安全通信或量产固件。')]:y=bullet(a,b,y)
end()

base('无线网络与传感分工','Wi-Fi 承担主要通信，BLE 配网能力待实现；房间传感信息可以由多个插座共享。')
image(R/'docs/system/cloud-edge-end-architecture.png',30,350,W-60,335)
y=330
y=bullet('已选通信硬件','ESP32-C3-WROOM-02U 集成 2.4 GHz Wi-Fi 与 Bluetooth LE；当前模型包含外接柔性天线和同轴线。通信固件、配网与射频实测未完成。',y)
y=bullet('推荐联网路径','插座经校园 IoT 接入点进入局域网，连接楼宇边缘服务，再同步云端。接入点提供网络，边缘服务器负责计算与策略，两者不是同一功能。',y)
y=bullet('测量完成边界','板上 TMP102 不代表已测得插套热点或房间温度。完整电能计量与输出状态检测尚需补全；房间温湿度、占用和门窗可由独立节点提供。',y)
end()

base('验证状态与真实完成程度','数字检查、工程审查和物理测试是不同证据，不能互相替代。')
v=json.loads((R/'mechanical/validation.json').read_text())
digital=json.loads((R/'release/digital_checks.json').read_text()) if (R/'release/digital_checks.json').exists() else {}
y=690
y=bullet('机械数字检查',f'当前机械检查记录包含 {v.get("parts",20)} 个零件。与 970 个电气导出实体的整合检查，仅发现 6 处预期端子导体接入。插入通道与参数重算均有独立记录；这些是数字几何检查。',y)
y=bullet('电路与 PCB 检查','最终 ERC 为 0 错误、0 警告；几何 DRC 为 0 违规，低压部分无未连接项。仍有 9 处市电连接未布线。33 个电气元件的 104 个引脚网络已核对；计量子板和实际输出反馈尚未实现。',y)
y=bullet('可视化与文件检查','审查 Blender 场景、关键渲染与爆炸动画，检查 GLB 文件结构和具名部件。数字交付自动检查见 release/digital_checks.json。',y)
y=bullet('未完成的物理验证','没有实物加工、装配、计量标定、温升、耐压、漏电、接地、EMC、浪涌、异常工况或寿命测试结果。不得将其写入作品报告作为已取得成果。',y)
y=bullet('继续推进条件','下一轮由专业电气人员关闭电路与接口问题，结合选定供应件修订机械结构，再决定打样。真实 220V 测试须在合适的实验条件下执行。',y)
end()

base('文件使用与工程交接','保留原始设计、生成脚本和验证记录，使下一位设计者可以继续工作。')
y=690
for a,b in [('机械与装配','mechanical：FreeCAD 参数化源文件、STEP 装配与零件、STL、参数表和检查记录。修改参数后重新生成并执行检查。'),('电气与 PCB','electronics：KiCad 工程、原理图、PCB、物料清单、导出与检查。具体开放问题以模块 README 为准。'),('视觉与动画','visuals：Blender 场景、渲染图、六视图、动画和 GLB。动画与源场景使用一致装配，不能当成实际制造过程证明。'),('系统与策略','docs/system、tests/policy：架构、能力模型、遥测示例、验收与可执行策略参考。示例均不代表真实设备数据。'),('版本与校验','发布包保留 Git 历史的 bundle、文件清单与校验值。仓库未公开发布；修改后应新建提交并重新验证。'),('证据与引用','用户提供的参考图不作为器件内部证据。器件官方来源与选型限制见 electronics，平台核算与协议依据见 docs/system。')]:y=bullet(a,b,y)
end();C.save();print(TARGET)
