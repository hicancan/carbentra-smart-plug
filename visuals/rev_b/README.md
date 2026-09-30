# CARBENTRA · 碳迹未来｜CARBENTRA-P16-EVT-B 可视化

本目录使用共同的机械、主板和远置温度传感头工程源。外壳标称 108 × 93 × 65 mm，单一三孔 16 A 级接口工程目标。数字检查不等于实物装配、量规合格、电气安全认证或可通电许可。

## 文件

- `carbentra_studio.blend`：可编辑完整物理零件场景，保持源网格分件与名称，字体内嵌，使用 Blender 原生压缩保存
- `carbentra_animation.blend`：动画专用刚性分组场景，原零件名称保存在各组 `source_members` 中
- `exports/carbentra_assembly.glb`：完整物理几何，可选择零件
- `exports/carbentra_twin_light.glb`：平台展示轻量模型；保留外观全精度网格与功能零件名，内部使用同一原生 CAD 的 0.04 mm 弦差 / 0.3 rad 角度公差显示网格，铜箔、焊盘和过孔按材质合并。因此不宣称它与完整网格逐顶点相同
- `animation/carbentra_exploded.mp4`：1280 × 1280、24 fps、6 秒的分解／停留／重组动画。动画使用 0.04 mm 显示网格；工程源不受影响
- `renders/`：两张 2400 × 2000 工作室外观图、背面接口、内部结构、透明检查、爆炸图、六视图、剖切图、主板检查
- `exports/deliverables_validation.json`：完成后生成的文件尺寸、哈希、视频参数与源一致性检查

## 几何与显示约定

机械源均为共同坐标系毫米单位。主板 OBJ 的底面位于局部 z=0，仅应用一次 +11.5 mm 的装配平移；HeadB OBJ 已应用正确的 180° X 旋转并置于共同坐标系，不重复平移。导入时统一以 0.001 比例换算为 Blender 米单位。

`exports/import_validation.json` 保存输入哈希、变换矩阵、远置温度头变换来源、原始网格顶点边界与共同坐标验证结果。`exports/common_frame_validation.json` 对照机械总装的主板封装边界。非物理的 RFServiceSlackEnvelope 是空间预留，不作为产品零件出现在产品图和 GLB 中。

分层位移由工程分组派生，属于检查用展示布局，不代表装配或拆解工艺。透明外壳是非物理的检查显示，剖切只作用于场景副本。PCB 图显示真实源铜箔路径及简化封装体；阻焊、塞孔／盖孔、制造工艺和电气安全仍需独立确认。

## 复现

脚本在 `../scripts/`。设置 `CARBENTRA_MECHANICAL_DIR=mechanical/rev_b`、`CARBENTRA_PCB_OBJ=electronics/rev_b/integrated/exports/integrated_assembly.obj`、`CARBENTRA_PCB_Z_MM=11.5`、`CARBENTRA_HEAD_OBJ=electronics/rev_b/integrated/exports/remote_head_assembled.obj`、`CARBENTRA_EXPECTED_ASSEMBLY_BOUNDS=mechanical/rev_b/assembly_world_bounds.json`，并令 `CARBENTRA_OUTPUT_DIR` 指向本目录。实际运行时使用绝对路径。

- Blender 后台运行 `build_studio.py -- technical` 渲染技术图；`hero` 渲染两张外观图；`views` 渲染六视图
- 运行 `prepare_animation_lod.py`，再以 `CARBENTRA_ANIMATION_LOD_DIR` 指向输出目录，执行 `build_studio.py -- animation`
- 在完整 studio 场景上运行 `export_twin_light.py`，`CARBENTRA_TWIN_LOD_DIR` 指向同一动画显示网格目录
- 运行 `compose_sheets_zh.py` 生成中文注释图，最后运行 `validate_deliverables.py`

`_preview/`、`_staged_*`、`_animation_benchmark/` 是过程材料，不应作为验证通过的最终工程源交付。实际完成状态以 `RELEASE_STATUS.json` 和最终验证报告为准。
