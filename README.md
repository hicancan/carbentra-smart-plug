<div align="center">

# CARBENTRA Plug

### 面向校园能源编排的 AIoT 边缘智能插座

**让普通用电设备拥有可感知、可判断、可执行、可验证的能源接口。**

[English](README_EN.md) ·
[机械工程](mechanical/rev_b/) ·
[电气工程](electronics/rev_b/integrated/) ·
[固件](firmware/) ·
[边缘服务](edge/) ·
[发布证据](release/)

[![Digital development checks](https://github.com/hicancan/carbentra-smart-plug/actions/workflows/digital-checks.yml/badge.svg)](https://github.com/hicancan/carbentra-smart-plug/actions/workflows/digital-checks.yml)
![Revision](https://img.shields.io/badge/revision-Rev%20B-0f766e)
![MCU](https://img.shields.io/badge/MCU-ESP32--C3-2563eb)
![ECAD](https://img.shields.io/badge/ECAD-KiCad%209-7c3aed)
![CAD](https://img.shields.io/badge/CAD-FreeCAD-0284c7)

</div>

<p align="center">
  <a href="visuals/rev_b/renders/01_hero_ivory.png">
    <img src="docs/assets/readme/hero.webp" alt="CARBENTRA Plug Rev B" width="920" />
  </a>
</p>

<p align="center">
  <sub>CARBENTRA Plug Rev B · 当前公开数字工程基线</sub>
</p>

---

## 一只插座，成为能源系统的最后一米

今天，我们把 CARBENTRA 的云边端能源编排能力落到第一个设备产品：**CARBENTRA Plug**。

它连接普通电器，也连接一整套能源系统。

从设备侧的电压、电流、功率、能量与温度感知，到本地安全判断、受约束执行、物理反馈，再到边缘协同、云端预测与优化，CARBENTRA Plug 把一条完整闭环收进同一个设备接口：

> **感知 → 校验 → 判断 → 执行 → 验证 → 回传**

当一台传统设备接入 CARBENTRA Plug，它同时获得联网能力，以及一套可以被能源系统理解和调度的数字接口。

### 四个关键词

| 能力 | CARBENTRA Plug 做什么 |
| --- | --- |
| **Sense / 感知** | 采集电压、电流、功率、能量、板温与输出状态 |
| **Protect / 保护** | 本地故障、负载档案、命令时效、序列与安全边界共同参与决策 |
| **Execute / 执行** | 在本地约束通过后执行受控开关动作 |
| **Verify / 验证** | 通过独立反馈确认输出侧状态，并把结果重新送回控制闭环 |

**云端负责全局智能，本地设备守住物理边界。**

---

## 产品一览

| 项目 | Rev B 数字工程基线 |
| --- | --- |
| 产品名称 | **CARBENTRA Plug** |
| 工程型号 | **CARBENTRA-P16-EVT-B** |
| 名义外形 | **108 × 93 × 65 mm** |
| 主 PCB | **100 × 85 mm，4 层** |
| 主控 | **ESP32-C3-WROOM-02U** |
| 电能计量 | **ATM90E26 + 隔离 SPI + 1 mΩ 分流器** |
| 机械系统 | **71 个物理机械零件** |
| 主板电气项 | **101 个电气项 + 4 个安装位** |
| 网络路径 | Wi-Fi + MQTT mutual TLS 参考实现 |
| 目标接口 | 单路 220 VAC / 16 A 级设计目标 |
| 当前阶段 | **Rev B 数字工程完成，进入实物 EVT 前验证阶段** |

<p align="center">
  <a href="visuals/rev_b/renders/02_hero_detail.png">
    <img src="docs/assets/readme/exterior.webp" alt="CARBENTRA Plug 外观与背部接口" width="920" />
  </a>
</p>

CARBENTRA Plug 的外壳、插孔、后部插脚、本地按钮、状态指示、主板空间、保护器件与温度拾取结构都在统一工程坐标系中完成建模，并贯通 FreeCAD、KiCad、Blender 与系统装配导出。

---

# 01 · Mechanical — 从外形到内部结构

产品首先要在真实空间里成立。

Rev B 机械工程围绕插接结构、保护门、L/N/PE 导电路径、保险与热保护安装、PCB、远端温度拾取、后部插脚和外壳装配建立完整数字模型。

## 六视图

<a href="visuals/rev_b/renders/07_six_view_sheet.png">
  <img src="docs/assets/readme/six-view.webp" alt="CARBENTRA Plug 六视图" width="100%" />
</a>

六视图把产品从视觉概念拉回工程尺寸。当前模型提供可编辑 FreeCAD 源、STEP 总装、独立零件、公共坐标系网格、装配边界和机制检查记录。

## 爆炸结构

<a href="visuals/rev_b/renders/06_exploded_annotated.png">
  <img src="docs/assets/readme/exploded.webp" alt="CARBENTRA Plug 爆炸结构图" width="100%" />
</a>

从外到内可以看到：

- 前后壳体与装配结构；
- 插孔保护门与接触机构；
- L / N / PE 导电路径；
- 保险与热保护部件；
- 四层主 PCB；
- 远端温度拾取头；
- 后部插脚与内部端接。

▶ [查看 6 秒爆炸动画](visuals/rev_b/animation/carbentra_exploded.mp4)

## 剖视图

<a href="visuals/rev_b/renders/08_section_annotated.png">
  <img src="docs/assets/readme/section.webp" alt="CARBENTRA Plug 剖视图" width="100%" />
</a>

剖视图展示各功能域在封闭体积中的真实关系：机械插接结构、电源路径、主板、保护器件与感知部件共享同一装配空间。

工程源文件：

- [FreeCAD 系统总装](mechanical/rev_b/CARBENTRA-P16-EVT-B_system_assembly.FCStd)
- [机械 STEP](mechanical/rev_b/CARBENTRA-P16-EVT-B_mechanical.step)
- [详细系统 STEP](mechanical/rev_b/CARBENTRA-P16-EVT-B_system_detailed.step)
- [机械验证摘要](mechanical/rev_b/VALIDATION_SUMMARY.md)

---

# 02 · Electronics — 把感知、控制与保护装进一块板

CARBENTRA Plug 的电子系统围绕五件事展开：

**测得准、隔得开、控得住、看得到结果、故障时仍保留本地边界。**

<p align="center">
  <a href="electronics/exports/electrical_architecture.svg">
    <img src="docs/assets/readme/electrical-architecture.svg" alt="CARBENTRA Plug 电气架构" width="920" />
  </a>
</p>

Rev B 已经把以下功能域整合进同一套电气工程：

- IRM-10-5 隔离 5 V 电源与 3.3 V 逻辑电源；
- ESP32-C3 主控、编程接口、本地按钮与状态指示；
- ATM90E26 电能计量链路与隔离 SPI；
- 1 mΩ 分流器和电压采样网络；
- 输出侧 AC presence 独立反馈；
- 远端 TMP302 温度阈值链路与本地 rearm；
- 主保险、热保护、继电器与输出路径；
- 连续 PE 导体路径。

## 六页原理图

<a href="electronics/rev_b/integrated/exports/schematic.pdf">
  <img src="docs/assets/readme/schematic-overview.webp" alt="CARBENTRA Plug Rev B 六页原理图总览" width="100%" />
</a>

**点击上图打开完整原理图 PDF。**

六个功能页面已经拆分为：

[总览](electronics/rev_b/integrated/exports/integrated.svg) ·
[Controller](electronics/rev_b/integrated/exports/integrated-1%20controller.svg) ·
[Metering](electronics/rev_b/integrated/exports/integrated-2%20meter.svg) ·
[Feedback](electronics/rev_b/integrated/exports/integrated-3%20feedback.svg) ·
[Thermal](electronics/rev_b/integrated/exports/integrated-4%20thermal.svg) ·
[Assembly / Protection](electronics/rev_b/integrated/exports/integrated-5%20assembly%20protection.svg)

Native KiCad 工程位于：

[`electronics/rev_b/integrated/`](electronics/rev_b/integrated/)

## 四层 PCB

Rev B 主板采用 **100 × 85 mm 四层设计**。当前数字检查记录：

- Native DRC：**0 violations**
- Unconnected items：**0**
- Footprint errors：**0**
- ERC：**0 errors / 0 warnings**
- 主板独立原理图—PCB pin 对照：**321 / 321 keys match**

<a href="electronics/rev_b/integrated/exports/copper_review.pdf">
  <img src="docs/assets/readme/pcb-layout.webp" alt="CARBENTRA Plug 四层 PCB 铜层" width="100%" />
</a>

上图汇总四层铜层，点击即可打开完整 Copper Review PDF。

## PCB 装配

<a href="visuals/rev_b/renders/09_pcb_annotated.png">
  <img src="docs/assets/readme/pcb-assembly.webp" alt="CARBENTRA Plug PCB 装配" width="100%" />
</a>

PCB 视觉装配直接来源于当前 ECAD 导出，并继续进入机械总装与 Blender 展示场景。

进一步查看：

- [Native KiCad project](electronics/rev_b/integrated/integrated.kicad_pro)
- [Electrical BOM](electronics/rev_b/integrated/electrical_bom.csv)
- [Electrical Source](electronics/rev_b/integrated/ELECTRICAL_SOURCE.md)
- [Power / Current Review](electronics/rev_b/integrated/POWER_CURRENT_REVIEW.md)
- [Final Validation Summary](electronics/rev_b/integrated/validation/final_summary.json)

---

# 03 · Firmware — 云端命令到物理动作之间，还有一道本地判断

CARBENTRA Plug 的固件把每一条控制命令都放进设备自身的安全上下文中。

<img src="docs/assets/readme/firmware-control.svg" alt="CARBENTRA Plug 固件控制链" width="100%" />

控制链会检查：

- 设备身份与目标；
- 命令时间边界与 TTL；
- 命令序列与重放；
- 当前负载档案；
- 本地故障锁存；
- 计量数据有效性；
- 动作间隔与当前物理状态；
- 输出反馈是否与请求一致。

### 三条核心原则

1. **本地安全拥有最高优先级。**
2. **过期、重放、错误目标和异常格式命令直接拒绝。**
3. **未知或未批准负载保持 monitor-only。**

当前固件代码已经覆盖：

- C 策略核心；
- ATM90E26 采集与完整性检查；
- TMP102 板温采集；
- AC presence 边沿反馈；
- Wi-Fi 重连；
- BLE 安全配网路径；
- MQTT mutual TLS；
- retain / 分片 / 长度 / 类型 / 重复键边界检查；
- NVS 持久命令序号；
- 有界 RAM 遥测缓冲；
- edge durable receipt 语义。

## 可复现软件检查

```bash
python3 -m unittest discover -s tests/policy -v
python3 -m unittest discover -s edge/tests -v
bash firmware/tests/run_host_tests.sh
python3 scripts/validate_firmware_evidence.py
python3 scripts/check_brand_hygiene.py
```

当前仓库已验证：

- **24 / 24** policy reference tests
- **24 / 24** edge unit tests
- **37** firmware policy cases
- **10,000** local-trip priority invariants
- protocol / meter-reset / stuck-link regression
- feedback qualification
- GitHub Actions digital development checks

ESP32-C3 新版 target binary 将在当前 CARBENTRA namespace 下重新构建后进入下一次发布。

---

# 04 · Edge — 设备数据在楼宇侧形成可持续闭环

设备把事实交给边缘节点，边缘节点把事实沉淀成可以协同的状态。

当前 Edge reference service 已提供：

- MQTT 设备适配；
- allowlist 与设备身份校验；
- SQLite WAL 持久化；
- boot epoch + sequence 去重；
- durable receipt；
- 控制回执保存；
- 削峰建议基线；
- 线性预测基线；
- 带来源边界的能碳核算工具。

一条设备遥测只有在成功落库后才返回持久化收据。由此可以区分“消息到达 broker”和“数据已经进入边缘系统”这两种状态。

[查看 Edge Reference Service](edge/README.md)

---

# 05 · 从 CARBENTRA Plug 到 CARBENTRA

当设备本体的感知、执行和反馈闭环成立，多个设备就可以进入更高层的能源协调。

<img src="docs/assets/readme/system-integration.svg" alt="CARBENTRA 云边端协同" width="100%" />

系统中的分工非常清晰：

- **CARBENTRA Plug**：感知、保护、执行、验证；
- **CARBENTRA Edge**：聚合、局部协调、策略过滤、离线连续性；
- **CARBENTRA Cloud**：负荷预测、碳感知优化、全局调度；
- **CARBENTRA Twin**：映射设备、空间、能耗、碳排与执行状态。

> **一只 Plug，让一台设备可被控制；一组 Plug，让一片负载可以被协同。**

这也是 CARBENTRA Plug 最重要的产品位置：它位于能源算法与真实物理设备之间，把“调度策略”真正落到最后一米。

---

## 工程进度

| 领域 | 当前状态 |
| --- | --- |
| 产品定义 | ✅ CARBENTRA Plug Rev B 数字基线 |
| 机械 CAD | ✅ Native CAD + STEP + 装配 / 机构 / 连通性证据 |
| 电气设计 | ✅ 六页原理图 + 四层 PCB + ERC / DRC 数字检查 |
| 固件 Host Logic | ✅ 策略、协议、反馈、计量回归测试 |
| Edge Reference | ✅ 持久遥测、核算、预测基线测试 |
| Visual / Twin | ✅ Blender、GLB、渲染、爆炸动画 |
| ESP32-C3 新版 Target Binary | 🔄 CARBENTRA namespace 下重新构建 |
| Physical EVT | ⏳ 下一阶段 |
| 逐台计量标定 | ⏳ 实物阶段 |
| 16 A 温升 / 故障验证 | ⏳ 实物阶段 |
| 绝缘 / EMC / Surge / 安规 | ⏳ 专业审查与试验阶段 |
| 校园现场闭环 | ⏳ EVT 与安全放行后进入 |

完整工程放行条件见：

[`docs/ENGINEERING_RELEASE_GATES.md`](docs/ENGINEERING_RELEASE_GATES.md)

---

## 打开工程

### Mechanical

```text
mechanical/rev_b/
├── CARBENTRA-P16-EVT-B.FCStd
├── CARBENTRA-P16-EVT-B_mechanical.step
├── CARBENTRA-P16-EVT-B_system_assembly.FCStd
├── CARBENTRA-P16-EVT-B_system_assembly.step
├── CARBENTRA-P16-EVT-B_system_detailed.step
├── parts/
├── meshes/
└── validation reports...
```

### Electronics

```text
electronics/rev_b/integrated/
├── integrated.kicad_pro
├── integrated.kicad_sch
├── integrated.kicad_pcb
├── electrical_bom.csv
├── electrical_manifest.json
├── exports/
└── validation/
```

### Firmware / Edge

```text
firmware/
├── core/
├── main/
├── tests/
├── tools/
└── validation.json

edge/
├── service.py
├── accounting.py
├── forecast.py
└── tests/
```

### Visual / Digital Twin

```text
visuals/rev_b/
├── carbentra_studio.blend
├── carbentra_animation.blend
├── exports/
│   ├── carbentra_assembly.glb
│   └── carbentra_twin_light.glb
├── renders/
└── animation/
```

---

## 仓库地图

```text
carbentra-smart-plug/
├── mechanical/      # CAD、STEP、零件、机构与装配检查
├── electronics/     # KiCad 原理图、PCB、BOM、电气验证
├── firmware/        # ESP32-C3 源码、策略、计量、网络与主机测试
├── edge/            # 边缘服务、持久遥测、核算与预测基线
├── visuals/         # Blender、渲染、GLB、动画
├── docs/            # 系统契约、品牌体系与平台叙事
├── tests/           # reference policy tests
├── scripts/         # 验证与发布工具
└── release/         # 数字工程发布证据与审阅材料
```

需要按工程审阅顺序阅读时，可以从 [`release/START_HERE.md`](release/START_HERE.md) 开始。

---

## 安全与工程边界

> [!WARNING]
> **当前公开版本对应数字工程阶段。220 VAC / 16 A 级接口是设计目标，实物通电、制造放行与产品合规需在完成专业验证后推进。**

进入 Physical EVT 与现场部署前，工程将继续完成：

- 目标市场对应的插头 / 插座标准确认；
- 实际爬电距离、空气间隙与绝缘结构审核；
- 外壳材料与异常工况验证；
- 预期故障电流与保护配合；
- 16 A 封闭温升与连接点发热试验；
- 插接量规、接触力、寿命、保持力与保护门验证；
- 不同负载类型的浪涌与继电器开断能力测试；
- 电压、电流、功率、能量逐台可溯源标定；
- Surge / EFT / EMC / RF 集成测试；
- 生产级设备身份、安全启动、升级与密钥配置；
- 受控 Physical EVT 与真实场景闭环验证。

这些步骤会把当前数字工程继续推进为可验证的物理产品。

---

## 项目与品牌

**CARBENTRA Plug** 是 CARBENTRA 产品体系中的首个设备终端。

```text
碳迹未来
└── CARBENTRA
    ├── CARBENTRA Plug      ← 本仓库
    ├── CARBENTRA Sense
    ├── CARBENTRA Edge
    ├── CARBENTRA Cloud
    └── CARBENTRA Twin
```

比赛 / 项目层名称：

> **碳迹未来——基于 AIoT 云边端协同的高校智慧能碳管理平台**

平台英文描述：

> **CARBENTRA — AIoT Campus Energy Orchestration Platform**

完整平台叙事已经放到：

[**docs/PLATFORM_OVERVIEW.md**](docs/PLATFORM_OVERVIEW.md)

---

<div align="center">

# CARBENTRA Plug

### **Sense · Protect · Execute · Verify**

**让普通设备进入可编排的能源系统。**

[English README](README_EN.md)

</div>
