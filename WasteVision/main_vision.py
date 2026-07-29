import cv2
import time
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import pyttsx3

# ================= 配置区 =================
MQTT_SERVER = "bemfa.com"
MQTT_PORT = 9501
MQTT_USER = "79ac2469ffbc41019518463ec32ced08" # 你的私钥
TOPIC = "WaterMonitor" # 你的主题

# YOLO 类别到下位机标签的映射表 (根据 COCO 数据集修改)
# 可回收: bottle, cup, wine glass, can
# 厨余: apple, orange, banana, broccoli, carrot
# 有害: cell phone, battery(需训练), remote
# 其他: book, clock, keyboard
CLASS_MAPPING = {
    'bottle': 'recyclable', 'cup': 'recyclable', 'wine glass': 'recyclable',
    'apple': 'food', 'orange': 'food', 'banana': 'food', 'broccoli': 'food',
    'cell phone': 'harmful', 'remote': 'harmful',
    'book': 'other', 'clock': 'other'
}

# ================= 核心处理类 =================
class WasteBrainUI:
    def __init__(self, window):
        self.window = window
        self.window.title("智能垃圾分类 - 上位机视觉大脑")
        self.window.geometry("1000x700")

        # 1. 初始化模型与硬件
        self.model = YOLO('yolov8n.pt') # 第一次运行会自动下载
        self.engine = pyttsx3.init()
        self.last_send_time = 0
        self.cd_time = 3 # 3秒限流
        
        # 2. 初始化 MQTT
        self.mqtt_client = mqtt.Client(client_id=MQTT_USER, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        try:
            self.mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except:
            print("MQTT 连接失败，请检查网络")

        # 3. 界面布局
        self.create_widgets()
        
        # 摄像头变量
        self.cap = None
        self.is_running = False

    def create_widgets(self):
        # 左侧：视频/图片显示区
        self.canvas = tk.Canvas(self.window, width=640, height=480, bg="#2c3e50")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # 右侧：控制区
        right_frame = tk.Frame(self.window)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        tk.Label(right_frame, text="系统控制", font=("微软雅黑", 16, "bold")).pack(pady=10)

        # 按钮组
        tk.Button(right_frame, text="开启实时识别", command=self.start_camera, width=20, bg="#27ae60", fg="white").pack(pady=5)
        tk.Button(right_frame, text="上传图片识别", command=self.upload_image, width=20).pack(pady=5)
        tk.Button(right_frame, text="停止识别", command=self.stop_system, width=20, bg="#c0392b", fg="white").pack(pady=5)

        # 手动发送区
        tk.Label(right_frame, text="\n手动模拟发送标签:", font=("微软雅黑", 10)).pack()
        self.manual_entry = tk.Entry(right_frame, width=22)
        self.manual_entry.insert(0, "recyclable")
        self.manual_entry.pack(pady=5)
        tk.Button(right_frame, text="发送手动指令", command=self.send_manual).pack()

        # 状态日志
        tk.Label(right_frame, text="\n系统日志:", font=("微软雅黑", 10)).pack()
        self.log_box = tk.Text(right_frame, width=30, height=15, font=("Consolas", 9))
        self.log_box.pack(pady=5)

    def log(self, msg):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        self.log_box.insert(tk.END, f"[{current_time}] {msg}\n")
        self.log_box.see(tk.END)

    # 发送 MQTT 指令
    def send_to_cloud(self, label):
        now = time.time()
        if now - self.last_send_time > self.cd_time:
            payload = json.dumps({"label": label})
            self.mqtt_client.publish(TOPIC, payload)
            self.last_send_time = now
            self.log(f"已下发指令: {label}")
            
            # 语音播报
            speech_map = {"recyclable": "可回收物", "food": "厨余垃圾", "harmful": "有害垃圾", "other": "其他垃圾"}
            cn_name = speech_map.get(label, "未知垃圾")
            threading.Thread(target=self.speak, args=(f"检测到{cn_name}，正在为您开启仓门",)).start()
            return True
        return False

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def send_manual(self):
        label = self.manual_entry.get()
        self.send_to_cloud(label)

    # 核心识别逻辑 (通用)
    def perform_inference(self, frame):
        results = self.model(frame, conf=0.5, verbose=False)
        annotated_frame = results[0].plot()

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label_name = self.model.names[cls_id]
                
                if label_name in CLASS_MAPPING:
                    target_label = CLASS_MAPPING[label_name]
                    self.send_to_cloud(target_label)
        
        return annotated_frame

    # 图片识别
    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.stop_system()
            img = cv2.imread(file_path)
            res_img = self.perform_inference(img)
            self.show_on_canvas(res_img)
            self.log("图片识别完成")

    # 实时识别循环
    def start_camera(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            self.is_running = True
            self.update_frame()
            self.log("摄像头已开启")

    def update_frame(self):
        if self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # 识别并画框
                res_frame = self.perform_inference(frame)
                self.show_on_canvas(res_frame)
                self.window.after(10, self.update_frame)

    def show_on_canvas(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk

    def stop_system(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.canvas.delete("all")
        self.log("系统已停止")

# ================= 启动程序 =================
if __name__ == "__main__":
    root = tk.Tk()
    app = WasteBrainUI(root)
    root.mainloop()