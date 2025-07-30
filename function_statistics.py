import sqlite3
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from db_utils import DatabaseManager

class FunctionCallStatistics:
    def __init__(self, db_manager=None):
        """初始化函数调用统计类"""
        self.db_manager = db_manager or DatabaseManager()
    
    def get_function_call_count(self):
        """获取各函数调用次数统计"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT function_name, COUNT(*) as call_count 
            FROM function_calls 
            GROUP BY function_name 
            ORDER BY call_count DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {}
        for row in results:
            stats[row[0]] = row[1]
        
        return stats
    
    def get_function_calls_by_period(self, days=7):
        """获取指定时间段内的函数调用统计"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # 计算指定天数前的时间
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT function_name, COUNT(*) as call_count, 
                   strftime('%Y-%m-%d', called_at) as call_date
            FROM function_calls 
            WHERE strftime('%Y-%m-%d', called_at) >= ?
            GROUP BY function_name, call_date
            ORDER BY call_date
        """, (start_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        # 整理数据格式为: {date: {function_name: count, ...}, ...}
        stats = {}
        for row in results:
            function_name, count, date = row
            if date not in stats:
                stats[date] = {}
            stats[date][function_name] = count
        
        return stats
    
    def get_eating_statistics(self):
        """获取饮食统计信息"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # 获取饮食类别统计
        cursor.execute("""
            SELECT food, COUNT(*) as count 
            FROM eating_records 
            GROUP BY food 
            ORDER BY count DESC
            LIMIT 10
        """)
        
        food_stats = cursor.fetchall()
        
        # 获取每日消费统计
        cursor.execute("""
            SELECT date, SUM(CAST(money AS REAL)) as daily_total 
            FROM eating_records 
            GROUP BY date 
            ORDER BY date
        """)
        
        spending_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "food_stats": food_stats,
            "spending_stats": spending_stats
        }
    
    def generate_function_call_report(self):
        """生成函数调用报告"""
        call_counts = self.get_function_call_count()
        recent_calls = self.get_function_calls_by_period(7)
        
        report = {
            "total_calls": sum(call_counts.values()),
            "function_breakdown": call_counts,
            "recent_activity": recent_calls
        }
        
        return report
    
    def generate_eating_report(self):
        """生成饮食报告"""
        stats = self.get_eating_statistics()
        
        # 计算总消费
        total_spending = sum([float(row[1]) for row in stats["spending_stats"]])
        
        # 计算平均每日消费
        if stats["spending_stats"]:
            avg_daily = total_spending / len(stats["spending_stats"])
        else:
            avg_daily = 0
        
        report = {
            "total_records": len(self.db_manager.get_all_eating_records()),
            "total_spending": total_spending,
            "avg_daily_spending": avg_daily,
            "top_foods": stats["food_stats"],
            "daily_spending": stats["spending_stats"]
        }
        
        return report 