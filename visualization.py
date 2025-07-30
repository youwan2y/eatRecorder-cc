import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from function_statistics import FunctionCallStatistics
from db_utils import DatabaseManager

class DataVisualizer:
    def __init__(self, stats_manager=None, db_manager=None):
        """初始化数据可视化类"""
        self.db_manager = db_manager or DatabaseManager()
        self.stats_manager = stats_manager or FunctionCallStatistics(self.db_manager)
        
        # 创建图表保存目录
        self.charts_dir = "charts"
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)
    
    def visualize_function_calls(self):
        """可视化函数调用统计"""
        # 获取函数调用统计
        call_stats = self.stats_manager.get_function_call_count()
        
        if not call_stats:
            return {"status": "error", "message": "没有函数调用数据"}
        
        # 创建函数调用条形图
        plt.figure(figsize=(10, 6))
        functions = list(call_stats.keys())
        counts = list(call_stats.values())
        
        plt.bar(functions, counts, color='skyblue')
        plt.xlabel('函数名称')
        plt.ylabel('调用次数')
        plt.title('函数调用统计')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        chart_path = os.path.join(self.charts_dir, f"function_calls_{timestamp}.png")
        plt.savefig(chart_path)
        plt.close()
        
        return {"status": "success", "chart_path": chart_path}
    
    def visualize_eating_stats(self):
        """可视化饮食统计"""
        # 获取饮食统计
        stats = self.stats_manager.get_eating_statistics()
        
        if not stats["food_stats"] and not stats["spending_stats"]:
            return {"status": "error", "message": "没有饮食数据"}
        
        # 创建食物类型饼图
        if stats["food_stats"]:
            plt.figure(figsize=(10, 6))
            foods = [row[0] for row in stats["food_stats"]]
            counts = [row[1] for row in stats["food_stats"]]
            
            plt.pie(counts, labels=foods, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('食物类型分布')
            
            # 保存饼图
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            pie_chart_path = os.path.join(self.charts_dir, f"food_types_{timestamp}.png")
            plt.savefig(pie_chart_path)
            plt.close()
        else:
            pie_chart_path = None
        
        # 创建每日消费折线图
        if stats["spending_stats"]:
            plt.figure(figsize=(12, 6))
            dates = [row[0] for row in stats["spending_stats"]]
            amounts = [float(row[1]) for row in stats["spending_stats"]]
            
            plt.plot(dates, amounts, marker='o', linestyle='-', color='green')
            plt.xlabel('日期')
            plt.ylabel('消费金额')
            plt.title('每日消费趋势')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # 保存折线图
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            line_chart_path = os.path.join(self.charts_dir, f"daily_spending_{timestamp}.png")
            plt.savefig(line_chart_path)
            plt.close()
        else:
            line_chart_path = None
        
        return {
            "status": "success", 
            "pie_chart_path": pie_chart_path, 
            "line_chart_path": line_chart_path
        }
    
    def generate_function_call_chart(self):
        """生成函数调用图表并返回路径"""
        # 记录函数调用
        self.db_manager.log_function_call("generate_function_call_chart", {})
        
        return self.visualize_function_calls()
    
    def generate_eating_charts(self):
        """生成饮食统计图表并返回路径"""
        # 记录函数调用
        self.db_manager.log_function_call("generate_eating_charts", {})
        
        return self.visualize_eating_stats() 