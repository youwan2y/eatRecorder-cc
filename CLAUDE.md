# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese AI chat assistant that helps users record their eating and spending habits. The application uses intent detection to route between two different agents: a chat agent for general conversation and a record agent for handling food/expense data entry.

## Architecture

### Core Components

1. **Dual-Agent System**: The application uses two separate LangChain agents:
   - **Chat Agent**: Handles general conversation and emotional support
   - **Record Agent**: Manages food/expense recording and data queries

2. **Intent Detection**: Uses LLM to classify user input as either "chat" or "record" intent before routing to appropriate agent

3. **Database Layer**: SQLite database with two main tables:
   - `eating_records`: Stores food, date, and spending information
   - `function_calls`: Logs all function calls for analytics

4. **LangChain Integration**: Built on LangChain framework with custom ZhipuAI adapter

### Key Files

- `app.py`: Main application with dual-agent system and intent detection
- `db_utils.py`: Database management and operations
- `file_operations.py`: File system operations (read, write, list directories)
- `function_statistics.py`: Analytics and reporting functions
- `visualization.py`: Chart generation for statistics

## Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python app.py
```

### Dependencies
- `zhipuai>=1.0.7`: ZhipuAI API client (now using zai-sdk)
- `langchain>=0.1.0`: LangChain framework
- `matplotlib>=3.5.0`: Chart generation
- `zai-sdk`: Custom ZhipuAI client

## Key Features

### Intent Detection
The system uses LLM-based intent detection to determine if user input is about food/expense recording or general conversation. This prevents the chat agent from accidentally triggering recording functions.

### Tool Functions
The record agent has access to 11 tools:
- `record_thing`: Record food/expense data
- `read_file`, `write_file`, `list_directory`: File operations
- `get_all_records`, `get_records_by_date`: Data retrieval
- `get_total_spending`, `get_function_stats`, `get_eating_stats`: Analytics
- `generate_function_chart`, `generate_eating_charts`: Visualization

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
The project includes a custom `ZhipuAIChatModel` class that adapts ZhipuAI's API to work with LangChain's interface. This handles message format conversion and tool calling.

### Error Handling
All functions include comprehensive error handling with try-catch blocks and detailed logging. Database operations are wrapped in error handling to prevent crashes.

### Function Call Logging
Every tool function call is automatically logged to the `function_calls` table for analytics and debugging purposes.

### Memory Management
Uses LangChain's `InMemoryChatMessageHistory` for conversation context within each session.

## Configuration

### API Key
The ZhipuAI API key is hardcoded in `app.py` at line 22. For production use, this should be moved to environment variables.

### Database Path
Database file is created as `agent_records.db` in the project root directory.

## Development Notes

### Adding New Tools
1. Define new tool functions with `@tool` decorator
2. Add to `all_tools` list in `app.py`
3. Update the record agent's system prompt if needed
4. Consider adding to function call logging

### Database Schema Changes
- Modify `init_db()` method in `DatabaseManager` class
- Update related query methods
- Consider migration strategies for existing data

### Testing Changes
The application is designed for interactive testing. Run `python app.py` and test different scenarios:
- General conversation should route to chat agent
- Food/expense related queries should route to record agent
- Test all tool functions for proper operation