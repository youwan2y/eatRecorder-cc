"""
Food and eating record related tools
"""
from typing import Dict
from langchain_core.tools import tool
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from db_utils import DatabaseManager

# Global database manager instance
db_manager = DatabaseManager()

@tool
def record_thing(date: str, eat: str, money: str) -> Dict:
    """记录用户在某日吃了什么花了多少钱"""
    try:
        # 参数校验
        if not date or not eat or not money:
            print(f"记录数据参数不完整: date={date}, eat={eat}, money={money}")
            return {"status": "error", "message": "日期、食物和金额不能为空"}
        
        print(f"准备记录数据: date={date}, eat={eat}, money={money}")
        
        # 记录函数调用
        call_logged = db_manager.log_function_call("record_thing", {"date": date, "eat": eat, "money": money})
        if not call_logged:
            print("函数调用日志记录失败")
        
        # 保存记录到数据库
        saved = db_manager.save_eating_record(date, eat, money)
        if not saved:
            print("饮食记录保存失败")
            return {"status": "error", "message": "数据库记录保存失败"}
        
        print("数据已成功记录到数据库")
        return {"status": "success", "message": f"已记录：{date}吃了{eat}，花费{money}"}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"记录数据失败: {str(e)}")
        print(error_trace)
        return {"status": "error", "message": f"记录数据失败: {str(e)}"}

@tool
def get_all_records() -> Dict:
    """获取所有饮食记录"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_all_records", {})
        
        records = db_manager.get_all_eating_records()
        return {"status": "success", "records": records}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_records_by_date(date: str) -> Dict:
    """获取特定日期的饮食记录"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_records_by_date", {"date": date})
        
        records = db_manager.get_eating_records_by_date(date)
        return {"status": "success", "records": records}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_total_spending() -> Dict:
    """获取总消费金额"""
    try:
        # 记录函数调用
        db_manager.log_function_call("get_total_spending", {})
        
        total = db_manager.get_total_spending()
        return {"status": "success", "total": total}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_eating_stats() -> Dict:
    """获取饮食统计信息"""
    try:
        from ..function_statistics import FunctionCallStatistics
        
        # 记录函数调用
        db_manager.log_function_call("get_eating_stats", {})
        
        stats_manager = FunctionCallStatistics(db_manager)
        report = stats_manager.generate_eating_report()
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def recommend_food() -> Dict:
    """基于用户最近的饮食历史推荐食物"""
    try:
        from datetime import datetime
        
        # 记录函数调用
        db_manager.log_function_call("recommend_food", {})
        
        # 获取最近的饮食记录
        recent_records = db_manager.get_recent_eating_records(15)
        
        # 获取食物频率分析
        food_analysis = db_manager.get_food_frequency_analysis(7)
        
        # 如果没有历史记录，返回通用推荐
        if not recent_records:
            return {
                "status": "success", 
                "recommendations": [
                    "建议您可以尝试一些简单的家常菜，如：",
                    "• 番茄炒蛋",
                    "• 青椒肉丝", 
                    "• 紫菜蛋花汤",
                    "• 清炒时蔬"
                ],
                "reason": "还没有您的饮食记录，建议一些基础家常菜"
            }
        
        # 分析时间段
        current_hour = datetime.now().hour
        time_period = ""
        if 5 <= current_hour < 11:
            time_period = "早餐"
        elif 11 <= current_hour < 14:
            time_period = "午餐"
        elif 17 <= current_hour < 21:
            time_period = "晚餐"
        else:
            time_period = "加餐"
        
        # 获取最近常吃的食物
        frequent_foods = [item["food"] for item in food_analysis[:3]]
        
        # 基于时间段的推荐逻辑
        recommendations = []
        
        if time_period == "早餐":
            recommendations = [
                "• 小米粥配咸菜",
                "• 豆浆油条",
                "• 鸡蛋三明治",
                "• 燕麦片配水果",
                "• 包子豆浆"
            ]
        elif time_period == "午餐":
            recommendations = [
                "• 宫保鸡丁",
                "• 麻婆豆腐",
                "• 红烧肉",
                "• 西红柿鸡蛋面",
                "• 鱼香肉丝"
            ]
        elif time_period == "晚餐":
            recommendations = [
                "• 清蒸鱼",
                "• 蒜蓉西兰花",
                "• 冬瓜排骨汤",
                "• 凉拌黄瓜",
                "• 白切鸡"
            ]
        else:
            recommendations = [
                "• 水果拼盘",
                "• 酸奶",
                "• 坚果",
                "• 全麦面包",
                "• 绿茶"
            ]
        
        # 避免重复推荐最近常吃的食物
        filtered_recommendations = []
        for rec in recommendations:
            food_name = rec.replace("• ", "").replace("配", "").replace("和", " ").split()[0]
            if not any(frequent_food in food_name for frequent_food in frequent_foods):
                filtered_recommendations.append(rec)
        
        # 如果过滤后推荐太少，添加一些通用推荐
        if len(filtered_recommendations) < 3:
            backup_recs = [
                "• 时令蔬菜",
                "• 蛋白质丰富的食物",
                "• 清淡易消化的食物",
                "• 营养均衡的搭配"
            ]
            filtered_recommendations.extend(backup_recs[:3])
        
        # 限制推荐数量
        final_recommendations = filtered_recommendations[:5]
        
        # 生成推荐理由
        reason = f"根据您最近的饮食记录，为您推荐{time_period}食物。"
        if frequent_foods:
            reason += f"考虑到您最近常吃{', '.join(frequent_foods)}，为您推荐一些不同的选择。"
        
        return {
            "status": "success",
            "recommendations": final_recommendations,
            "time_period": time_period,
            "recent_foods": frequent_foods,
            "reason": reason
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"推荐食物失败: {str(e)}")
        print(error_trace)
        return {"status": "error", "message": f"推荐食物失败: {str(e)}"}