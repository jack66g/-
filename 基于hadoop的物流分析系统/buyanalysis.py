import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import shutil
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class EnhancedHadoopManager:
    def __init__(self):
        self.hadoop_home = r"C:\hadoop\hadoop-3.1.3"
        self.hdfs_cmd = os.path.join(self.hadoop_home, "bin", "hdfs.cmd")
        self.base_hdfs_path = "/logistics_bigdata"
        self.temp_dir = os.path.abspath("./analysis_temp")
        self.cities = [
            '北京', '上海', '广州', '深圳', '东莞', '杭州', 
            '宁波', '温州', '南京', '苏州', '无锡', '成都',
            '绵阳', '宜宾', '武汉', '宜昌', '襄阳', '西安',
            '咸阳', '青岛', '济南', '烟台', '福州', '厦门', '泉州'
        ]
        self._prepare_env()
        self._prepare_temp_dir()

    def _prepare_env(self):
        os.environ['HADOOP_HOME'] = self.hadoop_home
        os.environ['PATH'] = f"{self.hadoop_home}/bin;{os.environ['PATH']}"

    def _prepare_temp_dir(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

    def run_hdfs_command(self, command):
        try:
            result = subprocess.run(
                [self.hdfs_cmd, "dfs"] + command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                shell=True,
                timeout=30
            )
            return True
        except Exception as e:
            print(f"命令执行失败: {str(e)}")
            return False

    def download_city_data(self, city, year):
        hdfs_dir = "historical" if year == 2023 else "forecast"
        hdfs_path = f"{self.base_hdfs_path}/{hdfs_dir}/orders/{city}_orders_{year}.csv"
        local_path = os.path.join(self.temp_dir, f"{city}_{year}.csv")
        
        if self.run_hdfs_command(["-get", hdfs_path, local_path]):
            return local_path
        return None

def generate_monthly_plots(city, df, year, output_dir):
    df['date'] = pd.to_datetime(df['date'])
    monthly = df.resample('M', on='date')['orders'].sum().reset_index()
    monthly['month'] = monthly['date'].dt.month
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=monthly, x='month', y='orders', 
                marker='o', linewidth=2.5, markersize=8)
    
    title_type = "实际数据" if year == 2023 else "LSTM预测数据"
    plt.title(f"{city} {year}年订单量趋势（{title_type}）")
    plt.xlabel("月份")
    plt.ylabel("订单量")
    plt.xticks(range(1,13))
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 创建年份目录
    year_dir = os.path.join(output_dir, str(year))
    os.makedirs(year_dir, exist_ok=True)
    
    filename = f"{city}_orders_{year}.png"
    plt.savefig(os.path.join(year_dir, filename), bbox_inches='tight')
    plt.close()

def main():
    hadoop = EnhancedHadoopManager()
    output_root = "./analysis_results"
    
    for year in [2023, 2024]:
        print(f"\n正在处理{year}年数据...")
        for city in hadoop.cities:
            local_file = hadoop.download_city_data(city, year)
            if not local_file or not os.path.exists(local_file):
                print(f"⚠️ 文件缺失：{city} {year}")
                continue
            
            try:
                df = pd.read_csv(local_file)
                generate_monthly_plots(city, df, year, output_root)
                print(f"✓ 生成 {city} {year} 趋势图")
            except Exception as e:
                print(f"❌ 处理失败 {city} {year}: {str(e)}")
            finally:
                if os.path.exists(local_file):
                    os.remove(local_file)

    print("\n✅ 分析完成！结果保存在以下目录：")
    print(f"2023年图表：{os.path.abspath(os.path.join(output_root, '2023'))}")
    print(f"2024年图表：{os.path.abspath(os.path.join(output_root, '2024'))}")

if __name__ == "__main__":
    main()