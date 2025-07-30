# LangChain 改写说明

## 改动概述

本项目已使用 LangChain 框架进行改写，保持了原有的所有功能并维持了原有的 prompt。

## 主要改动

### 1. 依赖更新
- 添加了 LangChain 相关依赖：
  - `langchain>=0.1.0`
  - `langchain-core>=0.1.0`
  - `langchain-community>=0.0.10`
  - `langgraph>=0.0.20`

### 2. 架构改进
- **工具定义**：使用 `@tool` 装饰器定义工具函数，替代了原来的手动工具配置
- **代理系统**：使用 LangChain 的 `AgentExecutor` 和 `create_tool_calling_agent` 创建代理
- **内存管理**：使用 `RunnableWithMessageHistory` 和 `InMemoryChatMessageHistory` 管理对话历史
- **模型适配**：创建了 `ZhipuAIChatModel` 适配器，将 ZhipuAI 集成到 LangChain 框架中

### 3. 代码简化
- 移除了复杂的手动工具调用处理逻辑
- 使用 LangChain 的标准工具调用机制
- 简化了消息格式转换逻辑

### 4. 功能保持
- 保持了所有原有的工具功能：
  - `record_thing`: 记录饮食信息
  - `read_file`: 读取文件
  - `write_file`: 写入文件
  - `list_directory`: 列出目录
  - `get_all_records`: 获取所有记录
  - `get_records_by_date`: 按日期查询记录
  - `get_total_spending`: 获取总消费
  - `get_function_stats`: 获取函数统计
  - `get_eating_stats`: 获取饮食统计
  - `generate_function_chart`: 生成函数调用图表
  - `generate_eating_charts`: 生成饮食统计图表

### 5. Prompt 维持
- 完全保持了原有的系统提示内容
- 使用 `ChatPromptTemplate` 进行提示管理

## 文件说明

### 主要文件
- `app.py`: 完整的 LangChain 版本应用
- `app_simple.py`: 简化版本，用于测试基本功能
- `requirements.txt`: 更新了依赖列表

### 原有文件保持不变
- `db_utils.py`: 数据库工具
- `file_operations.py`: 文件操作
- `function_statistics.py`: 函数统计
- `visualization.py`: 可视化功能

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行完整版本
```bash
python app.py
```

### 运行简化版本
```bash
python app_simple.py
```

## 优势

1. **代码简化**：使用 LangChain 标准模式，代码更简洁易读
2. **功能完整**：保持了所有原有功能
3. **扩展性好**：易于添加新的工具和功能
4. **维护性强**：使用标准框架，便于维护和调试
5. **兼容性好**：与 LangChain 生态系统兼容

## 注意事项

- 确保 ZhipuAI API 密钥配置正确
- 首次运行可能需要下载 LangChain 相关依赖
- 简化版本用于测试，完整版本包含所有功能 