# CARBENTRA Plug Rev B：当前交付入口

本仓负责Plug机械、电气、固件和物理放行事实。2026-10-01教室升级后，多产品Edge及合同已统一到carbentra-campus-platform；hardware/edge只留迁移与来源记录，不再有第二套运行实现。实物尚未制造/逐台标定/市电安全验证，制造与通电继续HOLD。

本机可复现入口见 [Windows 开发说明](../docs/WINDOWS_DEVELOPMENT.md)：uv / Python 3.12、MSVC、ESP-IDF 5.4.3、KiCad 10.0.5、FreeCAD 1.1.4、Blender 5.2.2。Windows 入口自动构建并执行四个真实 C 跨语言门禁；最新 Windows/Linux 软件结果与源码摘要见 `firmware/remediation-report.json`。历史 290 项数字设计检查不因本次软件维护自动更新，原生 CAD、三张用户修改的展示图和有依赖的源模块均保留。

153 个已忽略备份/帧/旧 host 产物约 402.15 MiB 已由用户执行清理，并于 2026-10-01 逐项确认不存在；它们未进入公开包。`release/windows-cleanup.json` 保留审计清单，`scripts/clean_local_outputs.ps1` 默认只读，用户显式 `-Apply` 才处理仍存在且身份匹配的候选。

## 当前查看顺序

1. `firmware/validation.json`：官方ESP-IDF5.4.3/ESP32-C3真实构建、当前C源/开发二进制摘要、主机测试及显式共享Edge证据
2. `docs/firmware/README.md`：本地按钮ON的同等安全守卫、15分钟手动保持、维护/受保护负载边界、可信时间和反馈语义
3. `contracts/README.md`、`edge/README.md`：共享包/共享运行时的唯一入口；运行完整跨仓测试必须设置CARBENTRA_PLATFORM_ROOT
4. `electronics/rev_b/integrated/integrated.kicad_pro`：未改变的整合电路工程；机械/电气当前独立数字检查见`release/digital_checks_rev_b.json`及相关freeze证据
5. `mechanical/rev_b/CARBENTRA-P16-EVT-B_system_assembly.FCStd` / `.step`与detailed.step：可编辑和补充CAD
6. `visuals/rev_b/`：原有实际CAD派生外观/装配/动画；本次软件升级没有重造未改变的外壳或PCB
7. `release/CARBENTRA_RevB_Design_Review_CN.pdf`：历史硬件设计审阅册；其中旧软件联调描述不能代替当前共享Edge证明
8. `docs/ENGINEERING_RELEASE_GATES.md`：实物与现场部署的独立门槛

## 当前软件变化

物理按键经稳定50ms防抖且开机先释放，允许请求切换；ON必须通过逐台调试放行、已批准非关键可切负载、有效新鲜计量/反馈、无故障及最短停启间隔。没有通过伪造网络鉴权绕过策略。物理OFF仍可离线请求。真实按键记录事件序号/时间/结果并形成15分钟手动保持；自动指令不能立即反向覆盖。维护状态阻止ON；故障锁存不能远程清除。

目标已实际重新编译，执行器默认仍被编译禁用。45个C策略案例、额外local-input守卫断言、10,000个故障优先不变量、7个启动场景、真实签名/证书负控及固件JSON→共享Edge合同测试已执行。当前共享suite数量和源摘要见`firmware/evidence/shared-edge-validation.json`；若共同仓继续变化，须重跑并更新证据，不以旧pass覆盖新源。

`release/software_broker_integration.json`仅为退休Edge的历史五组软件证明。新的多设备/两教室mTLS和实际后端闭环证据属于共同平台；firmware/validation.json明确区分当前共享proof与过期/缺失状态。虚拟软件设备的SIMULATED来源不会被当作真实运行结果。

## 独立职责和限制

- Plug/Switch/Sense硬件仓：各自电路、固件、物理输入和资格边界
- 校园资产仓：空间身份、坐标、模型及浏览器资产；不是现场测绘/部署数量证明
- 平台仓：唯一设备合同/Edge、资产绑定、权限、命令生命周期、预测/策略、能碳账本和UI

独立hardware CI仅检查本仓C host、CAD证据和ESP目标编译。跨仓密码学/设备wire/MQTT检查在显式共同工作区执行；缺共享源不会被静默跳过为pass。当前没有生产部署、真实设备烧录或市电动作，也不声称远程GitHub CI已验证本地修改。

16A、插接量规、绝缘/接地、耐压漏电、温升、异常故障、保护配合、浪涌EMC、逐台计量标定与实际无线/反馈互通仍需专业实测。数字通过不是安全认证或已证明校园节能成果。远端身份以Git配置/日志为准，交付状态以当前源/产物摘要为准。
