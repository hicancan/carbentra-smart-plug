# 从这里开始

本交付是碳镜校园统一自适应智能插座的数字工程开发包，不是可直接制造或接入 220 V 的成品方案。

## 推荐查看顺序

1. `release/CarbonMirror_Design_Review_CN.pdf`：中文图文审阅册
2. `visuals/renders/`：外观、内部、透明、剖切、爆炸与六视图
3. `visuals/animation/carbonmirror_exploded.mp4`：装配爆炸动画
4. `mechanical/CarbonMirror_S16_SystemAssembly.FCStd` / `.step`：完整机械与板件装配
5. `visuals/carbonmirror_studio.blend`：可继续编辑的可视化场景
6. `electronics/carbonmirror.kicad_pro`：电路开发工程，先读其 README
7. `docs/system/`：云边端、无线与传感器、策略及验证说明

## 打开和继续设计

- Blender 4.3.2：打开 `.blend`，场景中有独立部件和相机，字体已打包。最终动画场景另存于 `visuals/carbonmirror_animation.blend`。
- FreeCAD 1.0：STEP 可直接导入；原生参数化特征重算按 `mechanical/README.md` 操作，附本地宏与脚本。
- KiCad 9：打开项目，保留最终原理图、板文件及本地符号库；不要把无几何 DRC 错误等同于可用电路。
- GLB：`visuals/exports/carbonmirror_assembly.glb` 用于支持 glTF 2.0 的查看器或后续数字孪生应用。静态模型本身未连接设备数据。

脚本按此构建环境编写；在 Windows 上需调整本地软件调用与字体路径。源文件本身可用相应跨平台软件打开。未安装任何远程服务或自动开机程序。

## Git

交付压缩包保留本地 Git 仓库与历史，没有远程地址，没有推送 GitHub，也没有公开发布。解压后可在项目目录运行 `git log --oneline` 查看阶段提交。

## 当前最重要的未完成项

- 市电部分的 9 处连接未布线，完整计量子板和实际输出状态检测仍需设计
- 插脚/插孔量规、保护门运动和真实端接、线径、公差与材料工艺需确认
- 没有制作实物，没有热、电、机械耐久、无线或计量认证测试
- 策略参考是离线模拟，不是设备固件；配网、认证、升级和校园实际部署未实现

优先完成专业电气审查与上述数字设计缺口，再决定样机与实测。不能跳过放行门槛直接通电。
