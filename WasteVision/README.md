# WasteVision — 智能垃圾分类上位机视觉大脑

## 1. 项目简介

WasteVision 是一个基于 **YOLOv8 目标检测**的智能垃圾分类系统，作为上位机运行在 PC 端。它通过摄像头实时识别垃圾物品，自动分类为**可回收物、厨余垃圾、有害垃圾、其他垃圾**四类，并通过 **MQTT 协议**将分类结果下发到下位机（如 ESP32），驱动对应的舵机打开仓门，同时用**语音播报**提示用户。

### 核心功能

| 功能 | 说明 |
|------|------|
| 实时摄像头识别 | 调用本地摄像头，逐帧进行 YOLOv8 推理并标注 |
| 本地上传图片识别 | 选择本地图片文件进行单次识别 |
| MQTT 云端下发 | 识别结果通过巴法云 MQTT 下发到硬件端 |
| 语音播报 | 用中文语音读出当前识别结果 |
| 手动模拟发送 | 可在界面直接输入分类标签手动下发指令 |

---

## 2. 系统架构

```
┌──────────────────────┐     MQTT (bemfa.com:9501)
│  PC 上位机           │ ──────────────────────────────> ┌──────────────┐
│  ├─ YOLOv8 识别引擎  │   JSON: {"label": "recyclable"}  │  ESP32 下位机  │
│  ├─ Tkinter GUI      │                                 │  ├─ 舵机1: 可回收 │
│  ├─ pyttsx3 语音播报 │                                 │  ├─ 舵机2: 厨余  │
│  └─ MQTT Client      │                                 │  ├─ 舵机3: 有害  │
└──────────────────────┘                                 │  └─ 舵机4: 其他  │
                                                         └──────────────┘
```

### MQTT 消息格式

下发的 JSON 格式：

```json
{"label": "recyclable"}  // 可回收物
{"label": "food"}        // 厨余垃圾
{"label": "harmful"}     // 有害垃圾
{"label": "other"}       // 其他垃圾
```

### 垃圾分类映射表

| 垃圾类别 | MQTT 标签 | 下位机动作 | COCO 数据集对应物体 |
|----------|-----------|------------|---------------------|
| 可回收物 | `recyclable` | GPIO 13 舵机 | bottle, cup, wine glass, can |
| 厨余垃圾 | `food` | GPIO 12 舵机 | apple, orange, banana, broccoli, carrot |
| 有害垃圾 | `harmful` | GPIO 15 舵机 | cell phone, remote |
| 其他垃圾 | `other` | GPIO 2 舵机 | book, clock |

---

## 3. 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11（推荐）、macOS、Linux |
| Python | **3.10**（已在 3.10.6 下测试） |
| 摄像头 | USB 摄像头（实时识别需要） |
| 网络 | 需要联网（连接巴法云 MQTT 服务） |
| 模型文件 | `yolov8n.pt`（已提供，约 6.5MB） |

---

## 4. 快速开始

### 4.1 创建并激活虚拟环境

```bash
# Windows（Git Bash / CMD）
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4.2 安装依赖

```bash
pip install ultralytics opencv-python paho-mqtt pyttsx3 Pillow

