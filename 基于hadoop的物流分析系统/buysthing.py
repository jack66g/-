import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os
import subprocess
import sys

# 设置标准流编码
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class MegaDataGenerator:
    def __init__(self):
        # 扩展省份和城市（30个城市）
        self.provinces = {
            '北京': ['北京'],
            '上海': ['上海'],
            '广东': ['广州', '深圳', '东莞'],
            '浙江': ['杭州', '宁波', '温州'],
            '江苏': ['南京', '苏州', '无锡'],
            '四川': ['成都', '绵阳', '宜宾'],
            '湖北': ['武汉', '宜昌', '襄阳'],
            '陕西': ['西安', '咸阳'],
            '山东': ['青岛', '济南', '烟台'],
            '福建': ['福州', '厦门', '泉州']
        }
        self.cities = [city for province in self.provinces.values() for city in province]
        
        # 城市因子（根据城市等级设置）
        self.city_factors = {
            '北京': 1.5, '上海': 1.45,
            '广州': 1.35, '深圳': 1.3, '东莞': 1.1,
            '杭州': 1.25, '宁波': 1.15, '温州': 1.05,
            '南京': 1.2, '苏州': 1.25, '无锡': 1.1,
            '成都': 1.2, '绵阳': 0.95, '宜宾': 0.9,
            '武汉': 1.15, '宜昌': 0.98, '襄阳': 0.93,
            '西安': 1.1, '咸阳': 0.92,
            '青岛': 1.15, '济南': 1.05, '烟台': 0.99,
            '福州': 1.05, '厦门': 1.1, '泉州': 0.97
        }
        self.days_in_year = 365
        self.scale_factor = 15  # 增强数据量系数

    def _create_lstm_model(self, input_shape):
        model = Sequential([
            LSTM(256, input_shape=input_shape, return_sequences=True),
            LSTM(128, return_sequences=True),
            LSTM(64),
            Dense(32, activation='relu'),
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

    def generate_city_orders(self, city, year):
        """为单个城市生成订单数据"""
        base_dates = pd.date_range(f'{year}-01-01', f'{year}-12-31')
        n_days = len(base_dates)
        
        # 生成基础数据（增强15倍）
        base_orders = np.random.normal(1000, 300, n_days * self.scale_factor)
        seasonal_effect = np.sin(np.linspace(0, 4*np.pi, n_days * self.scale_factor))
        
        orders = []
        for i in range(n_days * self.scale_factor):
            day_of_year = i % self.days_in_year
            city_factor = self.city_factors[city]
            season = 1 + 0.4 * np.sin(2*np.pi*day_of_year/self.days_in_year)
            noise = np.random.normal(0, 80)
            orders.append(
                int(city_factor * season * (base_orders[i] + seasonal_effect[i]*150 + noise)))
        
        # LSTM预测处理（仅2024年）
        if year == 2024:
            model = self._create_lstm_model((60, 1))  # 使用60天历史数据
            # 取最后60天数据作为预测基础
            train_data = np.array(orders[-60*self.scale_factor:]).reshape(-1, 60, 1)
            forecast = model.predict(train_data).flatten()
            orders[-len(forecast):] = forecast
        
        return pd.DataFrame({
            'date': np.repeat(base_dates, self.scale_factor),
            'city': city,
            'orders': np.clip(orders, 500, 5000).astype(int)
        })[:n_days*self.scale_factor]

    def generate_all_orders(self, year):
        """生成所有城市数据并保存单独文件"""
        for city in self.cities:
            df = self.generate_city_orders(city, year)
            yield city, df

class HadoopManager:
    def __init__(self):
        self.hadoop_home = r"C:\hadoop\hadoop-3.1.3"
        self.hdfs_cmd = os.path.join(self.hadoop_home, "bin", "hdfs.cmd")
        self.base_hdfs_path = "/logistics_bigdata"

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
            f"{self.base_hdfs_path}/historical/orders",
            f"{self.base_hdfs_path}/forecast/orders"
        ]
        for path in paths:
            if self.run_hdfs_command(["-mkdir", "-p", path], f"创建目录 {path}"):
                print(f"目录 {path} 已就绪")
            else:
                raise Exception(f"目录创建失败: {path}")

    def upload_city_file(self, local_path, hdfs_dir, filename):
        hdfs_path = f"{self.base_hdfs_path}/{hdfs_dir}/{filename}"
        return self.run_hdfs_command(["-put", local_path, hdfs_path], f"上传 {filename}")

if __name__ == "__main__":
    hadoop = HadoopManager()
    hadoop.prepare_hdfs()
    
    generator = MegaDataGenerator()
    
    # 生成并上传数据
    for year in [2023, 2024]:
        directory = "historical" if year == 2023 else "forecast"
        for city, df in generator.generate_all_orders(year):
            filename = f"{city}_orders_{year}.csv"
            local_path = os.path.abspath(filename)
            df.to_csv(local_path, index=False, encoding='utf-8')
            hadoop.upload_city_file(local_path, f"{directory}/orders", filename)
            os.remove(local_path)
            print(f"已处理: {city} {year}年数据")

    print("✅ 增强大数据集已成功上传至HDFS")