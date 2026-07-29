import cv2
import numpy as np
import os

# 获取 OpenCV 自带的人脸检测模型路径
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
# 初始化人脸检测器
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

def get_images_and_labels(dataset_path):
    """
    辅助函数：从 dataset 目录读取图片并提取标签 (学生数据库ID)
    假设目录结构：dataset/1/img1.jpg, dataset/1/img2.jpg ... (1代表学生ID)
    """
    face_samples = []
    ids = []
    
    # 如果目录不存在，直接返回空
    if not os.path.exists(dataset_path):
        return face_samples, ids

    # 遍历 dataset 下的所有子目录（以学生ID命名的文件夹）
    for student_id_str in os.listdir(dataset_path):
        student_dir = os.path.join(dataset_path, student_id_str)
        if not os.path.isdir(student_dir):
            continue
            
        student_id = int(student_id_str) # LBPH 算法的标签必须是整数
        
        # 遍历该学生的所有图片
        for image_name in os.listdir(student_dir):
            image_path = os.path.join(student_dir, image_name)
            # 读取为灰度图
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
                
            # 检测图中的人脸（确保训练素材只有一张脸的区域）
            faces = face_detector.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                face_samples.append(img[y:y+h, x:x+w])
                ids.append(student_id)
                
    return face_samples, ids

def train_model(dataset_path='api/dataset', model_save_path='trainer.yml'):
    """
    训练模型：读取图片，训练 LBPH 识别器，并保存模型文件
    """
    print(f"开始读取人脸数据，目录: {dataset_path} ...")
    faces, ids = get_images_and_labels(dataset_path)
    
    if len(faces) == 0:
        print("错误：没有找到任何人脸数据，请先采集图片！")
        return False
        
    print(f"提取到 {len(faces)} 个人脸样本，准备训练...")
    
    # 创建 LBPH 人脸识别器
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # 开始训练
    recognizer.train(faces, np.array(ids))
    # 保存训练好的模型
    recognizer.write(model_save_path)
    
    print(f"训练完成！模型已保存至 {model_save_path}")
    return True

def recognize_face(image_frame, model_path='trainer.yml'):
    """
    人脸识别：接收一帧图片，返回识别到的学生ID
    image_frame: OpenCV 格式的图片数组 (BGR)
    """
    if not os.path.exists(model_path):
        return {"error": "模型未找到，请先训练模型"}
        
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)
    
    # 转换为灰度图
    gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))
    
    if len(faces) == 0:
        return {"error": "未检测到人脸"}
        
    # MVP 版本：假设画面中只有一个人（签到时一个人一个人来）
    x, y, w, h = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    
    # 识别！返回预测的 ID 和置信度 (confidence 越小越匹配，通常小于 50 算比较准)
    student_id, confidence = recognizer.predict(face_roi)
    
    if confidence < 70:  # 这个阈值可以根据实际摄像头效果微调
        return {"student_id": student_id, "confidence": confidence}
    else:
        return {"error": "无法确认身份(置信度太低)"}