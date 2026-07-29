import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore
import os
import subprocess
import sys

# 设置标准流编码
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class EnhancedDataGenerator:
    def __init__(self):
        self.cities = ['北京', '上海', '广州', '深圳', '成都', '重庆', '武汉', '西安']
        self.city_factors = {
            '北京': 1.35, '上海': 1.3, '广州': 1.2, '深圳': 1.15,
            '成都': 1.0, '重庆': 0.95, '武汉': 0.9, '西安': 0.85
        }
        self.days_in_year = 365
        self.scale_factor = 5  # 数据增强系数

    def _create_lstm_model(self, input_shape):
        model = Sequential([
            LSTM(128, input_shape=input_shape, return_sequences=True),
            LSTM(64, return_sequences=True),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def _generate_city_dates(self, year):
        """生成日期与城市的全组合数据"""
        dates = pd.date_range(f'{year}-01-01', f'{year}-12-31')
        return pd.DataFrame({
            'date': np.repeat(dates, len(self.cities)),
            'city': np.tile(self.cities, len(dates))
        })

    def generate_orders(self, year):
        base_data = self._generate_city_dates(year)
        n = len(base_data)
        
        # 生成基础订单量（增强数据量）
        base_orders = np.random.normal(800, 200, n * self.scale_factor)
        seasonal_effect = np.sin(np.linspace(0, 4*np.pi, n * self.scale_factor))
        
        # 应用城市因子和时间效应
        orders = []
        for i in range(n * self.scale_factor):
            city = base_data['city'][i % n]
            day_of_year = (i // len(self.cities)) % self.days_in_year
            city_factor = self.city_factors[city]
            season = 1 + 0.3 * np.sin(2*np.pi*day_of_year/self.days_in_year)
            noise = np.random.normal(0, 50)
            orders.append(
                int(city_factor * season * (base_orders[i] + seasonal_effect[i]*100 + noise))
            )
        
        # LSTM预测处理
        if year == 2024:
            model = self._create_lstm_model((30, 1))
            # 使用历史最后30天数据作为预测基础
            train_data = np.array(orders[-30*self.scale_factor:]).reshape(-1, 30, 1)
            forecast = model.predict(train_data).flatten()
            orders[-len(forecast):] = forecast
        
        return pd.DataFrame({
            'date': np.repeat(base_data['date'], self.scale_factor),
            'city': np.tile(base_data['city'], self.scale_factor),
            'orders': np.clip(orders, 300, 2000).astype(int)
        })[:n*self.scale_factor]  # 确保数据对齐

    def generate_revenue(self, year):
        base_data = self._generate_city_dates(year)
        n = len(base_data)
        
        # 城市专属收入参数
        city_params = {
            '北京': (10.6, 0.35), '上海': (10.5, 0.3),
            '广州': (10.4, 0.4), '深圳': (10.4, 0.35),
            '成都': (10.2, 0.5), '重庆': (10.1, 0.45),
            '武汉': (10.0, 0.5), '西安': (9.8, 0.6)
        }
        
        revenues = []
        for _ in range(self.scale_factor):
            for _, row in base_data.iterrows():
                mu, sigma = city_params[row['city']]
                if year == 2024: mu += 0.2  # 预测增长
                log_rev = np.random.normal(mu, sigma)
                revenues.append(np.exp(log_rev))
        
        return pd.DataFrame({
            'date': np.repeat(base_data['date'], self.scale_factor),
            'city': np.tile(base_data['city'], self.scale_factor),
            'revenue': np.clip(np.round(revenues, 2), 20000, 200000)
        })[:n*self.scale_factor]

    def generate_heatmap(self, year):
        base_data = self._generate_city_dates(year)
        n = len(base_data)
        
        heat_values = []
        for _ in range(self.scale_factor):
            for idx, row in base_data.iterrows():
                base = 1000 if year == 2023 else 1100
                city_idx = self.cities.index(row['city'])
                weekday = row['date'].weekday()
                # 城市基础 + 周末效应 + 周期性波动
                heat = base * (1 + city_idx*0.05) 
                heat *= 1.5 if weekday >= 5 else 1.0
                heat += 200 * np.sin(2*np.pi*idx/len(base_data))
                heat_values.append(int(np.random.normal(heat, 150)))
        
        return pd.DataFrame({
            'date': np.repeat(base_data['date'], self.scale_factor),
            'city': np.tile(base_data['city'], self.scale_factor),
            'heat': np.clip(heat_values, 500, 3000)
        })[:n*self.scale_factor]

class HadoopManager:
    def __init__(self):
        self.hadoop_home = r"C:\hadoop\hadoop-3.1.3"
        self.hdfs_cmd = os.path.join(self.hadoop_home, "bin", "hdfs.cmd")
        self.base_hdfs_path = "/logistics"

    def run_hdfs_command(self, command, operation_name):
        try:
            result = subprocess.run(
                [self.hdfs_cmd, "dfs"] + command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                shell=True
            )
            print(f"{operation_name}成功: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {operation_name}失败")
            print("=== 错误信息 ===")
            print(e.stderr if e.stderr else "无错误输出")
            return False

    def prepare_hdfs(self):
        self.run_hdfs_command(["-rm", "-r", self.base_hdfs_path], "清理旧目录")
        paths = [
            f"{self.base_hdfs_path}/historical",
            f"{self.base_hdfs_path}/forecast"
        ]
        for path in paths:
            if self.run_hdfs_command(["-mkdir", "-p", path], f"创建目录 {path}"):
                print(f"目录 {path} 已就绪")
            else:
                raise Exception(f"目录创建失败: {path}")

    def upload_to_hdfs(self, local_path, hdfs_path):
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"本地文件不存在: {local_path}")
        if self.run_hdfs_command(["-put", local_path, hdfs_path], f"上传 {os.path.basename(local_path)}"):
            print(f"文件已上传至 HDFS: {hdfs_path}")
            return True
        return False

if __name__ == "__main__":
    hadoop = HadoopManager()
    hadoop.prepare_hdfs()
    
    generator = EnhancedDataGenerator()
    
    # 生成增强数据集
    datasets = {
        '/historical/orders.csv': generator.generate_orders(2023),
        '/forecast/orders_2024.csv': generator.generate_orders(2024),
        '/historical/revenue.csv': generator.generate_revenue(2023),
        '/forecast/revenue_2024.csv': generator.generate_revenue(2024),
        '/historical/heatmap.csv': generator.generate_heatmap(2023),
        '/forecast/heatmap_2024.csv': generator.generate_heatmap(2024)
    }

    for hdfs_path, df in datasets.items():
        local_path = os.path.abspath(f"temp_{os.path.basename(hdfs_path)}")
        df.to_csv(local_path, index=False, encoding='utf-8')
        hadoop.upload_to_hdfs(local_path, f"{hadoop.base_hdfs_path}{hdfs_path}")
        os.remove(local_path)
        print(f"已处理: {hdfs_path}")

    print("✅ 增强版数据已成功上传至HDFS")