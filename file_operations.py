import os
import json
from db_utils import DatabaseManager

class FileManager:
    def __init__(self, db_manager=None):
        """初始化文件管理器"""
        self.db_manager = db_manager or DatabaseManager()
    
    def read_file(self, file_path):
        """读取文件内容"""
        try:
            # 记录函数调用
            self.db_manager.log_function_call("read_file", {"file_path": file_path})
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"文件不存在: {file_path}"}
            
            # 检查文件类型
            if not os.path.isfile(file_path):
                return {"status": "error", "message": f"路径不是文件: {file_path}"}
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return {"status": "success", "content": content}
        except UnicodeDecodeError:
            try:
                # 尝试使用不同的编码
                with open(file_path, 'r', encoding='gbk') as file:
                    content = file.read()
                return {"status": "success", "content": content}
            except Exception as e:
                return {"status": "error", "message": f"读取文件失败(编码问题): {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"读取文件失败: {str(e)}"}
    
    def write_file(self, file_path, content):
        """写入文件内容"""
        try:
            # 记录函数调用
            self.db_manager.log_function_call("write_file", {"file_path": file_path})
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            return {"status": "success", "message": f"文件已成功写入: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": f"写入文件失败: {str(e)}"}
    
    def append_to_file(self, file_path, content):
        """追加内容到文件"""
        try:
            # 记录函数调用
            self.db_manager.log_function_call("append_to_file", {"file_path": file_path})
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 追加内容到文件
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(content)
            
            return {"status": "success", "message": f"内容已成功追加到文件: {file_path}"}
        except Exception as e:
            return {"status": "error", "message": f"追加到文件失败: {str(e)}"}
    
    def list_directory(self, directory_path='.'):
        """列出目录内容"""
        try:
            # 记录函数调用
            self.db_manager.log_function_call("list_directory", {"directory_path": directory_path})
            
            # 检查目录是否存在
            if not os.path.exists(directory_path):
                return {"status": "error", "message": f"目录不存在: {directory_path}"}
            
            # 检查路径是否为目录
            if not os.path.isdir(directory_path):
                return {"status": "error", "message": f"路径不是目录: {directory_path}"}
            
            # 列出目录内容
            files = []
            directories = []
            
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    directories.append(item)
            
            return {
                "status": "success", 
                "files": files, 
                "directories": directories
            }
        except Exception as e:
            return {"status": "error", "message": f"列出目录失败: {str(e)}"}
    
    def file_exists(self, file_path):
        """检查文件是否存在"""
        try:
            # 记录函数调用
            self.db_manager.log_function_call("file_exists", {"file_path": file_path})
            
            exists = os.path.exists(file_path) and os.path.isfile(file_path)
            return {"status": "success", "exists": exists}
        except Exception as e:
            return {"status": "error", "message": f"检查文件失败: {str(e)}"} 