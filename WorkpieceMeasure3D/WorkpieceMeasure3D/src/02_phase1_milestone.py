import open3d as o3d
import numpy as np

# ==========================================
# Step 2: 仿真数据生成器
# ==========================================
def generate_simulated_point_cloud(shape_type="box", add_noise=True, add_outliers=True, cut_half=True):
    print(f"\n[Step 2] 正在生成仿真工业点云，当前模式: {shape_type}")
    
    if shape_type == "box":
        mesh = o3d.geometry.TriangleMesh.create_box(width=1.2, height=0.8, depth=0.5)
        true_dims = [1.2, 0.8, 0.5]
    elif shape_type == "cylinder":
        mesh = o3d.geometry.TriangleMesh.create_cylinder(radius=0.3, height=1.5)
        true_dims = {"radius": 0.3, "length": 1.5}
    
    # 稍微增加点云密度，让视觉效果更好
    pcd = mesh.sample_points_uniformly(number_of_points=30000)
    points = np.asarray(pcd.points)

    # 2. 模拟真实的单侧激光扫描盲区 (只保留迎着雷达的几个面，背侧全空)
    if cut_half:
        if shape_type == "box":
            # 真实模拟：只能看到顶面(z>0.24)、前面(y>0.39)或右面(x>0.59)
            mask = (points[:, 2] > 0.24) | (points[:, 1] > 0.39) | (points[:, 0] > 0.59)
            points = points[mask]
        else:
            # 圆柱体：只能扫到上半个曲面 (Y轴大于0的部分)
            points = points[points[:, 1] > 0.0]
        print("   -> 已模拟真实激光雷达视角 (剔除背侧盲区点云)")

    # 3. 注入高斯噪声
    if add_noise:
        noise = np.random.normal(0, 0.005, points.shape) 
        points += noise

    # 4. 注入游离飞点
    if add_outliers:
        bbox = pcd.get_axis_aligned_bounding_box()
        min_b, max_b = bbox.get_min_bound(), bbox.get_max_bound()
        outliers = np.random.uniform(low=min_b - 0.1, high=max_b + 0.1, size=(1000, 3))
        points = np.vstack((points, outliers))

    noisy_pcd = o3d.geometry.PointCloud()
    noisy_pcd.points = o3d.utility.Vector3dVector(points)
    noisy_pcd.paint_uniform_color([0.6, 0.6, 0.6]) 
    
    return noisy_pcd, true_dims

# ==========================================
# Step 3: 预处理清洗模块
# ==========================================
def preprocess_point_cloud(pcd):
    """
    点云清洗：体素下采样 + 统计滤波
    """
    print("\n[Step 3] 启动点云预处理清洗...")
    
    # 1. 体素下采样 (降维提速)
    voxel_size = 0.01 # 1cm 的体素格子
    pcd_down = pcd.voxel_down_sample(voxel_size)
    print(f"   -> 体素下采样完成，点数: {len(pcd.points)} -> {len(pcd_down.points)}")

    # 2. 统计滤波 (SOR 去除游离飞点)
    # nb_neighbors: 算多少个邻居, std_ratio: 标准差乘数阈值
    pcd_clean, ind = pcd_down.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    print(f"   -> 统计滤波(SOR)完成，去除了 {len(pcd_down.points) - len(pcd_clean.points)} 个飞点噪点")
    
    # 顺便把清洗后的点云涂成浅蓝色，方便肉眼区分
    pcd_clean.paint_uniform_color([0.2, 0.6, 0.8])
    return pcd_clean

# ==========================================
# Step 4: 核心尺寸解算 (终极抗噪版)
# ==========================================
def calculate_box_dimensions(pcd_clean):
    print("\n[Step 4] 启动长方体尺寸解算 (RANSAC + 百分位数抗噪)...")
    points = np.asarray(pcd_clean.points)
    
    # 1. 双重 RANSAC 提取正交主轴
    plane1, inliers1 = pcd_clean.segment_plane(distance_threshold=0.015, ransac_n=3, num_iterations=2000)
    normal1 = np.array(plane1[:3])
    normal1 /= np.linalg.norm(normal1)
    
    outlier_cloud = pcd_clean.select_by_index(inliers1, invert=True)
    plane2, inliers2 = outlier_cloud.segment_plane(distance_threshold=0.015, ransac_n=3, num_iterations=2000)
    normal2 = np.array(plane2[:3])
    
    # 施密特正交化，确保绝对垂直
    normal2 = normal2 - np.dot(normal2, normal1) * normal1
    normal2 /= np.linalg.norm(normal2)
    normal3 = np.cross(normal1, normal2)
    
    # 2. 投影计算尺寸
    proj1 = np.dot(points, normal1)
    proj2 = np.dot(points, normal2)
    proj3 = np.dot(points, normal3)
    
    # 【核心优化】：使用 0.5% 和 99.5% 的百分位数，彻底无视漏网飞点的拉扯！
    p_min1, p_max1 = np.percentile(proj1, 0.5), np.percentile(proj1, 99.5)
    p_min2, p_max2 = np.percentile(proj2, 0.5), np.percentile(proj2, 99.5)
    p_min3, p_max3 = np.percentile(proj3, 0.5), np.percentile(proj3, 99.5)
    
    dim1 = p_max1 - p_min1
    dim2 = p_max2 - p_min2
    dim3 = p_max3 - p_min3
    dims = sorted([dim1, dim2, dim3], reverse=True)
    
    print("   -> [结算完成] 长方体计算结果:")
    print(f"      测量长度 (L) = {dims[0]:.4f} m")
    print(f"      测量宽度 (W) = {dims[1]:.4f} m")
    print(f"      测量高度 (H) = {dims[2]:.4f} m")
    
    # 3. 重构完美贴合的 OBB 包围盒
    center_exact = ((p_max1 + p_min1)/2 * normal1 + 
                    (p_max2 + p_min2)/2 * normal2 + 
                    (p_max3 + p_min3)/2 * normal3)
    R = np.column_stack((normal1, normal2, normal3))
    obb = o3d.geometry.OrientedBoundingBox(center_exact, R, np.array([dim1, dim2, dim3]))
    obb.color = (1, 0, 0) # 红色
    return obb

