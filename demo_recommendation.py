#!/usr/bin/env python3
"""
智谱AI饮食记录助手 - 推荐功能演示
展示食物推荐功能的各个方面
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.db_manager import DatabaseManager
from app.tools.food_tools import recommend_food

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🍽️  {title}")
    print(f"{'='*60}")

def print_section(title):
    """打印小节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_basic_recommendation():
    """演示基本推荐功能"""
    print_header("基本推荐功能演示")
    
    # 获取推荐
    result = recommend_food.invoke({})
    
    if result['status'] == 'success':
        print(f"🕐 当前时间段: {result['time_period']}")
        print(f"💡 推荐理由: {result['reason']}")
        print(f"\n🍽️  推荐食物:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        if 'recent_foods' in result and result['recent_foods']:
            print(f"\n📊 您最近常吃的食物: {', '.join(result['recent_foods'][:3])}")
    else:
        print(f"❌ 推荐失败: {result.get('message', '未知错误')}")

def demo_database_analysis():
    """演示数据库分析功能"""
    print_header("数据库分析功能演示")
    
    db = DatabaseManager()
    
    # 显示最近记录
    print_section("最近饮食记录")
    recent_records = db.get_recent_eating_records(5)
    for i, record in enumerate(recent_records, 1):
        print(f"   {i}. {record['date']} - {record['food']} (¥{record['money']})")
    
    # 显示食物频率分析
    print_section("食物频率分析 (最近7天)")
    analysis = db.get_food_frequency_analysis(7)
    for i, item in enumerate(analysis[:5], 1):
        print(f"   {i}. {item['food']} - {item['count']}次")
        if item['dates']:
            print(f"      日期: {', '.join(item['dates'][:3])}")

def demo_time_periods():
    """演示不同时间段的推荐"""
    print_header("不同时间段推荐演示")
    
    # 模拟不同时间段的推荐
    time_scenarios = [
        ("早餐 (08:00)", "早餐"),
        ("午餐 (12:00)", "午餐"), 
        ("晚餐 (18:00)", "晚餐"),
        ("加餐 (15:00)", "加餐")
    ]
    
    db = DatabaseManager()
    recent_records = db.get_recent_eating_records(15)
    food_analysis = db.get_food_frequency_analysis(7)
    frequent_foods = [item["food"] for item in food_analysis[:3]]
    
    for scenario_name, time_period in time_scenarios:
        print(f"\n🕐 {scenario_name}")
        print("-" * 30)
        
        # 基于时间段的推荐逻辑
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
        
        # 避免重复推荐
        filtered_recs = []
        for rec in recommendations:
            food_name = rec.replace("• ", "").replace("配", "").replace("和", " ").split()[0]
            if not any(frequent_food in food_name for frequent_food in frequent_foods):
                filtered_recs.append(rec)
        
        # 显示推荐
        for rec in filtered_recs[:3]:
            print(f"   {rec}")
        
        if frequent_foods:
            print(f"   💡 避免重复推荐: {', '.join(frequent_foods)}")

def demo_empty_database():
    """演示空数据库场景"""
    print_header("空数据库场景演示")
    
    # 创建临时数据库
    temp_db = DatabaseManager('demo_empty.db')
    
    # 检查是否为空
    records = temp_db.get_all_eating_records()
    print(f"📊 数据库记录数: {len(records)}")
    
    if len(records) == 0:
        print("✅ 这是空数据库场景")
        print("\n🍽️  通用推荐:")
        generic_recommendations = [
            "建议您可以尝试一些简单的家常菜，如：",
            "• 番茄炒蛋",
            "• 青椒肉丝", 
            "• 紫菜蛋花汤",
            "• 清炒时蔬"
        ]
        for rec in generic_recommendations:
            print(f"   {rec}")
    
    # 清理临时数据库
    if os.path.exists('demo_empty.db'):
        os.remove('demo_empty.db')

def demo_statistics():
    """演示统计信息"""
    print_header("系统统计信息")
    
    db = DatabaseManager()
    
    # 基本统计
    all_records = db.get_all_eating_records()
    total_spending = db.get_total_spending()
    
    print(f"📊 总记录数: {len(all_records)}")
    print(f"💰 总消费: ¥{total_spending}")
    
    # 最近7天统计
    week_analysis = db.get_food_frequency_analysis(7)
    print(f"🍽️  最近7天吃了 {len(week_analysis)} 种不同的食物")
    
    if week_analysis:
        most_popular = week_analysis[0]
        print(f"🏆 最受欢迎: {most_popular['food']} (吃了{most_popular['count']}次)")
    
    # 函数调用统计
    print_section("函数调用统计")
    call_logs = db.get_function_call_logs(5)
    for log in call_logs:
        func_name = log['function_name']
        called_at = log['called_at']
        print(f"   • {func_name} - {called_at}")

def main():
    """主演示函数"""
    print("🎯 智谱AI饮食记录助手 - 推荐功能演示")
    print("📅 演示时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 运行各个演示
    demo_basic_recommendation()
    demo_database_analysis()
    demo_time_periods()
    demo_empty_database()
    demo_statistics()
    
    print_header("演示完成")
    print("✅ 食物推荐功能演示完成！")
    print("\n💡 使用提示:")
    print("   • 询问'不知道吃什么'获取推荐")
    print("   • 询问'今天吃啥好'获取建议")
    print("   • 询问'有什么推荐吗'获取灵感")
    print("   • 系统会根据您的饮食历史提供个性化推荐")

if __name__ == "__main__":
    main()