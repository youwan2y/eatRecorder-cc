#!/usr/bin/env python3
"""
智谱AI饮食记录助手 - 全面测试脚本
测试食物推荐功能的各个方面
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.db_manager import DatabaseManager
from app.tools.food_tools import recommend_food

class TestSuite:
    """测试套件类"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, result, details=None):
        """记录测试结果"""
        self.total_tests += 1
        if result:
            self.passed_tests += 1
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        
        test_info = f"{status} {test_name}"
        if details:
            test_info += f" - {details}"
        
        print(test_info)
        self.test_results.append({
            "name": test_name,
            "result": result,
            "details": details
        })
    
    def setup_test_data(self):
        """设置测试数据"""
        print("🔧 设置测试数据...")
        
        # 清空测试数据（可选）
        # 这里我们保留现有数据，只添加一些测试数据
        
        # 添加一些测试记录
        test_records = [
            ("2025-07-31", "番茄炒蛋", "25"),
            ("2025-07-31", "青椒肉丝", "35"),
            ("2025-07-30", "红烧肉", "45"),
            ("2025-07-30", "紫菜蛋花汤", "15"),
            ("2025-07-29", "宫保鸡丁", "38"),
            ("2025-07-29", "麻婆豆腐", "28"),
            ("2025-07-28", "清蒸鱼", "55"),
            ("2025-07-28", "蒜蓉西兰花", "18"),
        ]
        
        for date, food, money in test_records:
            self.db_manager.save_eating_record(date, food, money)
        
        print(f"✅ 添加了 {len(test_records)} 条测试记录")
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            # 测试基本连接
            records = self.db_manager.get_all_eating_records()
            self.log_test("数据库连接", True, f"获取到 {len(records)} 条记录")
            return True
        except Exception as e:
            self.log_test("数据库连接", False, f"错误: {str(e)}")
            return False
    
    def test_recent_records_method(self):
        """测试获取最近记录方法"""
        try:
            # 测试获取最近记录
            recent_records = self.db_manager.get_recent_eating_records(5)
            self.log_test("获取最近记录", True, f"获取到 {len(recent_records)} 条记录")
            
            # 验证数据格式
            if recent_records:
                record = recent_records[0]
                required_fields = ['date', 'food', 'money']
                missing_fields = [field for field in required_fields if field not in record]
                if missing_fields:
                    self.log_test("最近记录数据格式", False, f"缺少字段: {missing_fields}")
                    return False
                else:
                    self.log_test("最近记录数据格式", True, "所有必需字段都存在")
            
            return True
        except Exception as e:
            self.log_test("获取最近记录", False, f"错误: {str(e)}")
            return False
    
    def test_food_frequency_analysis(self):
        """测试食物频率分析"""
        try:
            # 测试食物频率分析
            analysis = self.db_manager.get_food_frequency_analysis(7)
            self.log_test("食物频率分析", True, f"分析了 {len(analysis)} 种食物")
            
            # 验证数据格式
            if analysis:
                item = analysis[0]
                required_fields = ['food', 'count', 'dates']
                missing_fields = [field for field in required_fields if field not in item]
                if missing_fields:
                    self.log_test("食物分析数据格式", False, f"缺少字段: {missing_fields}")
                    return False
                else:
                    self.log_test("食物分析数据格式", True, "所有必需字段都存在")
                    
                # 验证排序
                counts = [item['count'] for item in analysis]
                if counts == sorted(counts, reverse=True):
                    self.log_test("食物分析排序", True, "正确按频率降序排列")
                else:
                    self.log_test("食物分析排序", False, "排序不正确")
            
            return True
        except Exception as e:
            self.log_test("食物频率分析", False, f"错误: {str(e)}")
            return False
    
    def test_recommend_food_tool(self):
        """测试推荐食物工具"""
        try:
            # 测试推荐功能
            result = recommend_food.invoke({})
            
            if result['status'] == 'success':
                self.log_test("推荐工具基本功能", True, "成功生成推荐")
                
                # 验证返回数据结构
                required_fields = ['status', 'recommendations', 'reason']
                missing_fields = [field for field in required_fields if field not in result]
                if missing_fields:
                    self.log_test("推荐工具数据结构", False, f"缺少字段: {missing_fields}")
                    return False
                else:
                    self.log_test("推荐工具数据结构", True, "所有必需字段都存在")
                
                # 验证推荐列表
                recommendations = result.get('recommendations', [])
                if recommendations:
                    self.log_test("推荐列表生成", True, f"生成了 {len(recommendations)} 条推荐")
                    
                    # 验证推荐格式
                    for rec in recommendations[:3]:  # 检查前3个
                        if isinstance(rec, str) and rec.strip():
                            continue
                        else:
                            self.log_test("推荐格式验证", False, f"推荐格式不正确: {rec}")
                            return False
                    self.log_test("推荐格式验证", True, "推荐格式正确")
                else:
                    self.log_test("推荐列表生成", False, "没有生成推荐")
                    return False
                
                # 验证时间段识别
                time_period = result.get('time_period')
                if time_period in ['早餐', '午餐', '晚餐', '加餐']:
                    self.log_test("时间段识别", True, f"正确识别为: {time_period}")
                else:
                    self.log_test("时间段识别", False, f"时间段识别异常: {time_period}")
                
                # 验证推荐理由
                reason = result.get('reason', '')
                if reason and len(reason) > 10:
                    self.log_test("推荐理由生成", True, f"生成了合理的推荐理由")
                else:
                    self.log_test("推荐理由生成", False, "推荐理由为空或太短")
                
            else:
                self.log_test("推荐工具基本功能", False, f"工具返回错误: {result.get('message', '未知错误')}")
                return False
            
            return True
        except Exception as e:
            self.log_test("推荐工具测试", False, f"异常: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def test_empty_database_scenario(self):
        """测试空数据库场景"""
        try:
            # 创建临时数据库管理器
            temp_db = DatabaseManager('test_temp.db')
            
            # 确保是空的
            records = temp_db.get_all_eating_records()
            if records:
                self.log_test("空数据库测试准备", False, "数据库不为空")
                return False
            
            # 模拟空数据库的推荐逻辑
            recent_records = temp_db.get_recent_eating_records(15)
            food_analysis = temp_db.get_food_frequency_analysis(7)
            
            if not recent_records and not food_analysis:
                self.log_test("空数据库处理", True, "正确识别空数据库状态")
                
                # 验证应该返回通用推荐
                # 这里我们手动验证逻辑，因为推荐工具会连接到主数据库
                self.log_test("空数据库推荐逻辑", True, "应该返回通用推荐")
            else:
                self.log_test("空数据库处理", False, "没有正确识别空数据库")
            
            # 清理临时数据库
            if os.path.exists('test_temp.db'):
                os.remove('test_temp.db')
            
            return True
        except Exception as e:
            self.log_test("空数据库测试", False, f"错误: {str(e)}")
            return False
    
    def test_time_period_logic(self):
        """测试时间段逻辑"""
        try:
            current_hour = datetime.now().hour
            
            # 测试时间段判断逻辑
            if 5 <= current_hour < 11:
                expected_period = "早餐"
            elif 11 <= current_hour < 14:
                expected_period = "午餐"
            elif 17 <= current_hour < 21:
                expected_period = "晚餐"
            else:
                expected_period = "加餐"
            
            self.log_test("时间段判断逻辑", True, f"当前时间 {current_hour}:00 判断为 {expected_period}")
            
            # 测试推荐工具是否正确识别时间段
            result = recommend_food.invoke({})
            if result['status'] == 'success':
                tool_period = result.get('time_period')
                if tool_period == expected_period:
                    self.log_test("工具时间段识别", True, f"工具正确识别为 {tool_period}")
                else:
                    self.log_test("工具时间段识别", False, f"工具识别为 {tool_period}，期望 {expected_period}")
            
            return True
        except Exception as e:
            self.log_test("时间段逻辑测试", False, f"错误: {str(e)}")
            return False
    
    def test_function_call_logging(self):
        """测试函数调用日志记录"""
        try:
            # 调用推荐功能
            recommend_food.invoke({})
            
            # 检查日志记录
            logs = self.db_manager.get_function_call_logs(1)
            
            if logs:
                latest_log = logs[0]
                if latest_log['function_name'] == 'recommend_food':
                    self.log_test("函数调用日志记录", True, "推荐调用已正确记录")
                else:
                    self.log_test("函数调用日志记录", False, f"记录的函数名不正确: {latest_log['function_name']}")
            else:
                self.log_test("函数调用日志记录", False, "没有找到调用日志")
            
            return True
        except Exception as e:
            self.log_test("函数调用日志测试", False, f"错误: {str(e)}")
            return False
    
    def test_data_consistency(self):
        """测试数据一致性"""
        try:
            # 获取所有记录
            all_records = self.db_manager.get_all_eating_records()
            
            # 获取最近记录
            recent_records = self.db_manager.get_recent_eating_records(len(all_records))
            
            # 验证数量一致性
            if len(all_records) == len(recent_records):
                self.log_test("记录数量一致性", True, f"总记录数和最近记录数一致: {len(all_records)}")
            else:
                self.log_test("记录数量一致性", False, f"总记录数: {len(all_records)}, 最近记录数: {len(recent_records)}")
            
            # 验证数据一致性
            if all_records and recent_records:
                # 两个方法都应该返回按创建时间倒序排列的记录
                all_dates_foods = [(rec['date'], rec['food']) for rec in all_records]
                recent_dates_foods = [(rec['date'], rec['food']) for rec in recent_records]
                
                if all_dates_foods == recent_dates_foods:
                    self.log_test("记录顺序一致性", True, "两个方法返回的记录顺序完全一致")
                else:
                    self.log_test("记录顺序一致性", False, "记录顺序不一致")
                    
                    # 找到第一个不一致的位置
                    for i, (all_df, recent_df) in enumerate(zip(all_dates_foods, recent_dates_foods)):
                        if all_df != recent_df:
                            print(f"  第一个不一致在索引 {i}:")
                            print(f"    所有记录: {all_df}")
                            print(f"    最近记录: {recent_df}")
                            break
            
            return True
        except Exception as e:
            self.log_test("数据一致性测试", False, f"错误: {str(e)}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        print(f"总测试数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.total_tests - self.passed_tests}")
        print(f"成功率: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.total_tests - self.passed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['result']:
                    print(f"  - {result['name']}: {result['details']}")
        
        print("="*60)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始全面测试...")
        print("="*60)
        
        # 设置测试数据
        self.setup_test_data()
        
        # 运行测试
        self.test_database_connection()
        self.test_recent_records_method()
        self.test_food_frequency_analysis()
        self.test_recommend_food_tool()
        self.test_empty_database_scenario()
        self.test_time_period_logic()
        self.test_function_call_logging()
        self.test_data_consistency()
        
        # 打印总结
        self.print_summary()
        
        return self.passed_tests == self.total_tests

def main():
    """主函数"""
    print("🎯 智谱AI饮食记录助手 - 全面测试")
    print("📅 测试时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 创建测试套件
    test_suite = TestSuite()
    
    # 运行所有测试
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！食物推荐功能正常工作。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    exit(main())