def calculate_cylinder_dimensions(pcd_clean):
    print("\n[Step 4] 启动残缺圆柱体尺寸解算 (降维拟合 + 轴向矫正)...")
    points = np.asarray(pcd_clean.points)
    
    # 1. PCA 提取主轴 (对于半圆柱，主轴依然平行于母线，这点是稳定的)
    mean, cov = pcd_clean.compute_mean_and_covariance()
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    u = eigenvectors[:, 2] # 最大特征值对应的向量即为圆柱长度方向
    v = eigenvectors[:, 1]
    w = eigenvectors[:, 0]
    
    # 2. 2D 截面投影与最小二乘拟合半径
    points_centered = points - mean
    x_2d = np.dot(points_centered, v)
    y_2d = np.dot(points_centered, w)
    
    B = x_2d**2 + y_2d**2
    A = np.c_[x_2d, y_2d, np.ones_like(x_2d)]
    W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    
    xc, yc = W[0]/2, W[1]/2
    radius = np.sqrt(W[2] + xc**2 + yc**2)
    
    # 3. 长度计算 (沿主轴 u 投影，使用百分位数抗噪)
    proj_u = np.dot(points_centered, u)
    length = np.percentile(proj_u, 99.5) - np.percentile(proj_u, 0.5)
    
    print("   -> [结算完成] 残缺圆柱体计算结果:")
    print(f"      测量长度 (L) = {length:.4f} m")
    print(f"      测量半径 (R) = {radius:.4f} m")
    
    # 4. 重构圆柱体专属的修正版包围盒 (不再倾斜！)
    center_u = (np.percentile(proj_u, 99.5) + np.percentile(proj_u, 0.5)) / 2
    # 将中心移回到拟合出的圆心位置
    center_exact = mean + center_u * u + xc * v + yc * w
    
    R_cyl = np.column_stack((u, v, w))
    # 理论包围盒的长宽高：长=length, 宽=2*R, 高=2*R
    obb = o3d.geometry.OrientedBoundingBox(center_exact, R_cyl, np.array([length, radius*2, radius*2]))
    obb.color = (0, 1, 0) # 绿色
    return obb

# ==========================================
# 阶段一：主运行流水线
# ==========================================
def main():
    print("="*50)
    print(" 阶段一里程碑：尺寸自动测量算法管线测试 ")
    print("="*50)
    
    # ---------- 测试 1: 长方体 ----------
    print("\n>>> 开始测试工件 A: 长方体")
    noisy_box, true_box_dims = generate_simulated_point_cloud("box")
    clean_box = preprocess_point_cloud(noisy_box)
    box_obb = calculate_box_dimensions(clean_box)
    
    print(f"\n[误差对比] 长方体真实尺寸: {true_box_dims}")
    # 可视化长方体结果 (关闭时会继续执行圆柱体测试)
    print("\n提示：请关闭弹出的 3D 窗口以继续测试圆柱体...")
    o3d.visualization.draw_geometries([clean_box, box_obb], window_name="长方体测试结果")
    
    # ---------- 测试 2: 残缺圆柱体 ----------
    print("\n" + "="*50)
    print(">>> 开始测试工件 B: 残缺圆柱体")
    noisy_cylinder, true_cyl_dims = generate_simulated_point_cloud("cylinder")
    clean_cylinder = preprocess_point_cloud(noisy_cylinder)
    cyl_obb = calculate_cylinder_dimensions(clean_cylinder)
    
    print(f"\n[误差对比] 圆柱体真实尺寸: 半径 {true_cyl_dims['radius']}, 长度 {true_cyl_dims['length']}")
    # 可视化圆柱体结果
    o3d.visualization.draw_geometries([clean_cylinder, cyl_obb], window_name="残缺圆柱体测试结果")
    
    print("\n[里程碑达成] 阶段一所有测试顺利通关！")

if __name__ == "__main__":
    main()