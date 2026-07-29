import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import shutil

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class HadoopManager:
    def __init__(self):
        self.hadoop_home = r"C:\hadoop\hadoop-3.1.3"
        self.hdfs_cmd = os.path.join(self.hadoop_home, "bin", "hdfs.cmd")
        self.base_hdfs_path = "/logistics"
        self.temp_dir = os.path.abspath("./hadoop_temp")
        self._prepare_temp_dir()
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
        except subprocess.CalledProcessError:
            return False
        except subprocess.TimeoutExpired:
            return False

    def download_from_hdfs(self, hdfs_path, local_name):
        local_path = os.path.join(self.temp_dir, f"{local_name}.csv")
        if self.run_hdfs_command(["-get", hdfs_path, local_path]):
            if os.path.exists(local_path):
                return local_path
        return None

def load_data(hadoop, mapping):
    local_files = {}
    for key, path in mapping.items():
        full_hdfs_path = f"{hadoop.base_hdfs_path}{path}"
        local_path = hadoop.download_from_hdfs(full_hdfs_path, key)
        if not local_path:
            raise FileNotFoundError(f"文件下载失败: {full_hdfs_path}")
        local_files[key] = local_path
    return local_files

def plot_orders_comparison(hist_path, forecast_path):
    # 2023实际订单量
    df_2023 = pd.read_csv(hist_path)
    orders_2023 = df_2023.groupby("city")["orders"].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(12,6))
    plt.bar(orders_2023.index, orders_2023, alpha=0.8, color='#1f77b4')
    plt.title("2023年各城市实际订单量")
    plt.xlabel("城市")
    plt.ylabel("订单总量")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig("orders_2023.png")
    plt.close()

    # 2024预测订单量
    df_2024 = pd.read_csv(forecast_path)
    orders_2024 = df_2024.groupby("city")["orders"].sum().reindex(orders_2023.index)
    
    plt.figure(figsize=(12,6))
    plt.bar(orders_2024.index, orders_2024, alpha=0.8, color='#ff7f0e')
    plt.title("2024年LSTM预测各城市订单量")
    plt.xlabel("城市")
    plt.ylabel("预测订单总量")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig("orders_2024.png")
    plt.close()

def plot_revenue_comparison(hist_path, forecast_path):
    # 2023实际收入
    df_2023 = pd.read_csv(hist_path)
    total_2023 = df_2023["revenue"].sum() / 1e8
    revenue_2023 = df_2023.groupby("city")["revenue"].sum()
    
    plt.figure(figsize=(10,10))
    plt.pie(revenue_2023, labels=revenue_2023.index, autopct="%1.1f%%", 
            startangle=90, colors=sns.color_palette("pastel"))
    plt.title(f"2023年货运收入分布（总计：{total_2023:.2f}亿元）")
    plt.savefig("revenue_2023.png")
    plt.close()

    # 2024预测收入
    df_2024 = pd.read_csv(forecast_path)
    total_2024 = df_2024["revenue"].sum() / 1e8
    revenue_2024 = df_2024.groupby("city")["revenue"].sum()
    
    plt.figure(figsize=(10,10))
    plt.pie(revenue_2024, labels=revenue_2024.index, autopct="%1.1f%%", 
            startangle=90, colors=sns.color_palette("pastel"))
    plt.title(f"2024年LSTM预测货运收入（预测总计：{total_2024:.2f}亿元）")
    plt.savefig("revenue_2024.png")
    plt.close()

def plot_heatmap_comparison(hist_path, forecast_path):
    # 2023实际热力图
    df_2023 = pd.read_csv(hist_path)
    df_2023["month"] = pd.to_datetime(df_2023["date"]).dt.month
    heat_2023 = df_2023.pivot_table(index="city", columns="month", values="heat", aggfunc="mean")
    
    plt.figure(figsize=(12,6))
    sns.heatmap(heat_2023, annot=True, fmt=".0f", cmap="YlOrRd", 
               cbar_kws={'label': '热度值'})
    plt.title("2023年月度城市热度分布")
    plt.xlabel("月份")
    plt.ylabel("城市")
    plt.tight_layout()
    plt.savefig("heatmap_2023.png")
    plt.close()

    # 2024预测热力图
    df_2024 = pd.read_csv(forecast_path)
    df_2024["month"] = pd.to_datetime(df_2024["date"]).dt.month
    heat_2024 = df_2024.pivot_table(index="city", columns="month", values="heat", aggfunc="mean")
    
    plt.figure(figsize=(12,6))
    sns.heatmap(heat_2024, annot=True, fmt=".0f", cmap="YlOrRd", 
               cbar_kws={'label': '预测热度值'})
    plt.title("2024年LSTM预测月度城市热度")
    plt.xlabel("月份")
    plt.ylabel("城市")
    plt.tight_layout()
    plt.savefig("heatmap_2024.png")
    plt.close()

if __name__ == "__main__":
    hadoop = HadoopManager()
    paths = {
        "orders_hist": "/historical/orders.csv",
        "orders_forecast": "/forecast/orders_2024.csv",
        "revenue_hist": "/historical/revenue.csv",
        "revenue_forecast": "/forecast/revenue_2024.csv",
        "heat_hist": "/historical/heatmap.csv",
        "heat_forecast": "/forecast/heatmap_2024.csv",
    }
    try:
        files = load_data(hadoop, paths)
        plot_orders_comparison(files["orders_hist"], files["orders_forecast"])
        plot_revenue_comparison(files["revenue_hist"], files["revenue_forecast"])
        plot_heatmap_comparison(files["heat_hist"], files["heat_forecast"])
        print("✅ 成功生成6张图表：")
        print("订单分析：orders_2023.png, orders_2024.png")
        print("收入分析：revenue_2023.png, revenue_2024.png")
        print("热度分析：heatmap_2023.png, heatmap_2024.png")
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        shutil.rmtree(hadoop.temp_dir, ignore_errors=True)