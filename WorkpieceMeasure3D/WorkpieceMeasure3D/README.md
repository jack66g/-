# WorkpieceMeasure3D —— 三维工件尺寸自动测量系统

## 1. 项目概述

本项目是一个**基于点云的三维工件尺寸自动测量算法管线**，适用于工业质检场景（如传送带上工件的非接触式尺寸测量）。系统从模拟激光雷达扫描得到的带噪点云出发，经过预处理清洗与鲁棒几何解算，自动输出工件的关键尺寸（长/宽/高，半径/长度）。

核心算法分为两个阶段：

- **阶段一（仿真验证）**：生成带噪声、飞点、扫描盲区的长方体/圆柱体仿真点云 → 体素下采样 + 统计滤波清洗 → RANSAC/PCA 鲁棒尺寸解算 → 3D可视化
- **阶段二（真实数据验证）**：读取真实场景点云（室内房间 / 斯坦福兔子）→ 背景平面剥离 → 实物提取与尺寸测量 → 论文级性能图表

## 2. 目录结构

```
WorkpieceMeasure3D/
├── data/
│   ├── fragment.pcd          # 真实室内场景点云（用于背景剔除实验）
│   └── BunnyMesh.ply         # 斯坦福兔子模型（用于复杂边界测量实验）
├── src/
│   ├── 02_phase1_milestone.py   # 阶段一：仿真数据算法管线主程序
│   ├── 05_real_data_experiment.py # 阶段二：真实物理点云抗噪与测量
│   └── 06_draw_thesis_plots.py   # 论文图表：抗噪性能折线图 + 实时性柱状图
├── output/
│   ├── Experiment_1_Noise_vs_Error.png  # 抗噪性能折线图
│   ├── Experiment_2_Density_vs_Time.png # 实时性对比柱状图
│   ├── 兔子.png / 长方体.png / 圆柱体.png / 室内环境.png 等
│   └── 真实数据测试.png / 数据面板.png
├── src/output/
│   └── (同 output/ 的副本)
└── 需要安装的依赖.txt
```

## 3. 环境准备

### 3.1 系统要求

- **操作系统**：Windows / Linux / macOS
- **Python**：3.8 及以上
- **GPU**：不强制要求（纯 CPU 即可运行）

### 3.2 安装步骤

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows (Git Bash / PowerShell):
source venv/Scripts/activate
# 或 CMD:
venv\Scripts\activate

# 3. 安装依赖
pip install open3d numpy matplotlib
```

## 4. 各模块运行说明

### 4.1 阶段一：仿真算法管线（`02_phase1_milestone.py`）

**功能**：用仿真数据端到端验证整套测量算法的正确性。

运行命令（**从项目根目录**执行）：

```bash
python src/02_phase1_milestone.py
```

执行流程：

1. 生成带噪长方体点云（模拟真实激光雷达单侧扫描盲区、高斯噪声、游离飞点）
2. 体素下采样（1cm 体素格）+ 统计滤波（SOR）清洗
3. 双重 RANSAC 平面提取 → 施密特正交化 → 百分位数抗噪尺寸计算
4. 弹出 3D 窗口显示清洗后的点云（浅蓝色）+ 红色 OBB 包围盒
5. **关闭 3D 窗口**后自动进入圆柱体测试
6. 生成带噪残缺圆柱体（同理含噪、飞点、半侧盲区）
7. PCA + 2D 截面最小二乘拟合半径 → 轴向投影求长度
8. 弹出 3D 窗口显示结果（绿色 OBB 包围盒）
9. 控制台输出真实尺寸与测量尺寸的对比

### 4.2 阶段二：真实数据实验（`05_real_data_experiment.py`）

**功能**：在真实物理点云上验证背景剥离与边界测量算法。

运行命令（**从项目根目录**执行）：

```bash
python src/05_real_data_experiment.py
```

执行流程：

- **实验 A：真实场景背景剔除**  
  读取 `data/fragment.pcd`（室内场景）→ RANSAC 提取最大平面（模拟传送带底面）→ 灰色标记底面、绿色标记有效物体 → 3D 窗口展示
- **实验 B：复杂实物边界测量**  
  读取 `data/BunnyMesh.ply`（斯坦福兔子）→ 注入噪声 → 滤波清洗 → 计算最小定向包围盒（OBB）→ 输出长宽高 → 3D 窗口展示

### 4.3 论文图表生成（`06_draw_thesis_plots.py`）

**功能**：批量生成论文级性能分析图表。

运行命令（**从项目根目录**执行）：

```bash
python src/06_draw_thesis_plots.py
```

执行流程：

1. **实验1 — 抗噪性能折线图**：在 1/3/5/8/12mm 五档高斯噪声下，分别对长方体（双重RANSAC）和圆柱体（降维最小二乘）各测5轮取MAE，绘制噪声-误差曲线
2. **实验2 — 实时性柱状图**：对比原始数据/0.01m体素/0.05m体素三种策略下的单次尺寸解算耗时
3. 图表自动保存至 `output/` 目录

## 5. 核心算法一览

| 步骤 | 技术 | 目的 |
|------|------|------|
| 体素下采样 | `voxel_down_sample` | 降维提速，保持几何特征 |
| 统计滤波 | SOR (`remove_statistical_outlier`) | 剔除游离飞点 |
| 平面提取 | RANSAC (`segment_plane`) | 提取工件主平面 / 剥离传送带背景 |
| 正交化 | 施密特正交化 | 确保三轴严格垂直 |
| 尺寸计算 | 0.5%/99.5% 百分位数 | 无视漏网飞点对极值的拉扯 |
| 圆柱拟合 | PCA + 2D截面最小二乘 | 适用于残缺半圆柱的半径推算 |
| 包围盒 | OBB (Oriented Bounding Box) | 紧凑包裹工件，输出精确尺寸 |

## 6. 常见问题

| 问题 | 解决方法 |
|------|----------|
| 找不到 `fragment.pcd` / `BunnyMesh.ply` | 确保从项目根目录运行，路径为 `data/xxx` |
| 中文图表乱码 | 确认系统安装了 `Microsoft YaHei` 或 `SimHei` 字体，或在 `06_draw_thesis_plots.py` 的 `plt.rcParams['font.sans-serif']` 中添加你系统可用的中文字体 |
| 3D 窗口卡死 / 程序不继续 | 关闭弹出的 Open3D 可视化窗口后程序自动继续 |
| `ImportError: No module named 'open3d'` | 检查虚拟环境是否激活，重新 `pip install open3d` |
