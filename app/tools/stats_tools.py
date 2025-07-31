"""
Statistics and visualization tools
"""
from typing import Dict
from langchain_core.tools import tool
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.database.db_manager import DatabaseManager

# Global database manager instance
db_manager = DatabaseManager()

@tool
def get_function_stats() -> Dict:
    """获取函数调用统计信息"""
    try:
        from ..function_statistics import FunctionCallStatistics
        
        # 记录函数调用
        db_manager.log_function_call("get_function_stats", {})
        
        stats_manager = FunctionCallStatistics(db_manager)
        report = stats_manager.generate_function_call_report()
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def generate_function_chart() -> Dict:
    """生成函数调用可视化图表"""
    try:
        from ..visualization import DataVisualizer
        from ..function_statistics import FunctionCallStatistics
        
        stats_manager = FunctionCallStatistics(db_manager)
        visualizer = DataVisualizer(stats_manager, db_manager)
        
        result = visualizer.generate_function_call_chart()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def generate_eating_charts() -> Dict:
    """生成饮食统计可视化图表"""
    try:
        from ..visualization import DataVisualizer
        from ..function_statistics import FunctionCallStatistics
        
        stats_manager = FunctionCallStatistics(db_manager)
        visualizer = DataVisualizer(stats_manager, db_manager)
        
        result = visualizer.generate_eating_charts()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}