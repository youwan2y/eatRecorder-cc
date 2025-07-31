import sqlite3
import json
import os
import traceback
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='agent_records.db'):
        self.db_path = db_path
        # 确保数据库目录存在
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self.init_db()
        print(f"数据库初始化完成: {os.path.abspath(db_path)}")
    
    def init_db(self):
        """初始化数据库表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建记录表，用于存储用户饮食记录
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS eating_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                food TEXT,
                money TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建函数调用日志表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS function_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT,
                arguments TEXT,
                called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            print("数据库表结构初始化成功")
        except Exception as e:
            print(f"初始化数据库出错: {str(e)}")
            print(traceback.format_exc())
    
    def log_function_call(self, function_name, arguments):
        """记录函数调用到数据库"""
        try:
            print(f"记录函数调用: {function_name}, 参数: {arguments}")
            
            # 确保参数是可序列化的
            if not isinstance(arguments, dict):
                arguments = {"data": str(arguments)}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 将参数转换为JSON字符串
            args_json = json.dumps(arguments, ensure_ascii=False)
            
            cursor.execute(
                "INSERT INTO function_calls (function_name, arguments) VALUES (?, ?)",
                (function_name, args_json)
            )
            
            conn.commit()
            conn.close()
            print(f"函数调用已记录到数据库: {function_name}")
            return True
        except Exception as e:
            print(f"记录函数调用失败: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def save_eating_record(self, date, food, money):
        """保存饮食记录到数据库"""
        try:
            print(f"保存饮食记录: 日期={date}, 食物={food}, 金额={money}")
            
            # 参数验证
            if not date or not food or not money:
                print("保存饮食记录失败: 参数不完整")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO eating_records (date, food, money) VALUES (?, ?, ?)",
                (date, food, money)
            )
            
            # 获取插入的ID
            last_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            print(f"饮食记录已保存到数据库, ID: {last_id}")
            return True
        except Exception as e:
            print(f"保存饮食记录失败: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def get_all_eating_records(self):
        """获取所有饮食记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT date, food, money FROM eating_records ORDER BY created_at DESC")
            records = cursor.fetchall()
            
            conn.close()
            
            formatted_records = []
            for record in records:
                formatted_records.append({
                    "date": record[0],
                    "food": record[1],
                    "money": record[2]
                })
            
            print(f"获取到 {len(formatted_records)} 条饮食记录")
            return formatted_records
        except Exception as e:
            print(f"获取饮食记录失败: {str(e)}")
            print(traceback.format_exc())
            return []
    
    def get_function_call_logs(self, limit=10):
        """获取最近的函数调用日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT function_name, arguments, called_at FROM function_calls ORDER BY called_at DESC LIMIT ?", 
                (limit,)
            )
            logs = cursor.fetchall()
            
            conn.close()
            
            formatted_logs = []
            for log in logs:
                try:
                    args = json.loads(log[1])
                except:
                    args = {"error": "无法解析参数", "raw": log[1]}
                
                formatted_logs.append({
                    "function_name": log[0],
                    "arguments": args,
                    "called_at": log[2]
                })
            
            print(f"获取到 {len(formatted_logs)} 条函数调用日志")
            return formatted_logs
        except Exception as e:
            print(f"获取函数调用日志失败: {str(e)}")
            print(traceback.format_exc())
            return []
    
    def get_eating_records_by_date(self, date):
        """根据日期查询饮食记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT date, food, money FROM eating_records WHERE date = ? ORDER BY created_at", 
                (date,)
            )
            records = cursor.fetchall()
            
            conn.close()
            
            formatted_records = []
            for record in records:
                formatted_records.append({
                    "date": record[0],
                    "food": record[1],
                    "money": record[2]
                })
            
            print(f"日期 {date} 获取到 {len(formatted_records)} 条记录")
            return formatted_records
        except Exception as e:
            print(f"根据日期查询记录失败: {str(e)}")
            print(traceback.format_exc())
            return []
    
    def get_total_spending(self):
        """计算总花费"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(CAST(money AS REAL)) FROM eating_records")
            total = cursor.fetchone()[0]
            
            conn.close()
            
            result = total if total else 0
            print(f"总消费: {result}")
            return result
        except Exception as e:
            print(f"计算总花费失败: {str(e)}")
            print(traceback.format_exc())
            return 0
    
    def get_recent_eating_records(self, limit=10):
        """获取最近的饮食记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT date, food, money FROM eating_records ORDER BY created_at DESC LIMIT ?", 
                (limit,)
            )
            records = cursor.fetchall()
            
            conn.close()
            
            formatted_records = []
            for record in records:
                formatted_records.append({
                    "date": record[0],
                    "food": record[1],
                    "money": record[2]
                })
            
            print(f"获取到最近 {len(formatted_records)} 条饮食记录")
            return formatted_records
        except Exception as e:
            print(f"获取最近饮食记录失败: {str(e)}")
            print(traceback.format_exc())
            return []
    
    def get_food_frequency_analysis(self, days=7):
        """分析食物频率"""
        try:
            from datetime import datetime, timedelta
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute(
                """SELECT food, COUNT(*) as count, 
                          GROUP_CONCAT(DISTINCT date) as dates
                   FROM eating_records 
                   WHERE date >= ? 
                   GROUP BY food 
                   ORDER BY count DESC""",
                (start_date.strftime('%Y-%m-%d'),)
            )
            results = cursor.fetchall()
            
            conn.close()
            
            food_analysis = []
            for result in results:
                food_analysis.append({
                    "food": result[0],
                    "count": result[1],
                    "dates": result[2].split(',') if result[2] else []
                })
            
            print(f"分析了 {len(food_analysis)} 种食物的频率")
            return food_analysis
        except Exception as e:
            print(f"分析食物频率失败: {str(e)}")
            print(traceback.format_exc())
            return [] 