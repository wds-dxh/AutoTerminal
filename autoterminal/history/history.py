import os
import json
from typing import List, Dict, Any
from datetime import datetime

class HistoryManager:
    """历史命令管理器，用于记录和检索命令历史"""
    
    def __init__(self, history_file: str = None, max_history: int = 10):
        if history_file is None:
            # 将历史文件存储在用户主目录下的.autoterminal目录中
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".autoterminal")
            self.history_file = os.path.join(config_dir, "history.json")
        else:
            self.history_file = history_file
            
        self.max_history = max_history
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        """从历史文件加载命令历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 无法读取历史文件 {self.history_file}: {e}")
        return []
    
    def save_history(self) -> bool:
        """保存命令历史到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file) if os.path.dirname(self.history_file) else '.', exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"错误: 无法保存历史文件 {self.history_file}: {e}")
            return False
    
    def add_command(self, user_input: str, generated_command: str, executed: bool = True) -> None:
        """添加命令到历史记录"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "generated_command": generated_command,
            "executed": executed
        }
        
        self.history.append(entry)
        
        # 保持历史记录在最大数量限制内
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # 保存到文件
        self.save_history()
    
    def get_last_executed_command(self) -> str:
        """获取最后一条已执行的命令"""
        for entry in reversed(self.history):
            if entry.get("executed", False):
                return entry.get("generated_command", "")
        return ""
    
    def get_recent_history(self, count: int = None) -> List[Dict[str, Any]]:
        """获取最近的命令历史"""
        if count is None:
            count = self.max_history
        
        return self.history[-count:] if self.history else []
    
    def get_last_command(self) -> Dict[str, Any]:
        """获取最后一条命令"""
        if self.history:
            return self.history[-1]
        return {}