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