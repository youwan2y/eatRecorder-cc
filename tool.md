tools = [
    {
        "type": "function",
        "function": {
            "name": "record_thing",
            "description": "记录用户在某日吃了什么花了多少钱",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "吃的日期",
                    },
                    "eat": {
                        "type": "string",
                        "description": "吃了什么的名字",
                    },
                    "money": {
                        "type": "string",
                        "description": "要查询的火车日期",
                    },
                },
                "required": ["date", "eat", "money"],
            },
        }
    }
]