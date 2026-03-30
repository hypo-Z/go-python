"""
自定义模块示例 - 数据验证和配置管理
"""

import json
import os
from datetime import datetime

class DataValidator:
    """数据验证器"""
    
    def validate_email(self, email):
        """验证邮箱格式"""
        if not email:
            return False
        
        # 简单的邮箱验证
        if "@" not in email:
            return False
        
        parts = email.split("@")
        if len(parts) != 2:
            return False
        
        local_part, domain = parts
        if not local_part or not domain:
            return False
        
        if "." not in domain:
            return False
        
        return True
    
    def validate_phone(self, phone):
        """验证手机号格式"""
        if not phone:
            return False
        
        # 移除分隔符
        cleaned = phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # 检查是否为数字
        if not cleaned.isdigit():
            return False
        
        # 检查长度（支持国际号码）
        if len(cleaned) < 10 or len(cleaned) > 15:
            return False
        
        return True
    
    def validate_date(self, date_str, format="%Y-%m-%d"):
        """验证日期格式"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    def validate_json(self, json_str):
        """验证 JSON 格式"""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.config = {
            "version": "1.0.0",
            "environment": "production",
            "debug": False,
            "max_retries": 3,
            "timeout": 30,
            "log_level": "INFO"
        }
        
        # 从文件加载配置（如果存在）
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file):
        """从文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
    
    def save_to_file(self, config_file=None):
        """保存配置到文件"""
        file_path = config_file or self.config_file
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

# 工具函数
def format_timestamp(timestamp=None):
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def generate_id(prefix="", length=8):
    """生成唯一ID"""
    import random
    import string
    
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}{random_part}" if prefix else random_part

# 模块初始化时的操作
print(f"✅ mylib 模块已加载 - 版本 {ConfigManager().get('version')}")

# 导出公共接口
__all__ = ['DataValidator', 'ConfigManager', 'format_timestamp', 'generate_id']