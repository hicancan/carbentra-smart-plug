# CARBENTRA Brand & Naming System

本文件冻结当前仓库的品牌层级，避免项目名、平台名、产品名和内部型号再次混用。

## Canonical naming

| 层级 | 规范名称 | 用途 |
| --- | --- | --- |
| 中文项目 / 竞赛作品名 | **碳迹未来** | 申报、路演、中文项目叙事 |
| 正式课题名 | **碳迹未来——基于 AIoT 云边端协同的高校智慧能碳管理平台** | 申报书、报告、答辩封面 |
| 技术平台品牌 | **CARBENTRA** | 云边端平台、GitHub、技术架构 |
| 英文平台描述 | **AIoT Campus Energy Orchestration Platform** | 英文技术说明 |
| 设备产品 | **CARBENTRA Plug** | 智能边缘插座 |
| 感知产品 | **CARBENTRA Sense** | 环境 / 占用 / 状态感知 |
| 边缘层 | **CARBENTRA Edge** | 边缘计算与局部协调 |
| 云端层 | **CARBENTRA Cloud** | 预测、优化、全局调度 |
| 数字孪生 | **CARBENTRA Twin** | 数字孪生与运行态势 |
| 当前硬件工程型号 | **CARBENTRA-P16-EVT-B** | Rev B 工程资产与文件名 |

## Naming rules

- 项目名与平台名不是翻译关系：**碳迹未来**负责中文竞赛叙事，**CARBENTRA**负责长期技术品牌。
- 产品名统一使用“品牌 + 产品族”：`CARBENTRA Plug`、`CARBENTRA Edge`、`CARBENTRA Cloud`、`CARBENTRA Twin`。
- 代码符号采用 `carbentra_` / `CARBENTRA_` 前缀；协议主题使用 `carbentra/` 命名空间。
- 文件名中工程型号统一使用 `CARBENTRA-P16-...`；代码标识符需要下划线时使用 `CARBENTRA_P16_...`。
- Rev A / Rev B 表示工程修订，不是品牌的一部分。
- 不重新引入已经弃用的历史项目名、旧型号前缀或旧协议命名空间。

## Safety language

`220 V AC / 16 A` 在当前仓库中只能称为**设计目标 / 候选工程等级**，不能描述为已经验证的产品额定能力。数字工程检查不等价于实物安全认证、EMC 合规、温升验证或生产放行。