# Windows 下若 pyttsx3 报错，降级 comtypes
pip install comtypes==1.1.11
```

### 4.3 配置 MQTT（重要）

在 `main_vision.py` 的配置区修改自己的巴法云信息：

```python
MQTT_SERVER = "bemfa.com"
MQTT_PORT = 9501
MQTT_USER = "你的巴法云私钥"   # <-- 替换这里
TOPIC = "WaterMonitor"          # <-- 替换为你的主题
```

> 巴法云注册地址：https://cloud.bemfa.com（免费注册后获取私钥）

### 4.4 启动程序

```bash
python main_vision.py
```

首次运行时 YOLO 模型会自动下载（约 6.5MB），若已存在 `yolov8n.pt` 则直接加载。

---

## 5. 使用指南

### 界面布局

```
┌──────────────────────┬─────────────────────┐
│                      │     系统控制          │
│                      │                     │
│   640×480 视频显示区  │  [开启实时识别]       │
│   （识别结果标注）     │  [上传图片识别]       │
│                      │  [停止识别]           │
│                      │                     │
│                      │  手动模拟发送标签:     │
│                      │  [recyclable  ▾  ]  │
│                      │  [发送手动指令]       │
│                      │                     │
│                      │  系统日志:            │
│                      │  [10:30:01] ...     │
│                      │  [10:30:05] ...     │
└──────────────────────┴─────────────────────┘
```

### 操作步骤

1. **开启实时识别**：点击绿色按钮，程序会打开摄像头并持续识别画面中的物体。识别到已知类别后自动通过 MQTT 下发指令并语音播报。

2. **上传图片识别**：点击按钮选择图片文件，程序对该图片进行识别并显示结果。

3. **手动发送**：在输入框中输入 `recyclable` / `food` / `harmful` / `other` 任一标签，点击「发送手动指令」可直接向下位机发送指令（用于调试）。

4. **停止识别**：点击红色按钮释放摄像头并停止所有识别。

### 限流机制

为防止频繁下发，同一标签的 MQTT 指令**最短间隔 3 秒**才会再次发送。

---

## 6. 项目文件结构

```
WasteVision/
├── main_vision.py    # 主程序（含 GUI、识别、MQTT、语音）
├── yolov8n.pt        # YOLOv8 nano 模型权重文件
├── venv/             # Python 虚拟环境
├── 说明.txt           # 原始简要说明
└── README.md         # 本启动与介绍文档
```

---

## 7. 自定义垃圾分类

如需增加/修改识别类别，编辑 `main_vision.py` 中的 `CLASS_MAPPING` 字典：

```python
CLASS_MAPPING = {
    'bottle': 'recyclable',
    'cup': 'recyclable',
    # 新增你想识别的类别 ↓
    'keyboard': 'other',       # COCO 中已有的类别
    'your_custom': 'harmful',  # 自定义训练的类别
}
```

- COCO 数据集共 80 个类别，完整列表参考：[Ultralytics YOLOv8 文档](https://docs.ultralytics.com/datasets/detect/coco/)
- 如需识别 COCO 之外的物品，需要自行训练 YOLO 模型

---

## 8. 常见问题

### Q1: MQTT 连接失败
- 检查网络是否能访问 `bemfa.com:9501`
- 确认私钥 `MQTT_USER` 填写正确
- 可先注释 MQTT 相关代码，仅离线运行识别功能

### Q2: 摄像头打不开
- 检查摄像头是否被其他程序占用
- 确认 USB 连接正常
- 代码中 `cv2.VideoCapture(0)` 的 `0` 代表默认摄像头，可改为 `1` 尝试其他设备

### Q3: pyttsx3 语音无声音
- Windows：确保系统 TTS 引擎正常
- 可尝试 `pip install pyttsx3==2.90` 或安装 `pypiwin32`
- 如仍无法解决，可注释 `threading.Thread(target=self.speak, ...)` 行禁用语音

### Q4: 模型下载慢
- YOLOv8n.pt 已预置在项目目录中，程序会优先加载本地文件
- 如需要更新模型，可手动下载放到项目根目录

---

## 9. 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 目标检测 | Ultralytics YOLOv8 Nano | 物体识别与分类 |
| GUI 框架 | Tkinter + Pillow | 桌面界面与图像显示 |
| 图像处理 | OpenCV (cv2) | 摄像头读取、图像处理 |
| 物联网通信 | paho-mqtt | 巴法云 MQTT 消息下发 |
| 语音合成 | pyttsx3 | 中文语音播报 |
| 模型权重 | yolov8n.pt | 预训练 COCO 模型 |
