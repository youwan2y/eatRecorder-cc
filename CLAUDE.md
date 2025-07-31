# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese AI chat assistant that helps users record their eating and spending habits. The application uses an intelligent unified agent system that can handle both conversation and food recording, plus smart food recommendations based on user's eating history.

## Architecture

### Core Components

1. **Smart Unified Agent System**: The application uses an intelligent single agent that can:
   - Handle natural conversation and emotional support
   - Manage food/expense recording and data queries
   - Provide smart food recommendations based on eating history

2. **Intelligent Intent Detection**: Uses LLM to understand user context and naturally handle:
   - Food recording scenarios
   - Food recommendation requests
   - General conversation
   - Data analysis queries

3. **Database Layer**: SQLite database with two main tables:
   - `eating_records`: Stores food, date, and spending information
   - `function_calls`: Logs all function calls for analytics

4. **Food Recommendation Engine**: Analyzes user's eating history to provide:
   - Personalized food recommendations
   - Time-aware suggestions (breakfast/lunch/dinner/snacks)
   - Variety optimization to avoid repetition

5. **LangChain Integration**: Built on LangChain framework with custom ZhipuAI adapter

### Key Files

- `main.py`: Main application with smart unified agent system
- `run.py`: Startup script with environment setup
- `app/`: Modular application structure
  - `core/`: Core configuration and models
  - `agents/`: Agent implementations (smart_agent.py, base_agent.py)
  - `tools/`: Tool functions (food_tools.py, file_tools.py, stats_tools.py)
  - `utils/`: Utility classes (session_manager.py)
- `db_utils.py`: Database management and operations with recommendation methods
- `test_recommendation.py`: Comprehensive test suite
- `demo_recommendation.py`: Feature demonstration script

## Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application (recommended)
python run.py

# Or run directly
python main.py

# Run comprehensive tests
python test_recommendation.py

# Run feature demonstration
python demo_recommendation.py
```

### Dependencies
- `zhipuai>=1.0.7`: ZhipuAI API client (now using zai-sdk)
- `langchain>=0.1.0`: LangChain framework
- `matplotlib>=3.5.0`: Chart generation
- `zai-sdk`: Custom ZhipuAI client

## Key Features

### Smart Intent Detection
The system uses LLM-based intent detection to naturally understand user context and handle:
- Food recording scenarios
- Food recommendation requests ("不知道吃什么", "今天吃啥好")
- General conversation
- Data analysis queries

### Food Recommendation System
- **Personalized Recommendations**: Based on user's eating history (7-10 days)
- **Time-Aware Suggestions**: Different recommendations for breakfast/lunch/dinner/snacks
- **Variety Optimization**: Avoids repetitive suggestions based on frequency analysis
- **Empty Database Handling**: Provides generic suggestions for new users

### Tool Functions
The smart agent has access to 12 tools:
- `record_thing`: Record food/expense data
- `recommend_food`: Smart food recommendations based on eating history
- `read_file`, `write_file`, `list_directory`: File operations
- `get_all_records`, `get_records_by_date`: Data retrieval
- `get_total_spending`, `get_function_stats`, `get_eating_stats`: Analytics
- `generate_function_chart`, `generate_eating_charts`: Visualization

### Recommendation Algorithm
1. Analyze recent eating records frequency
2. Identify user's food preferences and patterns
3. Match recommendations to current time period
4. Filter out frequently eaten foods for variety
5. Generate personalized recommendation reasons

### Database Schema
```sql
-- Eating records table
CREATE TABLE eating_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    food TEXT,
    money TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function call logs
CREATE TABLE function_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT,
    arguments TEXT,
    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Important Implementation Details

### Custom ZhipuAI Adapter
The project includes a custom `ZhipuAIChatModel` class that adapts ZhipuAI's API to work with LangChain's interface. This handles message format conversion and tool calling with special handling for the `record_thing` tool schema.

### Smart Agent System
The `SmartAgent` class uses a unified approach with:
- Natural conversation flow without explicit mode switching
- Context-aware tool selection based on user intent
- System prompt that handles multiple scenarios seamlessly

### Database Enhancements
Enhanced `DatabaseManager` class with new methods:
- `get_recent_eating_records(limit)`: Retrieves most recent eating records
- `get_food_frequency_analysis(days)`: Analyzes food frequency patterns
- Fixed sorting consistency across all retrieval methods

### Error Handling
All functions include comprehensive error handling with try-catch blocks and detailed logging. Database operations are wrapped in error handling to prevent crashes. The recommendation system gracefully handles empty databases.

### Function Call Logging
Every tool function call is automatically logged to the `function_calls` table for analytics and debugging purposes. This includes recommendation requests for usage analysis.

### Memory Management
Uses LangChain's `InMemoryChatMessageHistory` for conversation context within each session. The `SessionManager` handles multiple concurrent sessions with timeout cleanup.

## Configuration

### API Key
The ZhipuAI API key is configured in `run.py` with environment variable fallback. The system uses `zai-sdk` for ZhipuAI API integration.

### Environment Variables
```bash
ZHIPUAI_API_KEY=your_api_key_here
MODEL_NAME=glm-4.5-flash
MAX_SESSIONS=100
SESSION_TIMEOUT=3600
```

### Database Path
Database file is created as `agent_records.db` in the project root directory.

### Recommendation Settings
- History analysis period: 7 days (configurable)
- Recent records limit: 15 records
- Maximum recommendations: 5 items
- Time periods: 早餐 (5-11), 午餐 (11-14), 晚餐 (17-21), 加餐 (other)

## Development Notes

### Adding New Tools
1. Define new tool functions with `@tool` decorator in appropriate tool module
2. Add tool import to `main.py`
3. Register tool in `_setup_tools()` method
4. Update the smart agent's system prompt if needed
5. All tool calls are automatically logged

### Database Schema Changes
- Modify `init_db()` method in `DatabaseManager` class
- Update related query methods
- Consider migration strategies for existing data
- Ensure consistency with `get_all_eating_records()` sorting

### Recommendation System Extensions
- Add new time periods in `recommend_food()` tool
- Extend recommendation categories in tool logic
- Update food frequency analysis period as needed
- Add new recommendation filters or criteria

### Testing and Quality Assurance
- Run comprehensive tests: `python test_recommendation.py`
- Test feature demonstration: `python demo_recommendation.py`
- Verify all tool functions work properly
- Test edge cases (empty database, error handling)
- Ensure database sorting consistency across methods

### Interactive Testing
Run `python run.py` and test different scenarios:
- General conversation should flow naturally
- Food recording: "今天吃了牛肉面，花了35元"
- Food recommendations: "不知道吃什么", "今天吃啥好"
- Data queries: "查看我的所有记录"
- Test all tool functions for proper operation

## Version Information

### Current Version: 1.1.0
- **Architecture**: Smart unified agent system
- **Tools**: 12 tools including food recommendation
- **Database**: Enhanced with recommendation support methods
- **Testing**: 100% test coverage with comprehensive test suite
- **Language**: Chinese interface with intelligent intent recognition

### Key Changes from v1.0.0
- Migrated from dual-agent to smart unified agent system
- Added intelligent food recommendation system
- Enhanced database with frequency analysis methods
- Improved error handling and edge case management
- Added comprehensive testing and demonstration scripts