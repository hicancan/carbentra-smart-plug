# CARBENTRA Rev B：从这里开始

本交付服务于“碳迹未来”平台，是统一自适应智能插座的数字工程开发包。机械、电气、固件和边缘参考实现均附可检查证据；尚未制作并验证实物，不能直接据此接入 220 V。

## 推荐查看顺序

1. `release/CARBENTRA_RevB_Design_Review_CN.pdf`：最终中文图文审阅册（最终发布时提供）
2. `visuals/rev_b/renders/`：外观、内部、透明、剖切、爆炸与六视图
3. `visuals/rev_b/animation/carbentra_exploded.mp4`：装配爆炸动画
4. `mechanical/rev_b/CARBENTRA-P16-EVT-B_system_assembly.FCStd` / `.step`：轻量工程装配
5. `mechanical/rev_b/CARBENTRA-P16-EVT-B_system_detailed.step`：包含详细 PCB 几何的补充装配
6. `visuals/rev_b/carbentra_studio.blend`：可编辑展示场景
7. `electronics/rev_b/integrated/integrated.kicad_pro`：整合电路工程，先读同目录 README
8. `docs/firmware/README.md`、`edge/README.md` 和 `docs/system/`：固件、边缘与云边端架构
9. `docs/ENGINEERING_RELEASE_GATES.md`：进入样机阶段之前的阻断项

## 修订与打开方式

- 当前修订为 Rev B；Rev A 目录为历史基线，不能混用尺寸或检查结论
- FreeCAD 1.0：打开 FCStd，或导入 STEP。71 个物理机械零件；射频余线预留体为非物理辅助几何，默认隐藏
- Blender 4.3.2：打开 `.blend`；动画源场景为同目录 `carbentra_animation.blend`
- KiCad 9：打开整合项目，保留本地符号库、封装库和设计规则
- `visuals/rev_b/exports/carbentra_twin_light.glb`：优化的显示模型，可用于数字孪生应用开发；它没有自动连接真实遥测
- `visuals/rev_b/exports/carbentra_assembly.glb`：详细显示导出。显示网格不替代 CAD 精确几何
- 脚本按 Linux 构建环境编写；Windows 打开源文件可使用对应跨平台软件，执行重建脚本时需调整软件和字体路径

## 已实现及证据

- 机械：原创外壳、插接与保护门、接触簧片、接地路径、端接、保护器件安装、无线与温度拾取布局；冻结清单及几何检查位于 `mechanical/rev_b/`
- 电气：四层整合 PCB、六张原理图页、BOM、布局/布线与独立规则负控；最终 ERC、DRC 和未连接项均为 0，详见 `electronics/rev_b/integrated/validation/`
- 固件：ESP32-C3 开发构建、计量链路诊断、Wi-Fi/BLE 配置路径、认证通信及策略保护；默认禁止执行器动作，需真实凭据、标定和硬件验证
- 边缘：SQLite 接收持久化、重复数据冲突检测、建议型削峰、预测基线和有来源的能碳核算边界；并非完整部署的校园平台
- 最终数字交付状态：`release/digital_checks_rev_b.json`；固件证据：`firmware/validation.json` 和 `release/firmware_evidence_checks.json`

## Git 与交付

当前规范远端为 `https://github.com/hicancan/carbentra-smart-plug`。仓库保留完整 Git 历史；离线交付可继续使用 Git bundle 作为可验证备份，但 GitHub `main` 是当前协作与审阅入口。发布包不包含个人凭据、SSH 私钥或本地认证配置。

## 实物阶段仍未完成

- 16 A 等级与插接规格仍是设计目标；标准量规、公差、插拔力、接触力、寿命和材料工艺需实测
- 市电绝缘、保护接地、温升、异常故障、保护配合与空调浪涌能力需专业审查和试验
- 计量需逐台标定，无线、EMC、网络安全与真实校园部署尚未验证
- 自动升级、安全启动生产配置、实际预测模型训练和平台端到端验收尚未完成

几何距离、软件测试及 ERC/DRC 通过均不构成安全认证。必须完成相关工程放行流程后，才能决定样机通电与现场试用。
