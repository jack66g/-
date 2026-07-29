import open3d as o3d
import numpy as np
import os

print("="*50)
print(" 阶段二：真实物理点云抗噪与测量管线测试 ")
print("="*50)

# 直接指定相对于当前运行终端（根目录）的正确路径
scene_path = "data/fragment.pcd"
bunny_path = "data/BunnyMesh.ply"

# ==========================================
# 实验 A：处理复杂的真实房间场景 
# (核心目的：模拟“剔除传送带背景”与“实物提取”)
# ==========================================
def experiment_real_scene():
    print("\n>>> 开始实验 A：真实场景背景剔除 (模拟剥离传送带)")
    if not os.path.exists(scene_path):
        print(f" [报错] 找不到场景文件: {scene_path}")
        return

    # 1. 读取真实点云
    pcd = o3d.io.read_point_cloud(scene_path)
    print(f" [*] 原始数据加载成功，总点数: {len(pcd.points)}")
    
    # 2. 体素下采样 (真实数据往往极其庞大，必须先降维提速)
    pcd_down = pcd.voxel_down_sample(voxel_size=0.02)
    print(f" [*] 体素下采样完成，保留点数: {len(pcd_down.points)}")

    # 3. 【核心算法：RANSAC 强行剥离背景底面】
    # 在工厂里，面积最大的平面通常就是“传送带履带”或“车间地面”
    print(" [*] 正在启动 RANSAC 算法识别并剥离主平面...")
    # distance_threshold: 允许的平面起伏误差 (2cm)
    plane_model, inliers = pcd_down.segment_plane(distance_threshold=0.02, ransac_n=3, num_iterations=1000)
    
    # 提取地面/传送带点云
    belt_cloud = pcd_down.select_by_index(inliers)
    belt_cloud.paint_uniform_color([0.5, 0.5, 0.5]) # 把底面涂成低调的灰色
    
    # 提取除地面外的“有效工件点云”
    object_cloud = pcd_down.select_by_index(inliers, invert=True)
    object_cloud.paint_uniform_color([0.2, 0.8, 0.2]) # 有效物体涂成亮绿色
    
    # 4. 对提取出的物体进行“成簇飞点”清洗 (统计滤波)
    object_clean, _ = object_cloud.remove_statistical_outlier(nb_neighbors=30, std_ratio=1.0)
    
    print(" [结果] 背景剥离成功！请在 3D 窗口中查看 (灰色为被剔除的底面，绿色为提取的有效物体)")
    print(" 提示：关闭当前 3D 窗口后，将自动进入下一个兔子实验...")
    o3d.visualization.draw_geometries([belt_cloud, object_clean], window_name="实物实验 A：传送带背景剔除算法验证")

# ==========================================
# 实验 B：处理非标准形态的复杂实物 (斯坦福兔子)
# (核心目的：验证咱们的包围盒算法在面对奇形怪状物体时的紧凑度)
# ==========================================
def experiment_bunny():
    print("\n" + "="*50)
    print(">>> 开始实验 B：复杂实物边界测量 (斯坦福兔子)")
    if not os.path.exists(bunny_path):
        print(f" [报错] 找不到兔子文件: {bunny_path}")
        return

    # 1. 读取并放大兔子 (兔子原始坐标只有 0.1 米级别，放大方便观察)
    pcd = o3d.io.read_point_cloud(bunny_path)
    pcd.scale(10.0, center=pcd.get_center())
    pcd.paint_uniform_color([0.8, 0.6, 0.2]) # 涂成土黄色
    print(f" [*] 兔子加载成功，点数: {len(pcd.points)}")

    # 2. 模拟真实扫描误差，主动给兔子注入一点高斯噪声
    points = np.asarray(pcd.points)
    points += np.random.normal(0, 0.05, points.shape)
    pcd.points = o3d.utility.Vector3dVector(points)

    # 3. 滤波清洗
    pcd_clean, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

    # 4. 提取最小定向包围盒 (OBB) - 看看它能不能把两只耳朵完美包住
    print(" [*] 正在计算实物最小定向包围盒...")
    obb = pcd_clean.get_oriented_bounding_box()
    obb.color = (1, 0, 0) # 包围盒设为红色
    
    extents = obb.extent
    dims = sorted(extents, reverse=True)
    print(f" [结果] 实物计算完毕！长宽高尺寸为:")
    print(f"        L = {dims[0]:.3f}, W = {dims[1]:.3f}, H = {dims[2]:.3f}")
    
    o3d.visualization.draw_geometries([pcd_clean, obb], window_name="实物实验 B：复杂边界的紧凑测量")

if __name__ == "__main__":
    experiment_real_scene()
    experiment_bunny()
    print("\n[阶段二里程碑达成] 真实物理数据管线测试全部通关！")